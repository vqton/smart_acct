from decimal import Decimal
from datetime import date, datetime, timezone
import pytest
from pydantic import ValidationError as PydanticValidationError

from domain.fa import (
    AssetType, DepreciationMethod, AssetStatus, DisposalType, AdjustmentType,
    BiologicalType, GrowthStage, AssetClassification, FundSource, UseType,
    InventoryStatus, ProvisionType,
    FACategory, FixedAsset, DepreciationRecord, FAAdjustment, FADisposal,
    FAInventory, FAInventoryLine, FATransfer, FASparePart, FAComponent,
    BiologicalAsset, BiologicalProvision, DepreciationConfig,
)
from domain.common import ValidationError as DomainValidationError


# ── FACategory Tests ──────────────────────────────────────────────────────

class TestFACategory:
    def test_valid_category_all_fields(self):
        cat = FACategory(
            code="TSCD-HH",
            name="Tai san co dinh huu hinh",
            asset_type=AssetType.TANGIBLE,
            asset_classification=AssetClassification.MACHINERY_EQUIPMENT,
            default_depreciation_method=DepreciationMethod.STRAIGHT_LINE,
            default_useful_life_min=60,
            default_useful_life_max=120,
            description="May moc thiet bi",
        )
        assert cat.code == "TSCD-HH"
        assert cat.is_active is True
        assert cat.default_useful_life_min == 60
        assert cat.default_useful_life_max == 120

    def test_valid_category_minimal(self):
        cat = FACategory(
            code="TSCD-VH",
            name="Tai san co dinh vo hinh",
            asset_type=AssetType.INTANGIBLE,
            asset_classification=AssetClassification.OTHER,
        )
        assert cat.default_depreciation_method == DepreciationMethod.STRAIGHT_LINE
        assert cat.is_active is True
        assert cat.description is None

    def test_code_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FACategory(
                code="", name="Test",
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
            )

    def test_code_whitespace_only_raises(self):
        with pytest.raises(DomainValidationError):
            FACategory(
                code="   ", name="Test",
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
            )

    def test_code_stripped(self):
        cat = FACategory(
            code="  ABC-123  ", name="Test",
            asset_type=AssetType.TANGIBLE,
            asset_classification=AssetClassification.OTHER,
        )
        assert cat.code == "ABC-123"

    def test_code_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FACategory(
                code="A" * 51, name="Test",
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
            )

    def test_name_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FACategory(
                code="TEST", name="T" * 201,
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
            )

    def test_description_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FACategory(
                code="TEST", name="Test",
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
                description="D" * 501,
            )

    def test_default_useful_life_min_zero_raises(self):
        with pytest.raises(PydanticValidationError):
            FACategory(
                code="TEST", name="Test",
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
                default_useful_life_min=0,
            )

    def test_default_useful_life_max_zero_raises(self):
        with pytest.raises(PydanticValidationError):
            FACategory(
                code="TEST", name="Test",
                asset_type=AssetType.TANGIBLE,
                asset_classification=AssetClassification.OTHER,
                default_useful_life_max=0,
            )

    def test_all_asset_types_accepted(self):
        for at in AssetType:
            cat = FACategory(
                code=f"TYPE-{at.value}", name=at.value,
                asset_type=at,
                asset_classification=AssetClassification.OTHER,
            )
            assert cat.asset_type == at

    def test_all_asset_classifications_accepted(self):
        for ac in AssetClassification:
            cat = FACategory(
                code=f"CLS-{ac.value}", name=ac.value,
                asset_type=AssetType.TANGIBLE,
                asset_classification=ac,
            )
            assert cat.asset_classification == ac

    def test_is_active_defaults_true(self):
        cat = FACategory(
            code="ACTIVE", name="Active Cat",
            asset_type=AssetType.TANGIBLE,
            asset_classification=AssetClassification.OTHER,
        )
        assert cat.is_active is True

    def test_is_active_set_false(self):
        cat = FACategory(
            code="INACTIVE", name="Inactive Cat",
            asset_type=AssetType.TANGIBLE,
            asset_classification=AssetClassification.OTHER,
            is_active=False,
        )
        assert cat.is_active is False


# ── FixedAsset Tests ─────────────────────────────────────────────────────

