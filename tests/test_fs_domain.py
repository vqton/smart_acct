from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.fs import (
    FinancialStatementType,
    FSStatus,
    FSCashFlowMethod,
    FSLineItem,
    FSAuditLog,
    FSAccountMapping,
    FinancialStatement,
    FSConsolidationGroup,
    FSConsolidationMember,
)
from domain.common import ValidationError


class TestEnums:
    def test_statement_type_values(self):
        assert FinancialStatementType.BALANCE_SHEET_GC.value == "B01_DN"
        assert FinancialStatementType.INCOME_STATEMENT_GC.value == "B02_DN"
        assert FinancialStatementType.CASH_FLOW_GC.value == "B03_DN"
        assert FinancialStatementType.NOTES_GC.value == "B09_DN"
        assert FinancialStatementType.BALANCE_SHEET_NGC.value == "B01_DNKLT"

    def test_statement_type_methods(self):
        assert FinancialStatementType.is_going_concern("B01_DN")
        assert not FinancialStatementType.is_non_going_concern("B01_DN")
        assert FinancialStatementType.is_non_going_concern("B01_DNKLT")

    def test_fs_status_values(self):
        assert FSStatus.DRAFT.value == "DRAFT"
        assert FSStatus.IN_REVIEW.value == "IN_REVIEW"
        assert FSStatus.REVIEWED.value == "REVIEWED"
        assert FSStatus.APPROVED.value == "APPROVED"
        assert FSStatus.SIGNED.value == "SIGNED"
        assert FSStatus.REJECTED.value == "REJECTED"
        assert FSStatus.AMENDED.value == "AMENDED"

    def test_cash_flow_method_values(self):
        assert FSCashFlowMethod.DIRECT.value == "direct"
        assert FSCashFlowMethod.INDIRECT.value == "indirect"


class TestFSLineItem:
    def test_create_valid(self):
        item = FSLineItem(ma_so="100", ten_chi_tieu="Tiền", so_thu_tu=1)
        assert item.ma_so == "100"
        assert item.current_year == Decimal("0.00")
        assert item.previous_year is None
        assert not item.is_subtotal

    def test_create_with_all_fields(self):
        item = FSLineItem(
            ma_so="200", ten_chi_tieu="Đầu tư", so_thu_tu=2,
            parent_ma_so="100", current_year=Decimal("500000000"),
            previous_year=Decimal("300000000"), is_subtotal=True,
            is_calculated=True, calculation_formula="110+120+130",
            thuyet_minh="01",
        )
        assert item.current_year == Decimal("500000000.00")
        assert item.previous_year == Decimal("300000000.00")
        assert item.is_subtotal
        assert item.calculation_formula == "110+120+130"

    def test_empty_ma_so_raises(self):
        with pytest.raises(ValueError):
            FSLineItem(ma_so="", ten_chi_tieu="Test", so_thu_tu=1)

    def test_empty_ten_chi_tieu_raises(self):
        with pytest.raises(ValueError):
            FSLineItem(ma_so="100", ten_chi_tieu="", so_thu_tu=1)

    def test_negative_current_year(self):
        item = FSLineItem(ma_so="421", ten_chi_tieu="LN chưa PP",
                           so_thu_tu=1, current_year=Decimal("-50000000"))
        assert item.current_year == Decimal("-50000000.00")

    def test_vnd_quantization(self):
        raw = Decimal("1000000.555")
        item = FSLineItem(ma_so="110", ten_chi_tieu="Test",
                           so_thu_tu=1, current_year=raw)
        assert item.current_year == Decimal("1000000.56")


