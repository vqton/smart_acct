from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from flask import Flask
from sqlalchemy import create_engine
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
from infrastructure.models.coa_models import Base, COAModel
from infrastructure.models.fa_models import (
    FACategoryModel, FixedAssetModel, DepreciationRecordModel,
    FAAdjustmentModel, FADisposalModel, FAInventoryModel, FAInventoryLineModel,
    FATransferModel, FASparePartModel, FAComponentModel,
    BiologicalAssetModel, BiologicalProvisionModel,
    AssetStatusDB, InventoryStatusDB,
)
from infrastructure.models.gl_models import AccountingPeriodModel
from infrastructure.repositories.fa_repository import FARepository
from use_cases.fa import FAUseCases


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _ensure_coa_accounts(session, codes: list = None):
    """Create minimum COA accounts needed for GL posting in depreciation tests."""
    from sqlalchemy import select
    if codes is None:
        codes = ["6274", "2141"]
    for code in codes:
        existing = session.execute(
            select(COAModel).where(COAModel.code == code)
        ).scalar_one_or_none()
        if not existing:
            m = COAModel(
                code=code,
                name=f"Account {code}",
                account_type="expense" if code.startswith("6") else "asset",
                drcr_direction="debit" if code.startswith("6") else "credit",
                level=1,
            )
            session.add(m)
    session.flush()


def _make_category_data(code: str = "CAT-001", name: str = "May moc thiet bi", **kw) -> dict:
    data = {
        "code": code,
        "name": name,
        "asset_type": AssetType.TANGIBLE.value,
        "asset_classification": AssetClassification.MACHINERY_EQUIPMENT.value,
        "default_depreciation_method": DepreciationMethod.STRAIGHT_LINE.value,
        "default_useful_life_min": 60,
        "default_useful_life_max": 120,
        "description": "test category",
    }
    data.update(kw)
    return data


def _make_asset_data(category_id: int, code: str = "FA-001", cost: Decimal = Decimal("100000000"), **kw) -> dict:
    data = {
        "code": code,
        "name": "May san xuat",
        "category_id": category_id,
        "asset_type": AssetType.TANGIBLE.value,
        "asset_classification": AssetClassification.MACHINERY_EQUIPMENT.value,
        "original_cost": cost,
        "useful_life_months": 60,
        "depreciation_method": DepreciationMethod.STRAIGHT_LINE.value,
        "acquisition_date": date(2026, 1, 1),
        "in_use_date": date(2026, 1, 15),
        "department_id": "1",
        "location": "Phan xuong A",
        "status": AssetStatus.ACTIVE.value,
        "fund_source": FundSource.OWNERS_EQUITY.value,
        "use_type": UseType.PRODUCTION.value,
        "supplier": "NCC ABC",
        "invoice_ref": "HD-001",
        "description": "test asset",
        "created_by": "test_user",
    }
    data.update(kw)
    return data


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    yield sess
    sess.close()


@pytest.fixture
def repo(session):
    return FARepository(session)


@pytest.fixture
def uc(session):
    return FAUseCases(session)


# ── UC-FA-01: Category Management ──────────────────────────────────────

class TestFACategories:
    def test_create_category(self, uc):
        result = uc.create_category(_make_category_data())
        assert result.is_success()
        c = result.get_data()
        assert c.code == "CAT-001"
        assert c.name == "May moc thiet bi"
        assert c.is_active is True

    def test_create_category_duplicate_code(self, uc):
        uc.create_category(_make_category_data(code="CAT-001"))
        result = uc.create_category(_make_category_data(code="CAT-001", name="Duplicate"))
        assert result.is_failure()

    def test_get_category(self, uc):
        created = uc.create_category(_make_category_data(code="CAT-002", name="Phuong tien van tai"))
        c_id = created.get_data().id
        result = uc.get_category(c_id)
        assert result.is_success()
        assert result.get_data().code == "CAT-002"

    def test_list_categories(self, uc):
        uc.create_category(_make_category_data(code="CAT-A", name="Category A"))
        uc.create_category(_make_category_data(code="CAT-B", name="Category B"))
        result = uc.list_categories()
        assert result.is_success()
        assert len(result.get_data()) >= 2

    def test_delete_category_no_assets(self, uc):
        created = uc.create_category(_make_category_data(code="CAT-DEL"))
        c_id = created.get_data().id
        result = uc.delete_category(c_id)
        assert result.is_success()

    def test_delete_category_with_assets_fails(self, uc, repo):
        cat = uc.create_category(_make_category_data(code="CAT-HAS")).get_data()
        asset_data = _make_asset_data(cat.id, code="FA-HAS")
        uc.register_asset(asset_data)
        result = uc.delete_category(cat.id)
        assert result.is_failure()