class TestFixedAsset:
    """Helper to build a valid FixedAsset with overridable kwargs."""

    @staticmethod
    def make(**kw):
        params = dict(
            code="TS0001",
            name="May tinh tien",
            category_id=1,
            asset_type=AssetType.TANGIBLE,
            asset_classification=AssetClassification.MACHINERY_EQUIPMENT,
            original_cost=Decimal("50000000"),
            accumulated_depreciation=Decimal("10000000"),
            residual_value=Decimal("5000000"),
            useful_life_months=60,
            acquisition_date=date(2024, 1, 1),
            in_use_date=date(2024, 2, 1),
        )
        params.update(kw)
        return FixedAsset(**params)

    def test_valid_asset(self):
        asset = self.make()
        assert asset.code == "TS0001"
        assert asset.name == "May tinh tien"
        assert asset.category_id == 1
        assert asset.asset_type == AssetType.TANGIBLE
        assert asset.original_cost == Decimal("50000000.00")
        assert asset.status == AssetStatus.ACTIVE
        assert asset.fund_source == FundSource.OWNERS_EQUITY
        assert asset.use_type == UseType.PRODUCTION
        assert asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE

    def test_code_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(code="")

    def test_code_whitespace_only_raises(self):
        with pytest.raises(DomainValidationError):
            self.make(code="   ")

    def test_code_stripped(self):
        asset = self.make(code="  TS-ABC  ")
        assert asset.code == "TS-ABC"

    def test_code_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(code="A" * 51)

    def test_name_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(name="N" * 201)

    def test_original_cost_zero_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(original_cost=Decimal("0"))

    def test_original_cost_negative_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(original_cost=Decimal("-1000"))

    def test_original_cost_quantized(self):
        asset = self.make(original_cost=Decimal("50000000.123"))
        assert asset.original_cost == Decimal("50000000.12")

    def test_accumulated_depreciation_quantized(self):
        asset = self.make(accumulated_depreciation=Decimal("10000000.456"))
        assert asset.accumulated_depreciation == Decimal("10000000.46")

    def test_residual_value_quantized(self):
        asset = self.make(residual_value=Decimal("5000000.789"))
        assert asset.residual_value == Decimal("5000000.79")

    def test_useful_life_below_minimum_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(useful_life_months=11)

    def test_useful_life_at_minimum(self):
        asset = self.make(useful_life_months=12)
        assert asset.useful_life_months == 12

    def test_in_use_before_acquisition_raises(self):
        with pytest.raises(DomainValidationError):
            self.make(
                acquisition_date=date(2024, 3, 1),
                in_use_date=date(2024, 2, 1),
            )

    def test_in_use_equals_acquisition_ok(self):
        asset = self.make(
            acquisition_date=date(2024, 2, 1),
            in_use_date=date(2024, 2, 1),
        )
        assert asset.in_use_date == asset.acquisition_date

    def test_carrying_amount_positive_depreciation(self):
        asset = self.make(
            original_cost=Decimal("100000000"),
            accumulated_depreciation=Decimal("30000000"),
        )
        assert asset.carrying_amount == Decimal("70000000.00")

    def test_carrying_amount_no_depreciation(self):
        asset = self.make(
            original_cost=Decimal("80000000"),
            accumulated_depreciation=Decimal("0"),
        )
        assert asset.carrying_amount == Decimal("80000000.00")

    def test_carrying_amount_fully_depreciated(self):
        asset = self.make(
            original_cost=Decimal("50000000"),
            accumulated_depreciation=Decimal("50000000"),
            residual_value=Decimal("0"),
        )
        assert asset.carrying_amount == Decimal("0.00")

    def test_carrying_amount_quantized(self):
        asset = self.make(
            original_cost=Decimal("50000000.123"),
            accumulated_depreciation=Decimal("10000000.456"),
        )
        assert asset.carrying_amount == Decimal("39999999.66")

    def test_status_default_active(self):
        asset = self.make()
        assert asset.status == AssetStatus.ACTIVE

    def test_all_status_values_accepted(self):
        for status in AssetStatus:
            asset = self.make(status=status)
            assert asset.status == status

    def test_all_fund_source_values_accepted(self):
        for fs in FundSource:
            asset = self.make(fund_source=fs)
            assert asset.fund_source == fs

    def test_all_use_type_values_accepted(self):
        for ut in UseType:
            asset = self.make(use_type=ut)
            assert asset.use_type == ut

    def test_all_depreciation_methods_accepted(self):
        for dm in DepreciationMethod:
            asset = self.make(depreciation_method=dm)
            assert asset.depreciation_method == dm

    def test_department_id_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(department_id="D" * 51)

    def test_location_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(location="L" * 201)

    def test_supplier_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(supplier="S" * 201)

    def test_invoice_ref_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(invoice_ref="I" * 101)

    def test_description_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(description="D" * 501)

    def test_created_by_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            self.make(created_by="C" * 101)

    def test_original_cost_gt_zero_passes(self):
        asset = self.make(original_cost=Decimal("30000000"))
        assert asset.original_cost == Decimal("30000000.00")

    def test_original_cost_below_30m_also_valid(self):
        asset = self.make(original_cost=Decimal("5000000"))
        assert asset.original_cost == Decimal("5000000.00")

    def test_optional_fields_none(self):
        asset = self.make(
            department_id=None,
            location=None,
            supplier=None,
            invoice_ref=None,
            description=None,
            created_by=None,
        )
        assert asset.department_id is None
        assert asset.location is None

    def test_string_field_max_length_boundary(self):
        asset = self.make(
            department_id="D" * 50,
            location="L" * 200,
            supplier="S" * 200,
            invoice_ref="I" * 100,
            description="D" * 500,
            created_by="C" * 100,
        )
        assert len(asset.department_id) == 50
        assert len(asset.location) == 200


