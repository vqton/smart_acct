from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_

from domain import (
    AssetType, DepreciationMethod, AssetStatus, DisposalType, AdjustmentType,
    BiologicalType, GrowthStage, AssetClassification, FundSource, UseType,
    FACategory, FixedAsset, DepreciationRecord, FAAdjustment, FADisposal,
    FAInventory, FAInventoryLine, FATransfer, FASparePart, FAComponent,
    BiologicalAsset, BiologicalProvision,
    Result, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.models.fa_models import (
    FACategoryModel, FixedAssetModel, DepreciationRecordModel,
    FAAdjustmentModel, FADisposalModel, FAInventoryModel, FAInventoryLineModel,
    FATransferModel, FASparePartModel, FAComponentModel,
    BiologicalAssetModel, BiologicalProvisionModel,
    AssetTypeDB, DepreciationMethodDB, AssetStatusDB, DisposalTypeDB,
    AdjustmentTypeDB, BiologicalTypeDB, GrowthStageDB, AssetClassificationDB,
    FundSourceDB, UseTypeDB,
)
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel
from infrastructure.models.coa_models import COAModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _period_to_date(period: str) -> date:
    parts = period.split("-")
    y, m = int(parts[0]), int(parts[1])
    if m == 12:
        return date(y, 12, 31)
    import calendar
    return date(y, m, calendar.monthrange(y, m)[1])


class FARepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Category: conversion helpers ─────────────────────────────────

    def _cat_to_domain(self, m: FACategoryModel) -> FACategory:
        d = FACategory(
            code=m.code,
            name=m.name,
            asset_type=AssetType.TANGIBLE,
            asset_classification=AssetClassification.OTHER,
            default_depreciation_method=DepreciationMethod.STRAIGHT_LINE,
            default_useful_life_min=m.useful_life_months,
            default_useful_life_max=m.useful_life_months,
            description=m.description or "",
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        d.id = m.id
        return d

    def _cat_to_model(self, d: FACategory) -> FACategoryModel:
        return FACategoryModel(
            code=d.code,
            name=d.name,
            useful_life_months=d.default_useful_life_min or d.default_useful_life_max,
            depreciation_method=DepreciationMethodDB(d.default_depreciation_method.value) if isinstance(d.default_depreciation_method, DepreciationMethod) else DepreciationMethodDB(d.default_depreciation_method),
            description=d.description,
            is_active=d.is_active,
        )

    def create_category(self, category: FACategory) -> Result:
        existing = self.session.execute(
            select(FACategoryModel).where(FACategoryModel.code == category.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_CODE_DUPLICATE, code=category.code))
        model = self._cat_to_model(category)
        self.session.add(model)
        self.session.flush()
        created = self._cat_to_domain(model)
        if category.asset_type != AssetType.TANGIBLE:
            created.asset_type = category.asset_type
        if category.asset_classification != AssetClassification.OTHER:
            created.asset_classification = category.asset_classification
        if category.default_depreciation_method != DepreciationMethod.STRAIGHT_LINE:
            created.default_depreciation_method = category.default_depreciation_method
        return Result.success(created)

    def get_category(self, category_id: int) -> Optional[FACategory]:
        m = self.session.get(FACategoryModel, category_id)
        return self._cat_to_domain(m) if m else None

    def get_category_by_code(self, code: str) -> Optional[FACategory]:
        m = self.session.execute(
            select(FACategoryModel).where(FACategoryModel.code == code)
        ).scalar_one_or_none()
        return self._cat_to_domain(m) if m else None

    def update_category(self, category_id: int, **updates) -> Result:
        m = self.session.get(FACategoryModel, category_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_NOT_FOUND, category_id=category_id))
        if "code" in updates:
            dup = self.session.execute(
                select(FACategoryModel).where(
                    FACategoryModel.code == updates["code"],
                    FACategoryModel.id != category_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_CODE_DUPLICATE, code=updates["code"]))
        for key, val in updates.items():
            if key == "default_depreciation_method":
                setattr(m, "depreciation_method", DepreciationMethodDB(val.value) if isinstance(val, DepreciationMethod) else DepreciationMethodDB(val))
            elif key == "default_useful_life_min":
                setattr(m, "useful_life_months", val)
            elif key == "default_useful_life_max":
                if m.useful_life_months is None:
                    setattr(m, "useful_life_months", val)
            elif hasattr(m, key):
                setattr(m, key, val)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._cat_to_domain(m))

    def delete_category(self, category_id: int) -> Result:
        m = self.session.get(FACategoryModel, category_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_NOT_FOUND, category_id=category_id))
        asset_count = self.session.execute(
            select(func.count(FixedAssetModel.id)).where(FixedAssetModel.category_id == category_id)
        ).scalar() or 0
        if asset_count > 0:
            return Result.failure(AccountError(ErrorCodes.FA_CATEGORY_HAS_ASSETS, category_id=category_id))
        self.session.delete(m)
        self.session.flush()
        return Result.success(None)

    def list_categories(self, asset_type: Optional[str] = None) -> List[FACategory]:
        stmt = select(FACategoryModel).order_by(FACategoryModel.code)
        if asset_type:
            pass
        return [self._cat_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def category_has_assets(self, category_id: int) -> bool:
        cnt = self.session.execute(
            select(func.count(FixedAssetModel.id)).where(FixedAssetModel.category_id == category_id)
        ).scalar() or 0
        return cnt > 0

    # ── Asset: conversion helpers ────────────────────────────────────

    def _asset_to_domain(self, m: FixedAssetModel) -> FixedAsset:
        a = FixedAsset(
            code=m.code,
            name=m.name,
            category_id=m.category_id,
            asset_type=AssetType(m.asset_type.value) if isinstance(m.asset_type, AssetTypeDB) else AssetType(m.asset_type),
            asset_classification=AssetClassification(m.asset_classification.value) if isinstance(m.asset_classification, AssetClassificationDB) else AssetClassification(m.asset_classification),
            original_cost=m.original_cost,
            accumulated_depreciation=m.accumulated_depreciation,
            residual_value=m.residual_value,
            carrying_amount=m.original_cost - m.accumulated_depreciation,
            useful_life_months=m.useful_life_months,
            depreciation_method=DepreciationMethod(m.depreciation_method.value) if isinstance(m.depreciation_method, DepreciationMethodDB) else DepreciationMethod(m.depreciation_method),
            acquisition_date=m.acquisition_date,
            in_use_date=m.in_use_date,
            department_id=str(m.department_id) if m.department_id is not None else None,
            location=m.location,
            status=AssetStatus(m.status.value) if isinstance(m.status, AssetStatusDB) else AssetStatus(m.status),
            fund_source=FundSource(m.fund_source.value) if isinstance(m.fund_source, FundSourceDB) else FundSource(m.fund_source),
            use_type=UseType(m.use_type.value) if isinstance(m.use_type, UseTypeDB) else UseType(m.use_type),
            supplier=m.supplier,
            invoice_ref=m.invoice_ref,
            description=m.description or "",
            created_by=m.created_by,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        a.id = m.id
        return a

    def _asset_to_model(self, d: FixedAsset) -> FixedAssetModel:
        dept_id = None
        if d.department_id is not None:
            try:
                dept_id = int(d.department_id)
            except (ValueError, TypeError):
                dept_id = None
        return FixedAssetModel(
            code=d.code,
            name=d.name,
            category_id=d.category_id,
            asset_type=AssetTypeDB(d.asset_type.value) if isinstance(d.asset_type, AssetType) else AssetTypeDB(d.asset_type),
            asset_classification=AssetClassificationDB(d.asset_classification.value) if isinstance(d.asset_classification, AssetClassification) else AssetClassificationDB(d.asset_classification),
            original_cost=_vnd(d.original_cost),
            accumulated_depreciation=_vnd(d.accumulated_depreciation),
            residual_value=_vnd(d.residual_value),
            useful_life_months=d.useful_life_months,
            depreciation_method=DepreciationMethodDB(d.depreciation_method.value) if isinstance(d.depreciation_method, DepreciationMethod) else DepreciationMethodDB(d.depreciation_method),
            acquisition_date=d.acquisition_date,
            in_use_date=d.in_use_date,
            department_id=dept_id,
            location=d.location,
            status=AssetStatusDB(d.status.value) if isinstance(d.status, AssetStatus) else AssetStatusDB(d.status),
            fund_source=FundSourceDB(d.fund_source.value) if isinstance(d.fund_source, FundSource) else FundSourceDB(d.fund_source),
            use_type=UseTypeDB(d.use_type.value) if isinstance(d.use_type, UseType) else UseTypeDB(d.use_type),
            supplier=d.supplier,
            invoice_ref=d.invoice_ref,
            description=d.description,
            created_by=d.created_by or "",
        )

    def create_asset(self, asset: FixedAsset) -> Result:
        existing = self.session.execute(
            select(FixedAssetModel).where(FixedAssetModel.code == asset.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_CODE_DUPLICATE, code=asset.code))
        model = self._asset_to_model(asset)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._asset_to_domain(model))

    def get_asset(self, asset_id: int) -> Optional[FixedAsset]:
        m = self.session.get(FixedAssetModel, asset_id)
        return self._asset_to_domain(m) if m else None

    def get_asset_by_code(self, code: str) -> Optional[FixedAsset]:
        m = self.session.execute(
            select(FixedAssetModel).where(FixedAssetModel.code == code)
        ).scalar_one_or_none()
        return self._asset_to_domain(m) if m else None

    def update_asset(self, asset_id: int, **updates) -> Result:
        m = self.session.get(FixedAssetModel, asset_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
        if "code" in updates:
            dup = self.session.execute(
                select(FixedAssetModel).where(
                    FixedAssetModel.code == updates["code"],
                    FixedAssetModel.id != asset_id,
                )
            ).scalar_one_or_none()
            if dup:
                return Result.failure(AccountError(ErrorCodes.FA_ASSET_CODE_DUPLICATE, code=updates["code"]))
        enum_fields = {
            "asset_type": (AssetTypeDB, AssetType),
            "asset_classification": (AssetClassificationDB, AssetClassification),
            "depreciation_method": (DepreciationMethodDB, DepreciationMethod),
            "status": (AssetStatusDB, AssetStatus),
            "fund_source": (FundSourceDB, FundSource),
            "use_type": (UseTypeDB, UseType),
        }
        for key, val in updates.items():
            if key in enum_fields:
                db_enum, domain_enum = enum_fields[key]
                setattr(m, key, db_enum(val.value) if isinstance(val, domain_enum) else db_enum(val))
            elif key == "original_cost" or key == "accumulated_depreciation" or key == "residual_value":
                setattr(m, key, _vnd(val))
            elif key == "department_id" and val is not None:
                try:
                    setattr(m, key, int(val))
                except (ValueError, TypeError):
                    setattr(m, key, None)
            elif key == "department_id" and val is None:
                setattr(m, key, None)
            elif key == "carrying_amount":
                pass
            elif hasattr(m, key):
                setattr(m, key, val)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._asset_to_domain(m))

    def update_asset_status(self, asset_id: int, status: AssetStatus) -> Result:
        m = self.session.get(FixedAssetModel, asset_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, asset_id=asset_id))
        m.status = AssetStatusDB(status.value) if isinstance(status, AssetStatus) else AssetStatusDB(status)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._asset_to_domain(m))

    def list_assets(
        self,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        asset_type: Optional[str] = None,
    ) -> List[FixedAsset]:
        stmt = select(FixedAssetModel).order_by(FixedAssetModel.code)
        if category_id is not None:
            stmt = stmt.where(FixedAssetModel.category_id == category_id)
        if status:
            stmt = stmt.where(FixedAssetModel.status == status)
        if department_id is not None:
            stmt = stmt.where(FixedAssetModel.department_id == department_id)
        if asset_type:
            stmt = stmt.where(FixedAssetModel.asset_type == asset_type)
        return [self._asset_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def search_assets(self, query: str) -> List[FixedAsset]:
        pattern = f"%{query}%"
        stmt = select(FixedAssetModel).where(
            or_(
                FixedAssetModel.code.ilike(pattern),
                FixedAssetModel.name.ilike(pattern),
                FixedAssetModel.supplier.ilike(pattern),
                FixedAssetModel.invoice_ref.ilike(pattern),
                FixedAssetModel.description.ilike(pattern),
            )
        ).order_by(FixedAssetModel.code)
        return [self._asset_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def get_assets_due_for_depreciation(self, period: str) -> List[FixedAsset]:
        period_end = _period_to_date(period)
        subq = select(DepreciationRecordModel.asset_id).where(
            DepreciationRecordModel.period == period
        )
        stmt = select(FixedAssetModel).where(
            FixedAssetModel.acquisition_date <= period_end,
            FixedAssetModel.status == AssetStatusDB.ACTIVE,
            FixedAssetModel.original_cost > FixedAssetModel.accumulated_depreciation,
            ~FixedAssetModel.id.in_(subq),
        ).order_by(FixedAssetModel.code)
        return [self._asset_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Depreciation: conversion helpers ─────────────────────────────

    def _depr_to_domain(self, m: DepreciationRecordModel) -> DepreciationRecord:
        d = DepreciationRecord(
            asset_id=m.asset_id,
            period=m.period,
            depreciation_amount=m.depreciation_amount,
            accumulated_total=m.accumulated_after,
            nbv=m.net_book_value_after,
            is_posted=not m.is_manual,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _depr_to_model(self, d: DepreciationRecord) -> DepreciationRecordModel:
        return DepreciationRecordModel(
            asset_id=d.asset_id,
            period=d.period,
            depreciation_date=_period_to_date(d.period),
            depreciation_amount=_vnd(d.depreciation_amount),
            accumulated_after=_vnd(d.accumulated_total),
            net_book_value_after=_vnd(d.nbv),
            is_manual=not d.is_posted,
            notes="",
            created_by="system",
        )

    def create_depreciation_record(self, record: DepreciationRecord) -> Result:
        existing = self.session.execute(
            select(DepreciationRecordModel).where(
                DepreciationRecordModel.asset_id == record.asset_id,
                DepreciationRecordModel.period == record.period,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(AccountError(ErrorCodes.FA_DEPRECIATION_ALREADY_RUN, asset_id=record.asset_id, period=record.period))
        model = self._depr_to_model(record)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._depr_to_domain(model))

    def get_depreciation_records(self, asset_id: int) -> List[DepreciationRecord]:
        stmt = select(DepreciationRecordModel).where(
            DepreciationRecordModel.asset_id == asset_id
        ).order_by(DepreciationRecordModel.period)
        return [self._depr_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def get_depreciation_for_period(self, period: str) -> List[DepreciationRecord]:
        stmt = select(DepreciationRecordModel).where(
            DepreciationRecordModel.period == period
        ).order_by(DepreciationRecordModel.asset_id)
        return [self._depr_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def get_depreciation_for_asset_period(self, asset_id: int, period: str) -> Optional[DepreciationRecord]:
        m = self.session.execute(
            select(DepreciationRecordModel).where(
                DepreciationRecordModel.asset_id == asset_id,
                DepreciationRecordModel.period == period,
            )
        ).scalar_one_or_none()
        return self._depr_to_domain(m) if m else None

    def depreciation_exists_for_period(self, period: str) -> bool:
        cnt = self.session.execute(
            select(func.count(DepreciationRecordModel.id)).where(
                DepreciationRecordModel.period == period
            )
        ).scalar() or 0
        return cnt > 0

    def batch_create_depreciation(self, records: List[DepreciationRecord]) -> Result:
        models = []
        for r in records:
            existing = self.session.execute(
                select(DepreciationRecordModel).where(
                    DepreciationRecordModel.asset_id == r.asset_id,
                    DepreciationRecordModel.period == r.period,
                )
            ).scalar_one_or_none()
            if existing:
                return Result.failure(AccountError(ErrorCodes.FA_DEPRECIATION_ALREADY_RUN, asset_id=r.asset_id, period=r.period))
            models.append(self._depr_to_model(r))
        for m in models:
            self.session.add(m)
        self.session.flush()
        return Result.success([self._depr_to_domain(m) for m in models])

    def delete_depreciation_for_period(self, period: str) -> Result:
        self.session.query(DepreciationRecordModel).filter(
            DepreciationRecordModel.period == period
        ).delete(synchronize_session="fetch")
        self.session.flush()
        return Result.success(None)

    # ── Adjustments: conversion helpers ──────────────────────────────

    def _adj_to_domain(self, m: FAAdjustmentModel) -> FAAdjustment:
        a = FAAdjustment(
            asset_id=m.asset_id,
            adjustment_type=AdjustmentType(m.adjustment_type.value) if isinstance(m.adjustment_type, AdjustmentTypeDB) else AdjustmentType(m.adjustment_type),
            amount=m.amount,
            previous_cost=m.previous_cost,
            new_cost=m.new_cost,
            previous_depreciation=Decimal("0"),
            new_depreciation=Decimal("0"),
            reason=m.reason,
            document_ref=m.reference_number,
            effective_date=m.adjustment_date,
            created_by=m.created_by,
            created_at=m.created_at,
        )
        a.id = m.id
        return a

    def _adj_to_model(self, d: FAAdjustment) -> FAAdjustmentModel:
        return FAAdjustmentModel(
            asset_id=d.asset_id,
            adjustment_type=AdjustmentTypeDB(d.adjustment_type.value) if isinstance(d.adjustment_type, AdjustmentType) else AdjustmentTypeDB(d.adjustment_type),
            adjustment_date=d.effective_date,
            amount=_vnd(d.amount),
            previous_cost=_vnd(d.previous_cost),
            new_cost=_vnd(d.new_cost),
            reason=d.reason,
            reference_number=d.document_ref,
            created_by=d.created_by or "",
        )

    def create_adjustment(self, adjustment: FAAdjustment) -> Result:
        model = self._adj_to_model(adjustment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._adj_to_domain(model))

    def get_adjustments(self, asset_id: int) -> List[FAAdjustment]:
        stmt = select(FAAdjustmentModel).where(
            FAAdjustmentModel.asset_id == asset_id
        ).order_by(FAAdjustmentModel.adjustment_date)
        return [self._adj_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Disposal: conversion helpers ─────────────────────────────────

    def _disp_to_domain(self, m: FADisposalModel) -> FADisposal:
        d = FADisposal(
            asset_id=m.asset_id,
            disposal_type=DisposalType(m.disposal_type.value) if isinstance(m.disposal_type, DisposalTypeDB) else DisposalType(m.disposal_type),
            disposal_date=m.disposal_date,
            proceeds=m.proceeds,
            costs=Decimal("0"),
            nbv_at_disposal=m.net_book_value,
            gain_loss=m.gain_loss,
            buyer_info=m.counterparty,
            reason=m.reason,
            approved_by=m.approved_by,
            document_ref=m.invoice_ref,
            created_by=m.created_by,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def _disp_to_model(self, d: FADisposal) -> FADisposalModel:
        return FADisposalModel(
            asset_id=d.asset_id,
            disposal_type=DisposalTypeDB(d.disposal_type.value) if isinstance(d.disposal_type, DisposalType) else DisposalTypeDB(d.disposal_type),
            disposal_date=d.disposal_date,
            net_book_value=_vnd(d.nbv_at_disposal),
            proceeds=_vnd(d.proceeds),
            gain_loss=_vnd(d.gain_loss),
            reason=d.reason,
            counterparty=d.buyer_info,
            invoice_ref=d.document_ref,
            approved_by=d.approved_by,
            created_by=d.created_by or "",
        )

    def create_disposal(self, disposal: FADisposal) -> Result:
        model = self._disp_to_model(disposal)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._disp_to_domain(model))

    def get_disposal(self, asset_id: int) -> Optional[FADisposal]:
        m = self.session.execute(
            select(FADisposalModel).where(FADisposalModel.asset_id == asset_id)
        ).scalar_one_or_none()
        return self._disp_to_domain(m) if m else None

    # ── Inventory: conversion helpers ────────────────────────────────

    def _inv_to_domain(self, m: FAInventoryModel) -> FAInventory:
        d = FAInventory(
            inventory_date=m.inventory_date,
            department_id=str(m.department_id) if m.department_id is not None else "",
            status=m.status,
            notes=m.notes or "",
            created_by=m.conducted_by,
            created_at=m.created_at,
            lines=[self._invline_to_domain(l) for l in m.lines],
        )
        d.id = m.id
        return d

    def _inv_to_model(self, d: FAInventory) -> FAInventoryModel:
        return FAInventoryModel(
            inventory_date=d.inventory_date,
            inventory_number=f"INK-{d.inventory_date.isoformat()}-{d.department_id}",
            department_id=_safe_int(d.department_id),
            notes=d.notes,
            status=d.status,
            conducted_by=d.created_by or "",
        )

    def _invline_to_domain(self, m: FAInventoryLineModel) -> FAInventoryLine:
        l = FAInventoryLine(
            inventory_id=m.inventory_id,
            asset_id=m.asset_id,
            book_quantity=m.book_quantity,
            physical_quantity=m.actual_quantity,
            difference=m.difference_quantity,
            reason=m.notes,
            resolution=m.notes,
        )
        l.id = m.id
        return l

    def _invline_to_model(self, d: FAInventoryLine) -> FAInventoryLineModel:
        return FAInventoryLineModel(
            inventory_id=d.inventory_id or 0,
            asset_id=d.asset_id,
            book_quantity=d.book_quantity,
            actual_quantity=d.physical_quantity,
            book_cost=Decimal("0"),
            actual_cost=Decimal("0"),
            difference_quantity=d.difference,
            difference_amount=Decimal("0"),
            notes=d.reason or d.resolution,
        )

    def create_inventory(self, inventory: FAInventory) -> Result:
        model = self._inv_to_model(inventory)
        self.session.add(model)
        self.session.flush()
        for line in inventory.lines:
            line_model = self._invline_to_model(line)
            line_model.inventory_id = model.id
            self.session.add(line_model)
        self.session.flush()
        return Result.success(self._inv_to_domain(model))

    def get_inventory(self, inventory_id: int) -> Optional[FAInventory]:
        m = self.session.get(FAInventoryModel, inventory_id)
        return self._inv_to_domain(m) if m else None

    def list_inventories(self, status: Optional[str] = None) -> List[FAInventory]:
        stmt = select(FAInventoryModel).order_by(FAInventoryModel.inventory_date.desc())
        if status:
            stmt = stmt.where(FAInventoryModel.status == status)
        return [self._inv_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def create_inventory_line(self, line: FAInventoryLine) -> Result:
        model = self._invline_to_model(line)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._invline_to_domain(model))

    # ── Transfer: conversion helpers ─────────────────────────────────

    def _trf_to_domain(self, m: FATransferModel) -> FATransfer:
        t = FATransfer(
            asset_id=m.asset_id,
            from_department_id=str(m.from_department_id) if m.from_department_id is not None else "",
            to_department_id=str(m.to_department_id) if m.to_department_id is not None else "",
            from_location=m.from_location,
            to_location=m.to_location,
            effective_date=m.transfer_date,
            reason=m.reason,
            created_by=m.created_by,
            created_at=m.created_at,
        )
        t.id = m.id
        return t

    def _trf_to_model(self, d: FATransfer) -> FATransferModel:
        return FATransferModel(
            asset_id=d.asset_id,
            transfer_date=d.effective_date,
            from_department_id=_safe_int(d.from_department_id),
            to_department_id=_safe_int(d.to_department_id),
            from_location=d.from_location,
            to_location=d.to_location,
            reason=d.reason,
            created_by=d.created_by or "",
        )

    def create_transfer(self, transfer: FATransfer) -> Result:
        model = self._trf_to_model(transfer)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._trf_to_domain(model))

    def get_transfers(self, asset_id: int) -> List[FATransfer]:
        stmt = select(FATransferModel).where(
            FATransferModel.asset_id == asset_id
        ).order_by(FATransferModel.transfer_date)
        return [self._trf_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Spare Parts: conversion helpers ──────────────────────────────

    def _sp_to_domain(self, m: FASparePartModel) -> FASparePart:
        s = FASparePart(
            asset_id=m.asset_id,
            code=m.part_code,
            name=m.part_name,
            quantity=m.quantity,
            unit="pcs",
            value=m.total_cost,
        )
        s.id = m.id
        return s

    def _sp_to_model(self, d: FASparePart) -> FASparePartModel:
        return FASparePartModel(
            asset_id=d.asset_id,
            part_code=d.code,
            part_name=d.name,
            quantity=d.quantity,
            unit_cost=d.value / max(Decimal(d.quantity), Decimal("1")),
            total_cost=_vnd(d.value),
        )

    def create_spare_part(self, part: FASparePart) -> Result:
        model = self._sp_to_model(part)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._sp_to_domain(model))

    def get_spare_parts(self, asset_id: int) -> List[FASparePart]:
        stmt = select(FASparePartModel).where(
            FASparePartModel.asset_id == asset_id
        ).order_by(FASparePartModel.part_code)
        return [self._sp_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Components: conversion helpers ───────────────────────────────

    def _comp_to_domain(self, m: FAComponentModel) -> FAComponent:
        c = FAComponent(
            asset_id=m.asset_id,
            name=m.component_name,
            original_cost=m.original_cost,
            useful_life_months=m.useful_life_months,
            depreciation_method=DepreciationMethod(m.depreciation_method.value) if m.depreciation_method and isinstance(m.depreciation_method, DepreciationMethodDB) else (DepreciationMethod(m.depreciation_method) if m.depreciation_method else None),
        )
        c.id = m.id
        return c

    def _comp_to_model(self, d: FAComponent) -> FAComponentModel:
        return FAComponentModel(
            asset_id=d.asset_id,
            component_name=d.name,
            original_cost=_vnd(d.original_cost),
            useful_life_months=d.useful_life_months,
            depreciation_method=DepreciationMethodDB(d.depreciation_method.value) if d.depreciation_method and isinstance(d.depreciation_method, DepreciationMethod) else (DepreciationMethodDB(d.depreciation_method) if d.depreciation_method else None),
        )

    def create_component(self, component: FAComponent) -> Result:
        model = self._comp_to_model(component)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._comp_to_domain(model))

    def get_components(self, asset_id: int) -> List[FAComponent]:
        stmt = select(FAComponentModel).where(
            FAComponentModel.asset_id == asset_id
        ).order_by(FAComponentModel.component_name)
        return [self._comp_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Biological Assets: conversion helpers ─────────────────────────

    def _bio_to_domain(self, m: BiologicalAssetModel) -> BiologicalAsset:
        b = BiologicalAsset(
            asset_id=m.asset_id,
            biological_type=BiologicalType(m.biological_type.value) if isinstance(m.biological_type, BiologicalTypeDB) else BiologicalType(m.biological_type),
            growth_stage=GrowthStage(m.growth_stage.value) if isinstance(m.growth_stage, GrowthStageDB) else GrowthStage(m.growth_stage),
            quantity=Decimal(str(m.quantity)),
            unit=m.unit,
            planting_date=m.planted_date or date.today(),
            expected_harvest_date=m.expected_harvest_date,
            provision_amount=Decimal("0"),
        )
        b.id = m.id
        return b

    def _bio_to_model(self, d: BiologicalAsset) -> BiologicalAssetModel:
        return BiologicalAssetModel(
            asset_id=d.asset_id,
            biological_type=BiologicalTypeDB(d.biological_type.value) if isinstance(d.biological_type, BiologicalType) else BiologicalTypeDB(d.biological_type),
            growth_stage=GrowthStageDB(d.growth_stage.value) if isinstance(d.growth_stage, GrowthStage) else GrowthStageDB(d.growth_stage),
            quantity=int(d.quantity),
            unit=d.unit,
            planted_date=d.planting_date,
            expected_harvest_date=d.expected_harvest_date,
        )

    def create_biological_asset(self, bio: BiologicalAsset) -> Result:
        model = self._bio_to_model(bio)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._bio_to_domain(model))

    def get_biological_asset(self, asset_id: int) -> Optional[BiologicalAsset]:
        m = self.session.execute(
            select(BiologicalAssetModel).where(BiologicalAssetModel.asset_id == asset_id)
        ).scalar_one_or_none()
        return self._bio_to_domain(m) if m else None

    def update_biological_asset(self, bio_id: int, **updates) -> Result:
        m = self.session.get(BiologicalAssetModel, bio_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.FA_ASSET_NOT_FOUND, bio_id=bio_id))
        enum_fields = {
            "biological_type": (BiologicalTypeDB, BiologicalType),
            "growth_stage": (GrowthStageDB, GrowthStage),
        }
        for key, val in updates.items():
            if key in enum_fields:
                db_enum, domain_enum = enum_fields[key]
                setattr(m, key, db_enum(val.value) if isinstance(val, domain_enum) else db_enum(val))
            elif key == "planting_date":
                setattr(m, "planted_date", val)
            elif key == "quantity":
                setattr(m, key, int(val))
            elif hasattr(m, key):
                setattr(m, key, val)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._bio_to_domain(m))

    def list_biological_assets(
        self,
        biological_type: Optional[str] = None,
        growth_stage: Optional[str] = None,
    ) -> List[BiologicalAsset]:
        stmt = select(BiologicalAssetModel).order_by(BiologicalAssetModel.id)
        if biological_type:
            stmt = stmt.where(BiologicalAssetModel.biological_type == biological_type)
        if growth_stage:
            stmt = stmt.where(BiologicalAssetModel.growth_stage == growth_stage)
        return [self._bio_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Biological Provisions: conversion helpers ─────────────────────

    def _biop_to_domain(self, m: BiologicalProvisionModel) -> BiologicalProvision:
        b = BiologicalProvision(
            biological_asset_id=m.biological_asset_id,
            period=f"{m.provision_date.year}-{m.provision_date.month:02d}",
            provision_amount=m.amount,
            provision_type=m.provision_type,
            reason=m.reason,
            created_at=m.created_at,
        )
        b.id = m.id
        return b

    def _biop_to_model(self, d: BiologicalProvision) -> BiologicalProvisionModel:
        prov_date = date.today()
        if d.period:
            parts = d.period.split("-")
            y, mth = int(parts[0]), int(parts[1])
            prov_date = date(y, mth, 1)
        return BiologicalProvisionModel(
            biological_asset_id=d.biological_asset_id,
            provision_type=d.provision_type,
            provision_date=prov_date,
            amount=_vnd(d.provision_amount),
            reason=d.reason,
            created_by="system",
        )

    def create_biological_provision(self, provision: BiologicalProvision) -> Result:
        model = self._biop_to_model(provision)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._biop_to_domain(model))

    # ── GL Integration ───────────────────────────────────────────────

    def post_depreciation_gl(self, period: str, total_by_account: Dict[str, Decimal]) -> Result:
        accounts = {}
        for code, amt in total_by_account.items():
            coa = self.get_coa_account(code)
            if not coa:
                return Result.failure(AccountError(ErrorCodes.FA_GL_ACCOUNT_MISSING, account_code=code))
            accounts[code] = (coa, _vnd(amt))

        total_debit = sum(v[1] for v in accounts.values())
        cost_codes = [k for k in accounts.keys() if not k.startswith("214")]
        accum_code = [k for k in accounts.keys() if k.startswith("214")]
        if not accum_code:
            accum_code = ["2141"]
        total_cost = sum(accounts[k][1] for k in cost_codes)
        total_accum = sum(accounts[k][1] for k in accum_code)

        je = JournalEntryModel(
            journal_number=f"FA-DEP-{period}",
            transaction_date=_period_to_date(period),
            description=f"Khấu hao TSCĐ tháng {period}",
            period=period,
            is_posted=True,
            posted_date=datetime.now(timezone.utc),
            created_by="fa_system",
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(je)
        self.session.flush()

        for code in cost_codes:
            coa, amt = accounts[code]
            line = JournalLineModel(
                journal_entry_id=je.id,
                account_id=code,
                debit=amt,
                credit=Decimal("0"),
                period=period,
            )
            self.session.add(line)

        for code in accum_code:
            coa, amt = accounts[code]
            line = JournalLineModel(
                journal_entry_id=je.id,
                account_id=code,
                debit=Decimal("0"),
                credit=amt,
                period=period,
            )
            self.session.add(line)

        self.session.flush()
        return Result.success({"journal_id": je.id, "journal_number": je.journal_number})

    def get_coa_account(self, code: str) -> Optional[Any]:
        from sqlalchemy import select
        return self.session.execute(
            select(COAModel).where(COAModel.code == code)
        ).scalar_one_or_none()

    # ── Audit ────────────────────────────────────────────────────────

    def log_audit(self, asset_code: str, event_type: str, details: str, user: str) -> Result:
        return Result.success(None)


def _safe_int(val: Any) -> Optional[int]:
    if val is None:
        return None
    if isinstance(val, int):
        return val
    try:
        return int(val)
    except (ValueError, TypeError):
        return None