# ── UC-FA-02: Fixed Asset Registration ─────────────────────────────────

class TestFARegistration:
    def test_register_asset_valid(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-REG")).get_data()
        data = _make_asset_data(cat.id, code="FA-REG-01",
                                depreciation_method=DepreciationMethod.STRAIGHT_LINE.value)
        result = uc.register_asset(data)
        assert result.is_success()
        a = result.get_data()
        assert a.code == "FA-REG-01"
        assert a.original_cost == Decimal("100000000")
        assert a.status == AssetStatus.ACTIVE
        assert a.carrying_amount == a.original_cost

    def test_register_asset_below_30m_threshold(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-COST")).get_data()
        result = uc.register_asset(_make_asset_data(cat.id, code="FA-COST",
                                                     cost=Decimal("25000000")))
        assert result.is_success()

    def test_register_asset_useful_life_below_12_fails(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-LIFE")).get_data()
        data = _make_asset_data(cat.id, code="FA-LIFE", useful_life_months=6)
        result = uc.register_asset(data)
        assert result.is_failure()

    def test_register_asset_invalid_category_fails(self, uc):
        result = uc.register_asset(_make_asset_data(999, code="FA-BAD"))
        assert result.is_failure()

    def test_update_asset_metadata(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-UPD")).get_data()
        created = uc.register_asset(_make_asset_data(cat.id, code="FA-UPD-01")).get_data()
        result = uc.update_asset(created.id, name="May san xuat cap nhat", location="Phan xuong B")
        assert result.is_success()
        updated = result.get_data()
        assert updated.name == "May san xuat cap nhat"
        assert updated.location == "Phan xuong B"

    def test_search_assets(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-SRC")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-SRC-01", name="May tien CNC"))
        uc.register_asset(_make_asset_data(cat.id, code="FA-SRC-02", name="May phay"))
        result = uc.search_assets("tien")
        assert result.is_success()
        assert len(result.get_data()) >= 1


# ── UC-FA-03: Depreciation Engine ──────────────────────────────────────

class TestFADepreciation:
    def test_run_depreciation_straight_line(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-DEP-SL")).get_data()
        cost = Decimal("120000000")
        life = 60
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DEP-SL",
                                                    cost=cost, useful_life_months=life)).get_data()
        result = uc.run_depreciation("2026-06")
        assert result.is_success()
        data = result.get_data()
        assert data["count"] == 1
        expected_monthly = _vnd(cost / Decimal(life))
        assert _vnd(Decimal(data["total_amount"])) == expected_monthly

    def test_run_depreciation_declining_balance(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-DEP-DB")).get_data()
        cost = Decimal("100000000")
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DEP-DB",
                                                    cost=cost, useful_life_months=60,
                                                    depreciation_method=DepreciationMethod.DECLINING_BALANCE.value,
                                                    override_method=True)).get_data()
        result = uc.run_depreciation("2026-07")
        assert result.is_success()
        data = result.get_data()
        assert data["count"] == 1
        assert _vnd(Decimal(data["total_amount"])) > Decimal("0")

    def test_run_depreciation_units_of_production(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-DEP-UOP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DEP-UOP",
                                                    cost=Decimal("50000000"), useful_life_months=60,
                                                    depreciation_method=DepreciationMethod.UNITS_OF_PRODUCTION.value,
                                                    override_method=True)).get_data()
        result = uc.run_depreciation("2026-08")
        assert result.is_success()
        data = result.get_data()
        assert data["count"] == 1

    def test_run_depreciation_twice_skips(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-DEP-2X")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DEP-2X")).get_data()
        uc.run_depreciation("2026-09")
        result = uc.run_depreciation("2026-09")
        assert result.is_failure()

    def test_get_depreciation_for_period(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-DEP-PER")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-DEP-PER")).get_data()
        uc.run_depreciation("2026-10")
        result = uc.get_depreciation_for_period("2026-10")
        assert result.is_success()
        assert len(result.get_data()) >= 1

    def test_get_asset_depreciation_records(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-DEP-REC")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DEP-REC")).get_data()
        uc.run_depreciation("2026-11")
        result = uc.get_asset_depreciation(asset.id)
        assert result.is_success()
        assert len(result.get_data()) >= 1
        assert result.get_data()[0].asset_id == asset.id