# ── DepreciationRecord Tests ─────────────────────────────────────────────

class TestDepreciationRecord:
    def test_valid_record(self):
        rec = DepreciationRecord(
            asset_id=1,
            period="2024-06",
            depreciation_amount=Decimal("1000000"),
            accumulated_total=Decimal("6000000"),
            nbv=Decimal("44000000"),
        )
        assert rec.asset_id == 1
        assert rec.period == "2024-06"
        assert rec.is_posted is False

    def test_valid_record_posted(self):
        rec = DepreciationRecord(
            asset_id=1,
            period="2024-06",
            depreciation_amount=Decimal("1000000"),
            accumulated_total=Decimal("6000000"),
            nbv=Decimal("44000000"),
            is_posted=True,
        )
        assert rec.is_posted is True

    def test_period_format_invalid_no_hyphen_raises(self):
        with pytest.raises(PydanticValidationError):
            DepreciationRecord(
                asset_id=1,
                period="202406",
                depreciation_amount=Decimal("1000000"),
                accumulated_total=Decimal("6000000"),
                nbv=Decimal("44000000"),
            )

    def test_period_format_invalid_wrong_delimiter_raises(self):
        with pytest.raises(PydanticValidationError):
            DepreciationRecord(
                asset_id=1,
                period="2024/06",
                depreciation_amount=Decimal("1000000"),
                accumulated_total=Decimal("6000000"),
                nbv=Decimal("44000000"),
            )

    def test_period_format_letters_raises(self):
        with pytest.raises(PydanticValidationError):
            DepreciationRecord(
                asset_id=1,
                period="abcd-ef",
                depreciation_amount=Decimal("1000000"),
                accumulated_total=Decimal("6000000"),
                nbv=Decimal("44000000"),
            )

    def test_period_format_single_digit_month(self):
        with pytest.raises(PydanticValidationError):
            DepreciationRecord(
                asset_id=1,
                period="2024-1",
                depreciation_amount=Decimal("1000000"),
                accumulated_total=Decimal("6000000"),
                nbv=Decimal("44000000"),
            )

    def test_amounts_quantized(self):
        rec = DepreciationRecord(
            asset_id=1,
            period="2024-06",
            depreciation_amount=Decimal("1000000.123"),
            accumulated_total=Decimal("6000000.456"),
            nbv=Decimal("44000000.789"),
        )
        assert rec.depreciation_amount == Decimal("1000000.12")
        assert rec.accumulated_total == Decimal("6000000.46")
        assert rec.nbv == Decimal("44000000.79")


