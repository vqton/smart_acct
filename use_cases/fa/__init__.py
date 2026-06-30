from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from domain.fa import AdjustmentType as FAAdjustmentType
from domain import (
    AssetType, DepreciationMethod, AssetStatus, DisposalType,
    BiologicalType, GrowthStage, AssetClassification, FundSource, UseType,
    FACategory, FixedAsset, DepreciationRecord, FAAdjustment, FADisposal,
    FAInventory, FAInventoryLine, FATransfer, FASparePart, FAComponent,
    BiologicalAsset, BiologicalProvision, InventoryStatus, ProvisionType,
    Result, ValidationError, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.fa_repository import FARepository
from infrastructure.models.gl_models import AccountingPeriodModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class FAUseCases:
    def __init__(self, session: Session):
        self.repo = FARepository(session)
        self._session = session

    # ── Helpers ─────────────────────────────────────────────────────────

    def _validate_period_open(self, period: str) -> None:
        p = self._session.get(AccountingPeriodModel, period)
        if p and p.is_closed:
            raise ValidationError(ErrorCodes.FA_PERIOD_CLOSED, period=period)

    def _period_to_date(self, period: str) -> date:
        parts = period.split("-")
        y, m = int(parts[0]), int(parts[1])
        if m == 12:
            return date(y, 12, 31)
        import calendar
        return date(y, m, calendar.monthrange(y, m)[1])

    def _calc_monthly_straight_line(
        self, cost: Decimal, residual: Decimal, life_months: int
    ) -> Decimal:
        if life_months <= 0:
            return Decimal("0")
        return _vnd((cost - residual) / Decimal(life_months))

    def _calc_monthly_declining_balance(
        self, nbv: Decimal, life_months: int
    ) -> Decimal:
        life_years = Decimal(life_months) / Decimal(12)
        if life_years <= 0:
            return Decimal("0")
        rate = Decimal("2") / life_years
        return _vnd(nbv * rate / Decimal("12"))

    def _get_asset_or_fail(self, asset_id: int) -> FixedAsset:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            raise ValidationError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id)
        return asset

    # ── UC-FA-01: Category Management ───────────────────────────────────

    def create_category(self, data: dict) -> Result:
        try:
            category = FACategory(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_category(category)

    def get_category(self, category_id: int) -> Result:
        cat = self.repo.get_category(category_id)
        if not cat:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_NOT_FOUND, category_id=category_id))
        return Result.success(cat)

    def list_categories(self, asset_type: Optional[str] = None) -> Result:
        cats = self.repo.list_categories(asset_type=asset_type)
        return Result.success(cats)

    def update_category(self, category_id: int, **updates) -> Result:
        return self.repo.update_category(category_id, **updates)

    def delete_category(self, category_id: int) -> Result:
        cat = self.repo.get_category(category_id)
        if not cat:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_NOT_FOUND, category_id=category_id))
        if self.repo.category_has_assets(category_id):
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_HAS_ASSETS, category_id=category_id))
        return self.repo.delete_category(category_id)

    # ── UC-FA-02: Fixed Asset Registration ──────────────────────────────

    def register_asset(self, data: dict) -> Result:
        try:
            asset = FixedAsset(**data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

        cat = self.repo.get_category(asset.category_id)
        if not cat:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_NOT_FOUND, category_id=asset.category_id))

        if cat.default_useful_life_min and cat.default_useful_life_max:
            if asset.useful_life_months < cat.default_useful_life_min or asset.useful_life_months > cat.default_useful_life_max:
                return Result.failure(AccountError(
                    ErrorCodes.FA_USEFUL_LIFE_RANGE_INVALID,
                    asset_id=asset.code,
                    min=cat.default_useful_life_min,
                    max=cat.default_useful_life_max,
                ))

        if asset.depreciation_method != cat.default_depreciation_method and not data.get("override_method"):
            return Result.failure(AccountError(
                ErrorCodes.FA_DEPRECIATION_METHOD_MISMATCH,
                asset_id=asset.code,
                expected=cat.default_depreciation_method.value,
            ))

        return self.repo.create_asset(asset)

    def get_asset(self, asset_id: int) -> Result:
        try:
            asset = self._get_asset_or_fail(asset_id)
        except ValidationError as e:
            return Result.failure(e)
        return Result.success(asset)

    def update_asset(self, asset_id: int, **updates) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))

        depr_records = self.repo.get_depreciation_records(asset_id)
        if depr_records:
            if "original_cost" in updates or "residual_value" in updates:
                return Result.failure(AccountError(ErrorCodes.CANNOT_UPDATE_POSTED, subject="asset cost after first depreciation"))

        result = self.repo.update_asset(asset_id, **updates)
        if result.is_success() and "status" in updates:
            new_status = updates["status"]
            if isinstance(new_status, AssetStatus):
                self.repo.update_asset_status(asset_id, new_status)
        return result

    def list_assets(
        self,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        asset_type: Optional[str] = None,
    ) -> Result:
        assets = self.repo.list_assets(
            category_id=category_id,
            status=status,
            department_id=department_id,
            asset_type=asset_type,
        )
        return Result.success(assets)

    def search_assets(self, query: str) -> Result:
        assets = self.repo.search_assets(query)
        return Result.success(assets)

    # ── UC-FA-03: Depreciation Engine ───────────────────────────────────

    def run_depreciation(self, period: str, user: str = "system") -> Result:
        try:
            self._validate_period_open(period)
        except ValidationError as e:
            return Result.failure(e)

        if self.repo.depreciation_exists_for_period(period):
            return Result.failure(AccountError(ErrorCodes.FA_DEPRECIATION_ALREADY_RUN, period=period))

        assets = self.repo.get_assets_due_for_depreciation(period)
        if not assets:
            return Result.failure(AccountError(ErrorCodes.FA_NO_ASSETS_FOR_DEPRECIATION, period=period))

        records: List[DepreciationRecord] = []
        total_amount = Decimal("0")

        for asset in assets:
            depr_amount = self._compute_depreciation(asset, period)
            if depr_amount <= Decimal("0"):
                continue

            new_accum = _vnd(asset.accumulated_depreciation + depr_amount)
            max_depr = _vnd(asset.original_cost - asset.residual_value)
            if new_accum > max_depr:
                depr_amount = max_depr - asset.accumulated_depreciation
                new_accum = max_depr

            nbv = _vnd(asset.original_cost - new_accum)
            record = DepreciationRecord(
                asset_id=asset.id,
                period=period,
                depreciation_amount=_vnd(depr_amount),
                accumulated_total=new_accum,
                nbv=nbv,
                is_posted=True,
            )
            records.append(record)
            total_amount += depr_amount

            self.repo.update_asset(asset.id, accumulated_depreciation=new_accum)

            if new_accum >= max_depr:
                self.repo.update_asset_status(asset.id, AssetStatus.FULLY_DEPRECIATED)

        if not records:
            return Result.failure(AccountError(ErrorCodes.FA_NO_ASSETS_FOR_DEPRECIATION, period=period))

        batch_result = self.repo.batch_create_depreciation(records)
        if batch_result.is_failure():
            return batch_result

        gl_result = self.repo.post_depreciation_gl(period, {"6274": total_amount, "2141": total_amount})
        if gl_result.is_failure():
            return gl_result

        return Result.success({
            "count": len(records),
            "total_amount": str(_vnd(total_amount)),
            "period": period,
        })

    def _compute_depreciation(self, asset: FixedAsset, period: str) -> Decimal:
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            return self._calc_monthly_straight_line(
                asset.original_cost, asset.residual_value, asset.useful_life_months
            )
        elif asset.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
            nbv = asset.original_cost - asset.accumulated_depreciation
            return self._calc_monthly_declining_balance(nbv, asset.useful_life_months)
        elif asset.depreciation_method == DepreciationMethod.UNITS_OF_PRODUCTION:
            lifetime_units = Decimal(asset.useful_life_months * 100)
            period_units = Decimal("100")
            depr_base = asset.original_cost - asset.residual_value
            if lifetime_units <= 0:
                return Decimal("0")
            return _vnd(depr_base * period_units / lifetime_units)
        return Decimal("0")

    def get_depreciation_for_period(self, period: str) -> Result:
        records = self.repo.get_depreciation_for_period(period)
        return Result.success(records)

    def get_asset_depreciation(self, asset_id: int) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
        records = self.repo.get_depreciation_records(asset_id)
        return Result.success(records)

    # ── UC-FA-04: Asset Adjustments ─────────────────────────────────────

    def adjust_asset(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))

        if asset.status in (AssetStatus.DISPOSED, AssetStatus.FULLY_DEPRECIATED):
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_ALREADY_DISPOSED, asset_id=asset_id))

        try:
            adjustment = FAAdjustment(
                asset_id=asset_id,
                previous_cost=asset.original_cost,
                new_cost=asset.original_cost,
                **data,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

        if asset.depreciation_method != DepreciationMethod.STRAIGHT_LINE and adjustment.adjustment_type == FAAdjustmentType.UPGRADE:
            pass

        if adjustment.adjustment_type in (FAAdjustmentType.UPGRADE, FAAdjustmentType.COST_CORRECTION):
            new_cost = adjustment.new_cost
            if new_cost <= Decimal("0"):
                return Result.failure(AccountError(ErrorCodes.FA_ADJUSTMENT_EXCEEDS_COST, asset_id=asset_id))
            adj_result = self.repo.update_asset(asset_id, original_cost=new_cost)
            if adj_result.is_failure():
                return adj_result

        elif adjustment.adjustment_type == FAAdjustmentType.IMPAIRMENT:
            new_cost = asset.original_cost - adjustment.amount
            if new_cost < asset.residual_value:
                return Result.failure(AccountError(ErrorCodes.FA_ADJUSTMENT_EXCEEDS_COST, asset_id=asset_id))
            self.repo.update_asset(asset_id, original_cost=new_cost)
            adjustment.previous_depreciation = asset.accumulated_depreciation

        elif adjustment.adjustment_type == FAAdjustmentType.REVALUATION:
            if adjustment.amount < asset.carrying_amount:
                return Result.failure(AccountError(ErrorCodes.FA_REVALUATION_BELOW_NBV, asset_id=asset_id))
            self.repo.update_asset(asset_id, original_cost=adjustment.amount)

        adj_created = self.repo.create_adjustment(adjustment)
        self.repo.log_audit(f"FA-{asset_id}", "adjustment", f"{adjustment.adjustment_type.value}: {adjustment.reason}", adjustment.created_by or "system")
        return adj_created

    # ── UC-FA-05: Asset Transfer ────────────────────────────────────────

    def transfer_asset(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))

        try:
            transfer = FATransfer(asset_id=asset_id, **data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

        updates = {
            "department_id": transfer.to_department_id,
            "location": transfer.to_location,
        }
        self.repo.update_asset(asset_id, **{k: v for k, v in updates.items() if v is not None})
        result = self.repo.create_transfer(transfer)
        self.repo.log_audit(f"FA-{asset_id}", "transfer", f"from {transfer.from_department_id} to {transfer.to_department_id}: {transfer.reason}", transfer.created_by or "system")
        return result

    # ── UC-FA-06: Asset Disposal ────────────────────────────────────────

    def dispose_asset(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))

        if asset.status == AssetStatus.DISPOSED:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_ALREADY_DISPOSED, asset_id=asset_id))

        nbv_at_disposal = asset.original_cost - asset.accumulated_depreciation

        try:
            disposal = FADisposal(
                asset_id=asset_id,
                nbv_at_disposal=nbv_at_disposal,
                **data,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

        self.repo.update_asset_status(asset_id, AssetStatus.DISPOSED)
        result = self.repo.create_disposal(disposal)
        self.repo.log_audit(f"FA-{asset_id}", "disposal", f"{disposal.disposal_type.value}: {disposal.reason}, gain_loss={disposal.gain_loss}", disposal.created_by or "system")
        return result

    # ── UC-FA-07: FA Inventory ──────────────────────────────────────────

    def create_inventory(self, data: dict) -> Result:
        try:
            lines_data = data.pop("lines", [])
            inventory = FAInventory(**data)
            lines = []
            assets_in_scope = self.repo.list_assets(department_id=data.get("department_id"))
            asset_map = {a.id: a for a in assets_in_scope}

            for ld in lines_data:
                line = FAInventoryLine(inventory_id=0, **ld)
                asset_id = line.asset_id
                asset = asset_map.get(asset_id) or self.repo.get_asset(asset_id)
                if asset:
                    line.book_quantity = 1
                    line.physical_quantity = ld.get("physical_quantity", 1)
                lines.append(line)

            inventory.asset_count_book = len(assets_in_scope)
            inventory.asset_count_physical = len([l for l in lines if l.physical_quantity > 0])
            inventory.lines = lines
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_inventory(inventory)

    def get_inventory(self, inventory_id: int) -> Result:
        inv = self.repo.get_inventory(inventory_id)
        if not inv:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, inventory_id=inventory_id))
        return Result.success(inv)

    def list_inventories(self, status: Optional[str] = None) -> Result:
        invs = self.repo.list_inventories(status=status)
        return Result.success(invs)

    def add_inventory_line(self, inventory_id: int, data: dict) -> Result:
        inv = self.repo.get_inventory(inventory_id)
        if not inv:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, inventory_id=inventory_id))
        if inv.status == InventoryStatus.RESOLVED:
            return Result.failure(AccountError(ErrorCodes.FA_INVENTORY_UNRESOLVED, inventory_id=inventory_id))
        try:
            line = FAInventoryLine(inventory_id=inventory_id, **data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_inventory_line(line)

    def resolve_inventory(self, inventory_id: int) -> Result:
        inv = self.repo.get_inventory(inventory_id)
        if not inv:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, inventory_id=inventory_id))
        if inv.status == InventoryStatus.RESOLVED:
            return Result.failure(AccountError(ErrorCodes.FA_INVENTORY_UNRESOLVED, inventory_id=inventory_id))
        return self.repo.update_asset(inventory_id, status=InventoryStatus.RESOLVED, resolved_at=datetime.now(timezone.utc))

    # ── UC-FA-08: Spare Parts & Components ──────────────────────────────

    def add_spare_part(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
        try:
            part = FASparePart(asset_id=asset_id, **data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_spare_part(part)

    def get_spare_parts(self, asset_id: int) -> Result:
        parts = self.repo.get_spare_parts(asset_id)
        return Result.success(parts)

    def add_component(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
        try:
            component = FAComponent(asset_id=asset_id, **data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_component(component)

    def get_components(self, asset_id: int) -> Result:
        components = self.repo.get_components(asset_id)
        return Result.success(components)

    # ── UC-FA-09: Biological Assets ─────────────────────────────────────

    def register_biological_asset(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
        if asset.asset_type != AssetType.BIOLOGICAL:
            return Result.failure(AccountError(ErrorCodes.FA_INVALID_BIOLOGICAL_TYPE, asset_id=asset_id))
        try:
            bio = BiologicalAsset(asset_id=asset_id, **data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_biological_asset(bio)

    def update_biological_asset(self, bio_id: int, **updates) -> Result:
        return self.repo.update_biological_asset(bio_id, **updates)

    def list_biological_assets(
        self,
        biological_type: Optional[str] = None,
        growth_stage: Optional[str] = None,
    ) -> Result:
        bios = self.repo.list_biological_assets(
            biological_type=biological_type,
            growth_stage=growth_stage,
        )
        return Result.success(bios)

    def create_biological_provision(self, bio_id: int, data: dict) -> Result:
        try:
            provision = BiologicalProvision(biological_asset_id=bio_id, **data)
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_biological_provision(provision)

    # ── UC-FA-10: FA Reports ────────────────────────────────────────────

    def get_asset_register_report(
        self,
        asset_type: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> Result:
        assets = self.repo.list_assets(
            asset_type=asset_type,
            department_id=department_id,
        )
        if not assets:
            return Result.failure(AccountError(ErrorCodes.FA_NO_DATA))

        rows = []
        total_cost = Decimal("0")
        total_accum = Decimal("0")
        total_nbv = Decimal("0")

        for a in assets:
            nbv = a.original_cost - a.accumulated_depreciation
            depr_base = a.original_cost - a.residual_value
            annual_rate = Decimal("0")
            if depr_base > 0 and a.useful_life_months > 0:
                annual_rate = _vnd(
                    (a.accumulated_depreciation / depr_base) * Decimal("100")
                    / (Decimal(a.useful_life_months) / Decimal("12"))
                ) if a.accumulated_depreciation > 0 and a.useful_life_months > 0 else _vnd(
                    Decimal("100") / (Decimal(a.useful_life_months) / Decimal("12"))
                )

            total_cost += a.original_cost
            total_accum += a.accumulated_depreciation
            total_nbv += nbv

            rows.append({
                "asset_id": a.id,
                "code": a.code,
                "name": a.name,
                "category_id": a.category_id,
                "original_cost": str(a.original_cost),
                "accumulated_depreciation": str(a.accumulated_depreciation),
                "nbv": str(nbv),
                "depreciation_rate": str(annual_rate),
                "status": a.status.value if a.status else "active",
                "in_use_date": a.in_use_date.isoformat(),
                "department_id": a.department_id,
            })

        return Result.success({
            "assets": rows,
            "totals": {
                "original_cost": str(total_cost),
                "accumulated_depreciation": str(total_accum),
                "nbv": str(total_nbv),
            },
            "count": len(rows),
        })

    def get_depreciation_schedule_report(
        self,
        asset_id: Optional[int] = None,
        period: Optional[str] = None,
    ) -> Result:
        records: List[DepreciationRecord] = []
        asset = None

        if asset_id:
            asset = self.repo.get_asset(asset_id)
            if not asset:
                return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
            records = self.repo.get_depreciation_records(asset_id)
        elif period:
            records = self.repo.get_depreciation_for_period(period)
        else:
            return Result.failure(AccountError(ErrorCodes.MISSING_FIELD, field="asset_id or period"))

        if not records:
            return Result.failure(AccountError(ErrorCodes.FA_NO_DATA))

        rows = []
        total_per_asset: Dict[int, Decimal] = {}
        for r in records:
            rows.append({
                "asset_id": r.asset_id,
                "period": r.period,
                "depreciation_amount": str(r.depreciation_amount),
                "accumulated_total": str(r.accumulated_total),
                "nbv": str(r.nbv),
                "is_posted": r.is_posted,
            })
            total_per_asset[r.asset_id] = total_per_asset.get(r.asset_id, Decimal("0")) + r.depreciation_amount

        summary = []
        for aid, total in total_per_asset.items():
            a = self.repo.get_asset(aid)
            summary.append({
                "asset_id": aid,
                "asset_code": a.code if a else "",
                "asset_name": a.name if a else "",
                "total_depreciation": str(total),
            })

        return Result.success({
            "rows": rows,
            "summary": summary,
            "total_count": len(records),
        })

    def get_asset_increase_decrease_report(self, from_date: str, to_date: str) -> Result:
        from_dt = date.fromisoformat(from_date)
        to_dt = date.fromisoformat(to_date)

        all_assets = self.repo.list_assets()
        opening_balance = Decimal("0")
        increases: List[dict] = []
        decreases: List[dict] = []
        closing_balance = Decimal("0")

        for a in all_assets:
            if a.acquisition_date < from_dt:
                opening_balance += a.original_cost

            if from_dt <= a.acquisition_date <= to_dt:
                increases.append({
                    "asset_id": a.id,
                    "code": a.code,
                    "name": a.name,
                    "type": "new",
                    "amount": str(a.original_cost),
                    "date": a.acquisition_date.isoformat(),
                })

            if a.status == AssetStatus.DISPOSED:
                disposal = self.repo.get_disposal(a.id)
                if disposal and from_dt <= disposal.disposal_date <= to_dt:
                    decreases.append({
                        "asset_id": a.id,
                        "code": a.code,
                        "name": a.name,
                        "type": "disposal",
                        "amount": str(a.original_cost),
                        "date": disposal.disposal_date.isoformat(),
                    })

            if a.acquisition_date <= to_dt and a.status != AssetStatus.DISPOSED:
                closing_balance += a.original_cost

        total_increase = sum(Decimal(d["amount"]) for d in increases)
        total_decrease = sum(Decimal(d["amount"]) for d in decreases)

        return Result.success({
            "from_date": from_date,
            "to_date": to_date,
            "opening_balance": str(opening_balance),
            "increases": {
                "items": increases,
                "total": str(total_increase),
                "count": len(increases),
            },
            "decreases": {
                "items": decreases,
                "total": str(total_decrease),
                "count": len(decreases),
            },
            "closing_balance": str(closing_balance),
        })

    def get_asset_status_summary(self, asset_type: Optional[str] = None) -> Result:
        assets = self.repo.list_assets(asset_type=asset_type)
        if not assets:
            return Result.failure(AccountError(ErrorCodes.FA_NO_DATA))

        summary: Dict[str, dict] = {}
        for status in AssetStatus:
            key = status.value
            filtered = [a for a in assets if a.status == status]
            total_cost = sum(a.original_cost for a in filtered)
            summary[key] = {
                "count": len(filtered),
                "total_original_cost": str(total_cost),
            }

        return Result.success({
            "summary": summary,
            "total_assets": len(assets),
            "asset_type": asset_type or "all",
        })

    # ── UC-FA-11: TT 99/2025 Migration ──────────────────────────────────

    def run_tt99_migration(self, dry_run: bool = True, user: str = "system") -> Result:
        assets = self.repo.list_assets()
        if not assets:
            return Result.failure(AccountError(ErrorCodes.FA_NO_DATA))

        reclass_441_to_4118: List[dict] = []
        create_tk215: List[dict] = []
        adjust_tk2414: List[dict] = []
        other_issues: List[dict] = []

        for a in assets:
            if a.fund_source in (FundSource.GOVERNMENT_GRANT, FundSource.CAPITAL_CONSTRUCTION):
                reclass_441_to_4118.append({
                    "asset_id": a.id,
                    "code": a.code,
                    "name": a.name,
                    "current_fund_source": a.fund_source.value,
                    "recommended_action": "Reclassify fund source to 4118 per TT99/2025",
                })

            if a.asset_type == AssetType.BIOLOGICAL:
                if a.asset_classification == AssetClassification.PERENNIAL_PLANTS_LIVESTOCK:
                    create_tk215.append({
                        "asset_id": a.id,
                        "code": a.code,
                        "name": a.name,
                        "recommended_action": "Create TK 215 (tree/animals) account per TT99/2025",
                    })

            if a.use_type == UseType.CONSTRUCTION and a.status == AssetStatus.ACTIVE:
                if a.accumulated_depreciation > 0:
                    adjust_tk2414.append({
                        "asset_id": a.id,
                        "code": a.code,
                        "name": a.name,
                        "accumulated_depreciation": str(a.accumulated_depreciation),
                        "recommended_action": "Adjust TK 2414 account per TT99/2025",
                    })

        migration_results = {
            "reclassify_441_to_4118": reclass_441_to_4118,
            "create_tk215_biological": create_tk215,
            "adjust_2414_accounts": adjust_tk2414,
            "other_observations": other_issues,
            "dry_run": dry_run,
        }

        if not dry_run:
            for item in reclass_441_to_4118:
                self.repo.update_asset(item["asset_id"], fund_source=FundSource.OWNERS_EQUITY)
                self.repo.log_audit(f"FA-{item['asset_id']}", "tt99_migration", f"Reclassified fund source per TT99/2025", user)

            for item in create_tk215:
                self.repo.log_audit(f"FA-{item['asset_id']}", "tt99_migration", f"TK 215 classification per TT99/2025", user)

            migration_results["executed_by"] = user
            migration_results["executed_at"] = datetime.now(timezone.utc).isoformat()

        return Result.success(migration_results)

    # ── UC-FA-12: Depreciation Suspension (TT 30/2025) ──────────────────

    def suspend_depreciation(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))

        if asset.status != AssetStatus.ACTIVE:
            return Result.failure(AccountError(ErrorCodes.STATE_TRANSITION, action="suspend", subject="asset", state=asset.status.value))

        reason = data.get("reason", "")
        start_period = data.get("start_period", "")
        end_period = data.get("end_period", "")
        approved_by = data.get("approved_by", "")

        if not reason or not start_period or not end_period or not approved_by:
            return Result.failure(AccountError(ErrorCodes.REASON_EMPTY))

        try:
            self._validate_period_open(start_period)
        except ValidationError as e:
            return Result.failure(e)

        result = self.repo.update_asset_status(asset_id, AssetStatus.SUSPENDED)

        adjustment = FAAdjustment(
            asset_id=asset_id,
            adjustment_type=FAAdjustmentType.IMPAIRMENT,
            amount=Decimal("0"),
            previous_cost=asset.original_cost,
            new_cost=asset.original_cost,
            reason=f"Suspension: {reason} (periods {start_period} to {end_period})",
            effective_date=date.today(),
            created_by=data.get("created_by", "system"),
        )
        self.repo.create_adjustment(adjustment)
        self.repo.log_audit(f"FA-{asset_id}", "depreciation_suspend", f"Suspended {start_period} to {end_period}: {reason} (approved by {approved_by})", data.get("created_by", "system"))

        return result

    def resume_depreciation(self, asset_id: int, data: dict) -> Result:
        asset = self.repo.get_asset(asset_id)
        if not asset:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))

        if asset.status != AssetStatus.SUSPENDED:
            return Result.failure(AccountError(ErrorCodes.STATE_TRANSITION, action="resume", subject="asset", state=asset.status.value))

        reason = data.get("reason", "")
        resume_period = data.get("resume_period", "")
        approved_by = data.get("approved_by", "")

        if not reason or not resume_period or not approved_by:
            return Result.failure(AccountError(ErrorCodes.REASON_EMPTY))

        try:
            self._validate_period_open(resume_period)
        except ValidationError as e:
            return Result.failure(e)

        suspension_start = data.get("suspension_start_period", "2025-01")
        start_parts = suspension_start.split("-")
        resume_parts = resume_period.split("-")
        suspended_months = (
            (int(resume_parts[0]) - int(start_parts[0])) * 12
            + (int(resume_parts[1]) - int(start_parts[1]))
        )
        if suspended_months < 0:
            suspended_months = 0

        new_life = asset.useful_life_months + suspended_months
        self.repo.update_asset(asset_id, useful_life_months=new_life)
        result = self.repo.update_asset_status(asset_id, AssetStatus.ACTIVE)

        adjustment = FAAdjustment(
            asset_id=asset_id,
            adjustment_type=FAAdjustmentType.UPGRADE,
            amount=Decimal("0"),
            previous_cost=asset.original_cost,
            new_cost=asset.original_cost,
            reason=f"Resume: {reason} (from {resume_period}), life extended by {suspended_months} months",
            effective_date=date.today(),
            created_by=data.get("created_by", "system"),
        )
        self.repo.create_adjustment(adjustment)
        self.repo.log_audit(f"FA-{asset_id}", "depreciation_resume", f"Resumed at {resume_period}: {reason} (approved by {approved_by}), life extended by {suspended_months}m", data.get("created_by", "system"))

        return result