# ── UC-FA-04: Asset Adjustments ────────────────────────────────────────

class TestFAAdjustments:
    def test_upgrade_asset(self, uc):
        """Upgrade: avoids new_cost in data to match FAAdjustment constructor signature."""
        cat = uc.create_category(_make_category_data(code="CAT-ADJ-UP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-ADJ-UP",
                                                    cost=Decimal("100000000"))).get_data()
        result = uc.adjust_asset(asset.id, {
            "adjustment_type": FAAdjustmentType.UPGRADE.value,
            "amount": Decimal("20000000"),
            "reason": "Nang cap may moc",
            "effective_date": date(2026, 6, 1),
            "created_by": "test",
        })
        assert result.is_success()
        adj = result.get_data()
        assert adj.adjustment_type == FAAdjustmentType.UPGRADE

    def test_impairment(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-ADJ-IM")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-ADJ-IM",
                                                    cost=Decimal("100000000"))).get_data()
        result = uc.adjust_asset(asset.id, {
            "adjustment_type": FAAdjustmentType.IMPAIRMENT.value,
            "amount": Decimal("10000000"),
            "reason": "Hao mon binh thuong",
            "effective_date": date(2026, 6, 1),
            "created_by": "test",
        })
        assert result.is_success()
        updated = uc.get_asset(asset.id).get_data()
        assert updated.original_cost == Decimal("90000000")

    def test_get_adjustments(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-ADJ-GET")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-ADJ-GET")).get_data()
        uc.adjust_asset(asset.id, {
            "adjustment_type": FAAdjustmentType.UPGRADE.value,
            "amount": Decimal("5000000"),
            "reason": "Nang cap",
            "effective_date": date(2026, 7, 1),
            "created_by": "test",
        })
        adjustments = uc.repo.get_adjustments(asset.id)
        assert len(adjustments) >= 1


# ── UC-FA-05: Asset Transfer ──────────────────────────────────────────

class TestFATransfer:
    def test_transfer_between_departments(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-TRF-DEPT")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-TRF-DEPT",
                                                    department_id="1")).get_data()
        result = uc.transfer_asset(asset.id, {
            "from_department_id": "1",
            "to_department_id": "2",
            "effective_date": date(2026, 6, 1),
            "reason": "Dieu chuyen sang phong ban khac",
            "created_by": "test",
        })
        assert result.is_success()
        t = result.get_data()
        assert t.from_department_id == "1"
        assert t.to_department_id == "2"

    def test_transfer_between_locations(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-TRF-LOC")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-TRF-LOC",
                                                    department_id="1",
                                                    location="Kho A")).get_data()
        result = uc.transfer_asset(asset.id, {
            "from_department_id": "1",
            "to_department_id": "2",
            "from_location": "Kho A",
            "to_location": "Kho B",
            "effective_date": date(2026, 6, 15),
            "reason": "Chuyen kho",
            "created_by": "test",
        })
        assert result.is_success()
        t = result.get_data()
        assert t.from_location == "Kho A"
        assert t.to_location == "Kho B"
        updated = uc.get_asset(asset.id).get_data()
        assert updated.department_id == "2"


# ── UC-FA-06: Asset Disposal ──────────────────────────────────────────