# ── FAAdjustment Tests ───────────────────────────────────────────────────

class TestFAAdjustment:
    def test_valid_adjustment(self):
        adj = FAAdjustment(
            asset_id=1,
            adjustment_type=AdjustmentType.UPGRADE,
            amount=Decimal("10000000"),
            previous_cost=Decimal("50000000"),
            new_cost=Decimal("60000000"),
            reason="Nang cap may moc",
            effective_date=date(2026, 6, 15),
        )
        assert adj.adjustment_type == AdjustmentType.UPGRADE
        assert adj.amount == Decimal("10000000.00")
        assert adj.document_ref is None

    def test_all_adjustment_types(self):
        for adj_type in AdjustmentType:
            adj = FAAdjustment(
                asset_id=1,
                adjustment_type=adj_type,
                amount=Decimal("5000000"),
                previous_cost=Decimal("50000000"),
                new_cost=Decimal("55000000"),
                reason=f"Test {adj_type.value}",
                effective_date=date(2026, 6, 15),
            )
            assert adj.adjustment_type == adj_type

    def test_reason_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FAAdjustment(
                asset_id=1,
                adjustment_type=AdjustmentType.UPGRADE,
                amount=Decimal("5000000"),
                previous_cost=Decimal("50000000"),
                new_cost=Decimal("55000000"),
                reason="",
                effective_date=date(2026, 6, 15),
            )

    def test_reason_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FAAdjustment(
                asset_id=1,
                adjustment_type=AdjustmentType.UPGRADE,
                amount=Decimal("5000000"),
                previous_cost=Decimal("50000000"),
                new_cost=Decimal("55000000"),
                reason="R" * 501,
                effective_date=date(2026, 6, 15),
            )

    def test_amounts_quantized(self):
        adj = FAAdjustment(
            asset_id=1,
            adjustment_type=AdjustmentType.UPGRADE,
            amount=Decimal("10000000.123"),
            previous_cost=Decimal("50000000.456"),
            new_cost=Decimal("60000000.579"),
            reason="Nang cap",
            effective_date=date(2026, 6, 15),
        )
        assert adj.amount == Decimal("10000000.12")
        assert adj.previous_cost == Decimal("50000000.46")
        assert adj.new_cost == Decimal("60000000.58")

    def test_negative_amount_accepted(self):
        adj = FAAdjustment(
            asset_id=1,
            adjustment_type=AdjustmentType.PARTIAL_DISMANTLE,
            amount=Decimal("-5000000"),
            previous_cost=Decimal("50000000"),
            new_cost=Decimal("45000000"),
            reason="Thai bo mot phan",
            effective_date=date(2026, 6, 15),
        )
        assert adj.amount == Decimal("-5000000.00")
        assert adj.new_cost == Decimal("45000000.00")

    def test_with_document_ref(self):
        adj = FAAdjustment(
            asset_id=1,
            adjustment_type=AdjustmentType.UPGRADE,
            amount=Decimal("10000000"),
            previous_cost=Decimal("50000000"),
            new_cost=Decimal("60000000"),
            reason="Nang cap",
            document_ref="BB-2026-001",
            effective_date=date(2026, 6, 15),
        )
        assert adj.document_ref == "BB-2026-001"

    def test_document_ref_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FAAdjustment(
                asset_id=1,
                adjustment_type=AdjustmentType.UPGRADE,
                amount=Decimal("5000000"),
                previous_cost=Decimal("50000000"),
                new_cost=Decimal("55000000"),
                reason="Test",
                document_ref="D" * 101,
                effective_date=date(2026, 6, 15),
            )


# ── FADisposal Tests ─────────────────────────────────────────────────────