class TestFSAccountMapping:
    def test_create_valid(self):
        m = FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert m.weight == Decimal("1.00")
        assert m.direction == "both"

    def test_custom_weight_and_direction(self):
        m = FSAccountMapping(
            fs_ma_so="220", account_code="131",
            weight=Decimal("0.50"), direction="debit",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert m.weight == Decimal("0.50")
        assert m.direction == "debit"

    def test_empty_fields_raises(self):
        with pytest.raises(ValueError):
            FSAccountMapping(fs_ma_so="", account_code="1111",
                             statement_type=FinancialStatementType.BALANCE_SHEET_GC,
            )

    def test_invalid_direction_raises(self):
        with pytest.raises(ValidationError):
            FSAccountMapping(fs_ma_so="110", account_code="1111",
                             direction="invalid",
                             statement_type=FinancialStatementType.BALANCE_SHEET_GC,
            )

    def test_zero_weight_raises(self):
        with pytest.raises(ValidationError):
            FSAccountMapping(fs_ma_so="110", account_code="1111",
                             weight=Decimal("0"),
                             statement_type=FinancialStatementType.BALANCE_SHEET_GC,
            )


class TestFinancialStatement:
    def test_create_draft(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.status == FSStatus.DRAFT
        assert fs.version == 1
        assert fs.period == "2026-06"
        assert len(fs.lines) == 0

    def test_can_transition_to_valid(self):
        fs = FinancialStatement(
            period="2026",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.can_transition_to(FSStatus.IN_REVIEW)
        assert not fs.can_transition_to(FSStatus.SIGNED)

    def test_can_transition_from_reviewed(self):
        fs = FinancialStatement(
            period="2026", status=FSStatus.REVIEWED,
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.can_transition_to(FSStatus.APPROVED)
        assert fs.can_transition_to(FSStatus.REJECTED)
        assert not fs.can_transition_to(FSStatus.DRAFT)

    def test_can_transition_from_signed(self):
        fs = FinancialStatement(
            period="2026", status=FSStatus.SIGNED,
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.can_transition_to(FSStatus.AMENDED)
        assert not fs.can_transition_to(FSStatus.DRAFT)

    def test_invalid_period_format_raises(self):
        with pytest.raises(Exception):
            FinancialStatement(period="invalid",
                               statement_type=FinancialStatementType.BALANCE_SHEET_GC,
            )

    def test_short_period_valid(self):
        fs = FinancialStatement(
            period="2026",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.period == "2026"

    def test_b01_cash_flow_not_required(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.cash_flow_method is None

    def test_b03_cash_flow_required(self):
        with pytest.raises(ValidationError):
            FinancialStatement(period="2026-06",
                               statement_type=FinancialStatementType.CASH_FLOW_GC,
            )

    def test_b03_with_direct(self):
        fs = FinancialStatement(
            period="2026-06", cash_flow_method=FSCashFlowMethod.DIRECT,
            statement_type=FinancialStatementType.CASH_FLOW_GC,
        )
        assert fs.cash_flow_method == FSCashFlowMethod.DIRECT

    def test_b03_with_indirect(self):
        fs = FinancialStatement(
            period="2026-06", cash_flow_method=FSCashFlowMethod.INDIRECT,
            statement_type=FinancialStatementType.CASH_FLOW_GC,
        )
        assert fs.cash_flow_method == FSCashFlowMethod.INDIRECT

    def test_get_line_by_ma_so(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        fs.lines.append(FSLineItem(ma_so="110", ten_chi_tieu="Tiền", so_thu_tu=1))
        fs.lines.append(FSLineItem(ma_so="120", ten_chi_tieu="Phải thu", so_thu_tu=2))
        assert fs.get_line_by_ma_so("110") is not None
        assert fs.get_line_by_ma_so("999") is None

    def test_get_subtotals(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        fs.lines.append(FSLineItem(ma_so="100", ten_chi_tieu="TSNH",
                       so_thu_tu=1, is_subtotal=True, current_year=Decimal("100000000")))
        assert len(fs.get_subtotals()) > 0

    def test_verify_balance_sheet_equal(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        fs.lines.append(FSLineItem(ma_so="270", ten_chi_tieu="Tổng TS",
                       so_thu_tu=1, current_year=Decimal("100000000")))
        fs.lines.append(FSLineItem(ma_so="440", ten_chi_tieu="Tổng NV",
                       so_thu_tu=2, current_year=Decimal("100000000")))
        assert fs.verify_balance_sheet()

    def test_verify_balance_sheet_unequal(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        fs.lines.append(FSLineItem(ma_so="270", ten_chi_tieu="Tổng TS",
                       so_thu_tu=1, current_year=Decimal("100000000")))
        fs.lines.append(FSLineItem(ma_so="440", ten_chi_tieu="Tổng NV",
                       so_thu_tu=2, current_year=Decimal("90000000")))
        assert not fs.verify_balance_sheet()

    def test_verify_balance_sheet_skips_pl(self):
        fs = FinancialStatement(
            period="2026-06",
            statement_type=FinancialStatementType.INCOME_STATEMENT_GC,
        )
        assert fs.verify_balance_sheet()

    def test_consolidated_flag(self):
        fs = FinancialStatement(
            period="2026-06", is_consolidated=True,
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        assert fs.is_consolidated


class TestFSConsolidationGroup:
    def test_create_valid(self):
        g = FSConsolidationGroup(name="Tap doan", parent_entity_id=1)
        assert g.name == "Tap doan"
        assert g.consolidation_method == "full"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            FSConsolidationGroup(name="", parent_entity_id=1)


class TestFSConsolidationMember:
    def test_create_valid(self):
        m = FSConsolidationMember(entity_id=2, group_id=1,
                                   ownership_percentage=Decimal("80.00"))
        assert m.ownership_percentage == Decimal("80.00")
        assert m.consolidation_method == "full"

    def test_minority_ownership(self):
        m = FSConsolidationMember(entity_id=3, group_id=1,
                                   ownership_percentage=Decimal("25.00"),
                                   consolidation_method="equity")
        assert m.consolidation_method == "equity"

    def test_default_ownership(self):
        m = FSConsolidationMember(entity_id=4, group_id=1)
        assert m.ownership_percentage == Decimal("100.00")


class TestB01Template:
    def test_full_template_size(self):
        assert len(FinancialStatement.B01_DN_LINE_ITEMS) > 0

    def test_has_total_assets(self):
        codes = {i["ma_so"] for i in FinancialStatement.B01_DN_LINE_ITEMS}
        assert "270" in codes

    def test_has_total_sources(self):
        codes = {i["ma_so"] for i in FinancialStatement.B01_DN_LINE_ITEMS}
        assert "440" in codes


class TestB02Template:
    def test_full_template_size(self):
        assert len(FinancialStatement.B02_DN_LINE_ITEMS) > 0

    def test_has_net_profit(self):
        codes = {i["ma_so"] for i in FinancialStatement.B02_DN_LINE_ITEMS}
        assert "60" in codes