class TestFADisposal:
    def test_sale_disposal_gain(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-DISP-G")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DISP-G",
                                                    cost=Decimal("100000000"))).get_data()
        result = uc.dispose_asset(asset.id, {
            "disposal_type": DisposalType.SALE.value,
            "disposal_date": date(2026, 12, 1),
            "proceeds": Decimal("120000000"),
            "reason": "Ban thanh ly co lai",
            "buyer_info": "Cong ty Mua",
            "approved_by": "KTT",
            "created_by": "test",
        })
        assert result.is_success()
        d = result.get_data()
        assert d.disposal_type == DisposalType.SALE
        assert d.gain_loss > Decimal("0")

    def test_sale_disposal_loss(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-DISP-L")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DISP-L",
                                                    cost=Decimal("100000000"))).get_data()
        result = uc.dispose_asset(asset.id, {
            "disposal_type": DisposalType.SALE.value,
            "disposal_date": date(2026, 12, 1),
            "proceeds": Decimal("80000000"),
            "reason": "Ban thanh ly lo",
            "buyer_info": "Cong ty Mua",
            "approved_by": "KTT",
            "created_by": "test",
        })
        assert result.is_success()
        d = result.get_data()
        assert d.gain_loss < Decimal("0")

    def test_liquidation_disposal(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-DISP-LIQ")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-DISP-LIQ",
                                                    cost=Decimal("50000000"))).get_data()
        result = uc.dispose_asset(asset.id, {
            "disposal_type": DisposalType.LIQUIDATION.value,
            "disposal_date": date(2026, 12, 15),
            "proceeds": Decimal("0"),
            "reason": "Thanh ly het gia tri su dung",
            "approved_by": "KTT",
            "created_by": "test",
        })
        assert result.is_success()
        d = result.get_data()
        assert d.disposal_type == DisposalType.LIQUIDATION
        assert d.gain_loss < Decimal("0")


# ── UC-FA-07: FA Inventory ────────────────────────────────────────────

class TestFAInventory:
    def test_create_inventory(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-INV")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-INV-01",
                                                    department_id="1")).get_data()
        result = uc.create_inventory({
            "inventory_date": date(2026, 12, 31),
            "department_id": "1",
            "notes": "Kiem ke cuoi nam",
            "created_by": "test",
            "lines": [
                {"asset_id": asset.id, "physical_quantity": 1},
            ],
        })
        assert result.is_success()
        inv = result.get_data()
        assert inv.inventory_date == date(2026, 12, 31)

    def test_add_inventory_line(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-INV-LN")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-INV-LN",
                                                    department_id="1")).get_data()
        inv = uc.create_inventory({
            "inventory_date": date(2026, 12, 31),
            "department_id": "1",
            "created_by": "test",
            "lines": [],
        }).get_data()
        result = uc.add_inventory_line(inv.id, {
            "asset_id": asset.id,
            "physical_quantity": 1,
        })
        assert result.is_success()
        line = result.get_data()
        assert line.asset_id == asset.id

    def test_list_inventories(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-INV-LST")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-INV-LST",
                                            department_id="1")).get_data()
        uc.create_inventory({
            "inventory_date": date(2026, 12, 31),
            "department_id": "1",
            "created_by": "test",
            "lines": [],
        })
        result = uc.list_inventories()
        assert result.is_success()
        assert len(result.get_data()) >= 1


# ── UC-FA-08: Spare Parts & Components ────────────────────────────────

class TestFASpareParts:
    def test_add_spare_part(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-SP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-SP-01")).get_data()
        result = uc.add_spare_part(asset.id, {
            "code": "SP-001",
            "name": "Vong bi",
            "quantity": 5,
            "unit": "cai",
            "value": Decimal("500000"),
        })
        assert result.is_success()
        sp = result.get_data()
        assert sp.code == "SP-001"
        assert sp.quantity == 5

    def test_get_spare_parts(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-SP-GET")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-SP-GET")).get_data()
        uc.add_spare_part(asset.id, {"code": "SP-002", "name": "O bi", "quantity": 2, "unit": "cai", "value": Decimal("200000")})
        result = uc.get_spare_parts(asset.id)
        assert result.is_success()
        assert len(result.get_data()) >= 1

    def test_add_component(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-COMP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-COMP-01")).get_data()
        result = uc.add_component(asset.id, {
            "name": "Dong co dien",
            "original_cost": Decimal("15000000"),
            "useful_life_months": 36,
        })
        assert result.is_success()
        comp = result.get_data()
        assert comp.name == "Dong co dien"

    def test_get_components(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-COMP-GET")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-COMP-GET")).get_data()
        uc.add_component(asset.id, {"name": "Component A", "original_cost": Decimal("5000000")})
        result = uc.get_components(asset.id)
        assert result.is_success()
        assert len(result.get_data()) >= 1


# ── UC-FA-09: Biological Assets ───────────────────────────────────────