class TestFADisposal:
    def test_valid_disposal(self):
        disp = FADisposal(
            asset_id=1,
            disposal_type=DisposalType.SALE,
            disposal_date=date(2026, 6, 15),
            proceeds=Decimal("50000000"),
            costs=Decimal("2000000"),
            nbv_at_disposal=Decimal("30000000"),
            reason="Ban tai san",
        )
        assert disp.asset_id == 1
        assert disp.disposal_type == DisposalType.SALE
        assert disp.is_vat_applied is False

    def test_all_disposal_types(self):
        for dt in DisposalType:
            disp = FADisposal(
                asset_id=1,
                disposal_type=dt,
                disposal_date=date(2026, 6, 15),
                proceeds=Decimal("0"),
                costs=Decimal("0"),
                nbv_at_disposal=Decimal("30000000"),
                reason=f"Test {dt.value}",
            )
            assert disp.disposal_type == dt

    def test_gain_loss_positive(self):
        disp = FADisposal(
            asset_id=1,
            disposal_type=DisposalType.SALE,
            disposal_date=date(2026, 6, 15),
            proceeds=Decimal("50000000"),
            costs=Decimal("2000000"),
            nbv_at_disposal=Decimal("30000000"),
            reason="Ban co lai",
        )
        assert disp.gain_loss == Decimal("18000000.00")

    def test_gain_loss_negative(self):
        disp = FADisposal(
            asset_id=1,
            disposal_type=DisposalType.SALE,
            disposal_date=date(2026, 6, 15),
            proceeds=Decimal("20000000"),
            costs=Decimal("5000000"),
            nbv_at_disposal=Decimal("30000000"),
            reason="Ban lo",
        )
        assert disp.gain_loss == Decimal("-15000000.00")

    def test_gain_loss_zero(self):
        disp = FADisposal(
            asset_id=1,
            disposal_type=DisposalType.LIQUIDATION,
            disposal_date=date(2026, 6, 15),
            proceeds=Decimal("0"),
            costs=Decimal("0"),
            nbv_at_disposal=Decimal("0"),
            reason="Thanh ly het kau hao",
        )
        assert disp.gain_loss == Decimal("0.00")

    def test_gain_loss_quantized(self):
        disp = FADisposal(
            asset_id=1,
            disposal_type=DisposalType.SALE,
            disposal_date=date(2026, 6, 15),
            proceeds=Decimal("50000000.123"),
            costs=Decimal("2000000.456"),
            nbv_at_disposal=Decimal("30000000.789"),
            reason="Kiem tra lam tron",
        )
        expected = Decimal("50000000.12") - Decimal("2000000.46") - Decimal("30000000.79")
        assert disp.gain_loss == expected

    def test_reason_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FADisposal(
                asset_id=1,
                disposal_type=DisposalType.SALE,
                disposal_date=date(2026, 6, 15),
                proceeds=Decimal("0"),
                costs=Decimal("0"),
                nbv_at_disposal=Decimal("0"),
                reason="",
            )

    def test_with_buyer_and_document(self):
        disp = FADisposal(
            asset_id=1,
            disposal_type=DisposalType.SALE,
            disposal_date=date(2026, 6, 15),
            proceeds=Decimal("50000000"),
            costs=Decimal("2000000"),
            nbv_at_disposal=Decimal("30000000"),
            reason="Ban cho Cong ty ABC",
            buyer_info="Cong ty TNHH ABC",
            document_ref="HD-2026-001",
            approved_by="Giam doc",
            is_vat_applied=True,
        )
        assert disp.buyer_info == "Cong ty TNHH ABC"
        assert disp.document_ref == "HD-2026-001"
        assert disp.is_vat_applied is True

    def buyer_info_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FADisposal(
                asset_id=1,
                disposal_type=DisposalType.SALE,
                disposal_date=date(2026, 6, 15),
                proceeds=Decimal("0"),
                costs=Decimal("0"),
                nbv_at_disposal=Decimal("0"),
                reason="Test",
                buyer_info="B" * 301,
            )


# ── FAInventoryLine Tests ────────────────────────────────────────────────

class TestFAInventoryLine:
    def test_difference_positive(self):
        line = FAInventoryLine(
            asset_id=1,
            book_quantity=10,
            physical_quantity=13,
        )
        assert line.difference == 3

    def test_difference_negative(self):
        line = FAInventoryLine(
            asset_id=1,
            book_quantity=10,
            physical_quantity=7,
        )
        assert line.difference == -3

    def test_difference_zero(self):
        line = FAInventoryLine(
            asset_id=1,
            book_quantity=10,
            physical_quantity=10,
        )
        assert line.difference == 0

    def test_with_reason(self):
        line = FAInventoryLine(
            asset_id=1,
            book_quantity=5,
            physical_quantity=4,
            reason="Mat mot tai san",
        )
        assert line.difference == -1
        assert line.reason == "Mat mot tai san"

    def test_default_book_quantity_one(self):
        line = FAInventoryLine(
            asset_id=1,
            physical_quantity=2,
        )
        assert line.book_quantity == 1
        assert line.difference == 1

    def test_reason_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FAInventoryLine(
                asset_id=1,
                book_quantity=1,
                physical_quantity=1,
                reason="R" * 501,
            )