class TestFABiological:
    def test_register_biological_asset(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-BIO")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-BIO-01",
                                                    asset_type=AssetType.BIOLOGICAL.value,
                                                    asset_classification=AssetClassification.PERENNIAL_PLANTS_LIVESTOCK.value)).get_data()
        result = uc.register_biological_asset(asset.id, {
            "biological_type": BiologicalType.PERIODIC_PRODUCER_LONG_TERM.value,
            "quantity": Decimal("100"),
            "unit": "cay",
            "planting_date": date(2026, 1, 1),
        })
        assert result.is_success()
        bio = result.get_data()
        assert bio.unit == "cay"

    def test_create_biological_provision(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-BIO-PROV")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-BIO-PROV",
                                                    asset_type=AssetType.BIOLOGICAL.value,
                                                    asset_classification=AssetClassification.PERENNIAL_PLANTS_LIVESTOCK.value)).get_data()
        bio = uc.register_biological_asset(asset.id, {
            "biological_type": BiologicalType.PERIODIC_PRODUCER_LONG_TERM.value,
            "quantity": Decimal("100"),
            "unit": "cay",
            "planting_date": date(2026, 1, 1),
        }).get_data()
        result = uc.create_biological_provision(bio.id, {
            "period": "2026-12",
            "provision_amount": Decimal("5000000"),
            "provision_type": ProvisionType.NEW.value,
            "reason": "Du phong giam gia cay trong",
        })
        assert result.is_success()
        prov = result.get_data()
        assert prov.provision_amount == Decimal("5000000")

    def test_list_biological_assets(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-BIO-LST")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-BIO-LST",
                                                    asset_type=AssetType.BIOLOGICAL.value,
                                                    asset_classification=AssetClassification.PERENNIAL_PLANTS_LIVESTOCK.value)).get_data()
        uc.register_biological_asset(asset.id, {
            "biological_type": BiologicalType.PERIODIC_PRODUCER_LONG_TERM.value,
            "quantity": Decimal("50"),
            "unit": "con",
            "planting_date": date(2026, 1, 1),
        })
        result = uc.list_biological_assets()
        assert result.is_success()
        assert len(result.get_data()) >= 1


# ── UC-FA-10: FA Reports ──────────────────────────────────────────────

class TestFAReports:
    def test_asset_register_report(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-REP-REG")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-REP-REG")).get_data()
        result = uc.get_asset_register_report()
        assert result.is_success()
        data = result.get_data()
        assert data["count"] >= 1
        assert "totals" in data

    def test_depreciation_schedule_report(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-REP-DEP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-REP-DEP")).get_data()
        uc.run_depreciation("2026-06")
        result = uc.get_depreciation_schedule_report(asset_id=asset.id)
        assert result.is_success()
        data = result.get_data()
        assert len(data["rows"]) >= 1

    def test_asset_increase_decrease_report(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-REP-ID")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-REP-ID")).get_data()
        result = uc.get_asset_increase_decrease_report("2026-01-01", "2026-12-31")
        assert result.is_success()
        data = result.get_data()
        assert "increases" in data
        assert "decreases" in data

    def test_asset_status_summary(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-REP-SS")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-REP-SS")).get_data()
        result = uc.get_asset_status_summary()
        assert result.is_success()
        data = result.get_data()
        assert data["total_assets"] >= 1
        assert "summary" in data


# ── UC-FA-11: TT 99/2025 Migration ─────────────────────────────────────