# ── FAInventory Tests ────────────────────────────────────────────────────

class TestFAInventory:
    def test_valid_inventory(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
        )
        assert inv.status == InventoryStatus.OPEN
        assert inv.asset_count_book == 0
        assert inv.asset_count_physical == 0

    def test_surplus_computed(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
            asset_count_book=100,
            asset_count_physical=105,
        )
        assert inv.surplus_count == 5
        assert inv.deficit_count == 0

    def test_deficit_computed(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
            asset_count_book=100,
            asset_count_physical=93,
        )
        assert inv.surplus_count == 0
        assert inv.deficit_count == 7

    def test_no_surplus_no_deficit(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
            asset_count_book=100,
            asset_count_physical=100,
        )
        assert inv.surplus_count == 0
        assert inv.deficit_count == 0

    def test_status_default_open(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
        )
        assert inv.status == InventoryStatus.OPEN

    def test_status_resolved(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
            status=InventoryStatus.RESOLVED,
        )
        assert inv.status == InventoryStatus.RESOLVED

    def test_status_cancelled(self):
        inv = FAInventory(
            inventory_date=date(2026, 6, 30),
            department_id="D001",
            status=InventoryStatus.CANCELLED,
        )
        assert inv.status == InventoryStatus.CANCELLED

    def test_notes_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FAInventory(
                inventory_date=date(2026, 6, 30),
                department_id="D001",
                notes="N" * 1001,
            )

    def test_department_id_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FAInventory(
                inventory_date=date(2026, 6, 30),
                department_id="D" * 51,
            )


# ── FATransfer Tests ─────────────────────────────────────────────────────

class TestFATransfer:
    def test_valid_transfer_different_departments(self):
        transfer = FATransfer(
            asset_id=1,
            from_department_id="D001",
            to_department_id="D002",
            effective_date=date(2026, 7, 1),
            reason="Chuyen tai san sang bo phan khac",
        )
        assert transfer.from_department_id == "D001"
        assert transfer.to_department_id == "D002"

    def test_valid_transfer_with_locations(self):
        transfer = FATransfer(
            asset_id=1,
            from_department_id="D001",
            to_department_id="D002",
            from_location="Kho A",
            to_location="Kho B",
            effective_date=date(2026, 7, 1),
            reason="Chuyen kho",
        )
        assert transfer.from_location == "Kho A"
        assert transfer.to_location == "Kho B"

    def test_same_department_raises(self):
        with pytest.raises(DomainValidationError):
            FATransfer(
                asset_id=1,
                from_department_id="D001",
                to_department_id="D001",
                effective_date=date(2026, 7, 1),
                reason="Chuyen noi bo",
            )

    def test_reason_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FATransfer(
                asset_id=1,
                from_department_id="D001",
                to_department_id="D002",
                effective_date=date(2026, 7, 1),
                reason="",
            )

    def test_reason_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FATransfer(
                asset_id=1,
                from_department_id="D001",
                to_department_id="D002",
                effective_date=date(2026, 7, 1),
                reason="R" * 501,
            )

    def test_department_id_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FATransfer(
                asset_id=1,
                from_department_id="D" * 51,
                to_department_id="D002",
                effective_date=date(2026, 7, 1),
                reason="Test",
            )


# ── FASparePart Tests ────────────────────────────────────────────────────

class TestFASparePart:
    def test_valid_spare_part(self):
        part = FASparePart(
            asset_id=1,
            code="PK-001",
            name="Banh rang thay the",
            quantity=5,
            unit="cai",
            value=Decimal("500000"),
        )
        assert part.code == "PK-001"
        assert part.quantity == 5
        assert part.value == Decimal("500000.00")

    def test_code_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FASparePart(
                asset_id=1,
                code="",
                name="Test",
                unit="cai",
            )

    def test_code_too_long_raises(self):
        with pytest.raises(PydanticValidationError):
            FASparePart(
                asset_id=1,
                code="C" * 51,
                name="Test",
                unit="cai",
            )

    def test_name_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FASparePart(
                asset_id=1,
                code="PK-001",
                name="",
                unit="cai",
            )

    def test_value_quantized(self):
        part = FASparePart(
            asset_id=1,
            code="PK-002",
            name="Vong bi",
            unit="cai",
            value=Decimal("150000.789"),
        )
        assert part.value == Decimal("150000.79")

    def test_default_quantity_one(self):
        part = FASparePart(
            asset_id=1,
            code="PK-003",
            name="Oc vit",
            unit="cai",
        )
        assert part.quantity == 1
        assert part.value == Decimal("0.00")


# ── FAComponent Tests ────────────────────────────────────────────────────

class TestFAComponent:
    def test_valid_component(self):
        comp = FAComponent(
            asset_id=1,
            name="Dong co chinh",
            original_cost=Decimal("20000000"),
            useful_life_months=48,
            depreciation_method=DepreciationMethod.STRAIGHT_LINE,
        )
        assert comp.name == "Dong co chinh"
        assert comp.original_cost == Decimal("20000000.00")

    def test_component_minimal(self):
        comp = FAComponent(
            asset_id=1,
            name="Vo may",
        )
        assert comp.original_cost == Decimal("0.00")
        assert comp.useful_life_months is None
        assert comp.depreciation_method is None

    def test_name_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            FAComponent(
                asset_id=1,
                name="",
            )

    def test_original_cost_quantized(self):
        comp = FAComponent(
            asset_id=1,
            name="Bo phan A",
            original_cost=Decimal("15000000.789"),
        )
        assert comp.original_cost == Decimal("15000000.79")

    def test_useful_life_zero_raises(self):
        with pytest.raises(PydanticValidationError):
            FAComponent(
                asset_id=1,
                name="Test",
                original_cost=Decimal("1000000"),
                useful_life_months=0,
            )


# ── BiologicalAsset Tests ────────────────────────────────────────────────

class TestBiologicalAsset:
    def test_valid_immature(self):
        ba = BiologicalAsset(
            asset_id=1,
            biological_type=BiologicalType.PERIODIC_PRODUCER_LONG_TERM,
            quantity=Decimal("100"),
            unit="cay",
            planting_date=date(2025, 1, 1),
        )
        assert ba.growth_stage == GrowthStage.IMMATURE
        assert ba.provision_amount == Decimal("0.00")

    def test_valid_mature(self):
        ba = BiologicalAsset(
            asset_id=1,
            biological_type=BiologicalType.ONE_TIME_PRODUCT,
            growth_stage=GrowthStage.MATURE,
            unit="con",
            planting_date=date(2024, 1, 1),
        )
        assert ba.growth_stage == GrowthStage.MATURE

    def test_harvest_before_planting_raises(self):
        with pytest.raises(DomainValidationError):
            BiologicalAsset(
                asset_id=1,
                biological_type=BiologicalType.SEASONAL_CROP,
                unit="ha",
                planting_date=date(2026, 1, 1),
                expected_harvest_date=date(2025, 12, 1),
            )

    def test_harvest_after_planting_ok(self):
        ba = BiologicalAsset(
            asset_id=1,
            biological_type=BiologicalType.PERIODIC_PRODUCER_LONG_TERM,
            unit="cay",
            planting_date=date(2025, 1, 1),
            expected_harvest_date=date(2027, 1, 1),
        )
        assert ba.expected_harvest_date == date(2027, 1, 1)

    def test_provision_amount_quantized(self):
        ba = BiologicalAsset(
            asset_id=1,
            biological_type=BiologicalType.PERIODIC_PRODUCER_LONG_TERM,
            unit="cay",
            planting_date=date(2025, 1, 1),
            provision_amount=Decimal("5000000.123"),
        )
        assert ba.provision_amount == Decimal("5000000.12")

    def test_quantity_zero_allowed(self):
        ba = BiologicalAsset(
            asset_id=1,
            biological_type=BiologicalType.PERIODIC_PRODUCER_LONG_TERM,
            quantity=Decimal("0"),
            unit="cay",
            planting_date=date(2025, 1, 1),
        )
        assert ba.quantity == Decimal("0")

    def test_quantity_negative_raises(self):
        with pytest.raises(PydanticValidationError):
            BiologicalAsset(
                asset_id=1,
                biological_type=BiologicalType.PERIODIC_PRODUCER_LONG_TERM,
                quantity=Decimal("-1"),
                unit="cay",
                planting_date=date(2025, 1, 1),
            )

    def test_all_biological_types(self):
        for bt in BiologicalType:
            ba = BiologicalAsset(
                asset_id=1,
                biological_type=bt,
                unit="cay",
                planting_date=date(2025, 1, 1),
            )
            assert ba.biological_type == bt