class TestFATT99Migration:
    def test_dry_run_migration(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-TT99")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-TT99-01")).get_data()
        result = uc.run_tt99_migration(dry_run=True)
        assert result.is_success()
        data = result.get_data()
        assert data["dry_run"] is True

    def test_live_migration(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-TT99-LIVE")).get_data()
        uc.register_asset(_make_asset_data(cat.id, code="FA-TT99-LIVE-01",
                                            fund_source=FundSource.GOVERNMENT_GRANT.value)).get_data()
        result = uc.run_tt99_migration(dry_run=False, user="admin")
        assert result.is_success()
        data = result.get_data()
        assert data["dry_run"] is False
        assert "executed_by" in data


# ── UC-FA-12: Depreciation Suspension ─────────────────────────────────

class TestFASuspension:
    def test_suspend_depreciation(self, uc, session):
        cat = uc.create_category(_make_category_data(code="CAT-SUSP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-SUSP")).get_data()
        period = AccountingPeriodModel(period="2026-06", is_closed=False)
        session.add(period)
        session.flush()
        result = uc.suspend_depreciation(asset.id, {
            "reason": "Bao tri dai han",
            "start_period": "2026-06",
            "end_period": "2026-08",
            "approved_by": "KTT",
            "created_by": "test",
        })
        assert result.is_success()
        updated = uc.get_asset(asset.id).get_data()
        assert updated.status == AssetStatus.SUSPENDED

    def test_resume_depreciation(self, uc, session):
        cat = uc.create_category(_make_category_data(code="CAT-RES")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-RES")).get_data()
        period = AccountingPeriodModel(period="2026-09", is_closed=False)
        session.add(period)
        session.flush()
        uc.suspend_depreciation(asset.id, {
            "reason": "Bao tri",
            "start_period": "2026-06",
            "end_period": "2026-08",
            "approved_by": "KTT",
            "created_by": "test",
        })
        result = uc.resume_depreciation(asset.id, {
            "reason": "Da sua xong",
            "resume_period": "2026-09",
            "suspension_start_period": "2026-06",
            "approved_by": "KTT",
            "created_by": "test",
        })
        assert result.is_success()
        updated = uc.get_asset(asset.id).get_data()
        assert updated.status == AssetStatus.ACTIVE

    def test_suspend_without_reason_fails(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-SUSP-NR")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-SUSP-NR")).get_data()
        result = uc.suspend_depreciation(asset.id, {
            "reason": "",
            "start_period": "2026-06",
            "end_period": "2026-08",
            "approved_by": "",
        })
        assert result.is_failure()


# ── Edge Cases ─────────────────────────────────────────────────────────

class TestFAEdgeCases:
    def test_empty_list_returns(self, uc):
        result = uc.list_assets()
        assert result.is_success()
        assert len(result.get_data()) == 0

        result = uc.list_categories()
        assert result.is_success()
        assert len(result.get_data()) == 0

    def test_depreciation_closed_period_fails(self, uc, session):
        cat = uc.create_category(_make_category_data(code="CAT-EDGE-DEP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-EDGE-DEP")).get_data()
        period = AccountingPeriodModel(period="2026-06", is_closed=True)
        session.add(period)
        session.flush()
        result = uc.run_depreciation("2026-06")
        assert result.is_failure()

    def test_dispose_already_disposed_fails(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-EDGE-DISP")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-EDGE-DISP")).get_data()
        uc.dispose_asset(asset.id, {
            "disposal_type": DisposalType.LIQUIDATION.value,
            "disposal_date": date(2026, 12, 1),
            "proceeds": Decimal("0"),
            "reason": "Thanh ly",
            "approved_by": "KTT",
            "created_by": "test",
        })
        result = uc.dispose_asset(asset.id, {
            "disposal_type": DisposalType.LIQUIDATION.value,
            "disposal_date": date(2026, 12, 15),
            "proceeds": Decimal("0"),
            "reason": "Thu hoi",
            "approved_by": "KTT",
            "created_by": "test",
        })
        assert result.is_failure()

    def test_get_nonexistent_asset_fails(self, uc):
        result = uc.get_asset(9999)
        assert result.is_failure()

    def test_update_cost_after_depreciation_fails(self, uc, session):
        _ensure_coa_accounts(session)
        cat = uc.create_category(_make_category_data(code="CAT-EDGE-COST")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-EDGE-COST")).get_data()
        uc.run_depreciation("2026-06")
        result = uc.update_asset(asset.id, original_cost=Decimal("150000000"))
        assert result.is_failure()

    def test_transfer_same_department_fails(self, uc):
        cat = uc.create_category(_make_category_data(code="CAT-EDGE-TRF")).get_data()
        asset = uc.register_asset(_make_asset_data(cat.id, code="FA-EDGE-TRF",
                                                    department_id="1")).get_data()
        result = uc.transfer_asset(asset.id, {
            "from_department_id": "1",
            "to_department_id": "1",
            "effective_date": date(2026, 6, 1),
            "reason": "Test same dept",
            "created_by": "test",
        })
        assert result.is_failure()