# ── BiologicalProvision Tests ────────────────────────────────────────────

class TestBiologicalProvision:
    def test_valid_new_provision(self):
        bp = BiologicalProvision(
            biological_asset_id=1,
            period="2025-12",
            provision_amount=Decimal("10000000"),
            reason="Du phong giam gia sinh hoc",
        )
        assert bp.provision_type == ProvisionType.NEW
        assert bp.provision_amount == Decimal("10000000.00")

    def test_valid_reversal_provision(self):
        bp = BiologicalProvision(
            biological_asset_id=1,
            period="2025-12",
            provision_amount=Decimal("5000000"),
            provision_type=ProvisionType.REVERSAL,
            reason="Hoan nhap du phong",
        )
        assert bp.provision_type == ProvisionType.REVERSAL

    def test_period_format_invalid_raises(self):
        with pytest.raises(PydanticValidationError):
            BiologicalProvision(
                biological_asset_id=1,
                period="202512",
                provision_amount=Decimal("1000000"),
                reason="Test",
            )

    def test_reason_empty_raises(self):
        with pytest.raises(PydanticValidationError):
            BiologicalProvision(
                biological_asset_id=1,
                period="2025-12",
                provision_amount=Decimal("1000000"),
                reason="",
            )

    def test_amount_quantized(self):
        bp = BiologicalProvision(
            biological_asset_id=1,
            period="2025-12",
            provision_amount=Decimal("10000000.456"),
            reason="Du phong",
        )
        assert bp.provision_amount == Decimal("10000000.46")


# ── DepreciationConfig Tests ─────────────────────────────────────────────

class TestDepreciationConfig:
    def test_valid_config(self):
        cfg = DepreciationConfig(
            asset_id=1,
            method=DepreciationMethod.STRAIGHT_LINE,
            useful_life_months=60,
            residual_value=Decimal("5000000"),
            switch_to_sl_when_lower=False,
        )
        assert cfg.method == DepreciationMethod.STRAIGHT_LINE
        assert cfg.useful_life_months == 60
        assert cfg.residual_value == Decimal("5000000.00")

    def test_all_depreciation_methods(self):
        for dm in DepreciationMethod:
            cfg = DepreciationConfig(
                asset_id=1,
                method=dm,
                useful_life_months=60,
            )
            assert cfg.method == dm

    def test_useful_life_zero_raises(self):
        with pytest.raises(PydanticValidationError):
            DepreciationConfig(
                asset_id=1,
                method=DepreciationMethod.STRAIGHT_LINE,
                useful_life_months=0,
            )

    def test_residual_value_quantized(self):
        cfg = DepreciationConfig(
            asset_id=1,
            method=DepreciationMethod.STRAIGHT_LINE,
            useful_life_months=60,
            residual_value=Decimal("5000000.789"),
        )
        assert cfg.residual_value == Decimal("5000000.79")

    def test_switch_to_sl_default_false(self):
        cfg = DepreciationConfig(
            asset_id=1,
            method=DepreciationMethod.DECLINING_BALANCE,
            useful_life_months=60,
        )
        assert cfg.switch_to_sl_when_lower is False

    def test_switch_to_sl_true(self):
        cfg = DepreciationConfig(
            asset_id=1,
            method=DepreciationMethod.DECLINING_BALANCE,
            useful_life_months=60,
            switch_to_sl_when_lower=True,
        )
        assert cfg.switch_to_sl_when_lower is True
