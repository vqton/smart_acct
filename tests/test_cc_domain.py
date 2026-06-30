from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.cc import (
    CCDCType, AllocationMethod, CCDCStatus, AllocationStatus,
    TransactionType, InventoryStatus as CCInventoryStatus,
    ResponsibilityType,
    CCategory, CCDCItem, CCDCAllocation, CCDCAllocationLine,
    CCDCTransaction, CCDCTransfer, CCDCInventory, CCDCInventoryLine,
    CCDCWriteOff, CCDCSparePart, CCDCImportLog,
)
from domain.common import AccountError


class TestCCategory:
    def test_valid_minimal(self):
        c = CCategory(code="VP", name="Văn phòng phẩm")
        assert c.code == "VP"
        assert c.default_allocation_method == AllocationMethod.one_time
        assert c.gl_asset_account == "153"
        assert c.gl_expense_account == "627"
        assert c.is_active is True

    def test_valid_all_fields(self):
        c = CCategory(code="DC-SX", name="Dụng cụ sản xuất",
                       description="Dụng cụ phục vụ sản xuất",
                       default_allocation_method=AllocationMethod.multi_period,
                       default_useful_life_months=24,
                       gl_asset_account="153", gl_alloc_account="242",
                       gl_expense_account="627")
        assert c.default_useful_life_months == 24

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            CCategory(code="", name="Test")

    def test_code_whitespace_raises(self):
        with pytest.raises(AccountError):
            CCategory(code="   ", name="Test")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            CCategory(code="T1", name="")

    def test_useful_life_out_of_range(self):
        with pytest.raises(AccountError):
            CCategory(code="T1", name="Test", default_useful_life_months=48)


class TestCCDCItem:
    def test_valid_minimal(self):
        item = CCDCItem(code="CC001", name="Búa", category_id=1)
        assert item.status == CCDCStatus.in_stock
        assert item.allocation_method == AllocationMethod.one_time
        assert item.quantity == Decimal("1")
        assert item.unit == "cái"

    def test_valid_all_fields(self):
        item = CCDCItem(code="CC002", name="Máy khoan", category_id=1,
                        cc_type=CCDCType.equipment,
                        quantity=Decimal("2"), unit_price=Decimal("500000"),
                        total_cost=Decimal("1000000"),
                        purchase_date=date(2026, 1, 15))
        assert item.total_cost == Decimal("1000000")
        assert item.remaining_amount == item.total_cost - item.allocated_amount

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            CCDCItem(code="", name="Test", category_id=1)

    def test_negative_cost_raises(self):
        with pytest.raises(AccountError):
            CCDCItem(code="CC003", name="Test", category_id=1,
                     total_cost=Decimal("-1000"))

    def test_allocated_exceeds_cost(self):
        with pytest.raises(AccountError):
            CCDCItem(code="CC004", name="Test", category_id=1,
                     total_cost=Decimal("1000"),
                     allocated_amount=Decimal("2000"))

    def test_in_use_before_purchase_raises(self):
        with pytest.raises(AccountError):
            CCDCItem(code="CC005", name="Test", category_id=1,
                     purchase_date=date(2026, 6, 1),
                     in_use_date=date(2026, 1, 1))

    def test_remaining_amount_calculated(self):
        item = CCDCItem(code="CC006", name="Test", category_id=1,
                        total_cost=Decimal("1000000"),
                        allocated_amount=Decimal("300000"))
        assert item.remaining_amount == Decimal("700000")


class TestCCDCAllocation:
    def test_valid_one_time(self):
        a = CCDCAllocation(item_id=1, allocation_method=AllocationMethod.one_time,
                           total_amount=Decimal("1000000"),
                           start_period="2026-01")
        assert a.start_period == "2026-01"

    def test_invalid_period_format(self):
        with pytest.raises(AccountError):
            CCDCAllocation(item_id=1, allocation_method=AllocationMethod.one_time,
                           total_amount=Decimal("1000"),
                           start_period="2026/01")


class TestCCDCAllocationLine:
    def test_valid(self):
        l = CCDCAllocationLine(allocation_id=1, item_id=1,
                                period="2026-01",
                                planned_amount=Decimal("500000"))
        assert l.period == "2026-01"
        assert l.is_posted is False

    def test_invalid_period(self):
        with pytest.raises(AccountError):
            CCDCAllocationLine(allocation_id=1, item_id=1,
                               period="bad-period",
                               planned_amount=Decimal("500"))


class TestCCDCTransaction:
    def test_valid(self):
        t = CCDCTransaction(item_id=1, transaction_type=TransactionType.receipt,
                            quantity=Decimal("5"), unit_price=Decimal("100000"),
                            total_amount=Decimal("500000"),
                            transaction_date=date(2026, 1, 15),
                            period="2026-01")
        assert t.transaction_type == TransactionType.receipt

    def test_invalid_period(self):
        with pytest.raises(AccountError):
            CCDCTransaction(item_id=1, transaction_type=TransactionType.receipt,
                            quantity=Decimal("1"), total_amount=Decimal("100"),
                            transaction_date=date(2026, 1, 15),
                            period="invalid")


class TestCCDCTransfer:
    def test_valid(self):
        t = CCDCTransfer(item_id=1, transfer_date=date(2026, 2, 1),
                         to_department_id=2, reason="Chuyển kho")
        assert t.transfer_date == date(2026, 2, 1)


class TestCCDCInventory:
    def test_valid(self):
        inv = CCDCInventory(inventory_date=date(2026, 6, 30))
        assert inv.status == CCInventoryStatus.draft

    def test_valid_with_lines(self):
        line = CCDCInventoryLine(inventory_id=0, item_id=1,
                                  book_quantity=Decimal("10"),
                                  physical_quantity=Decimal("8"))
        assert line.difference == Decimal("-2")
        inv = CCDCInventory(inventory_date=date(2026, 6, 30), lines=[line])
        assert len(inv.lines) == 1


class TestCCDCInventoryLine:
    def test_surplus(self):
        l = CCDCInventoryLine(inventory_id=1, item_id=1,
                              book_quantity=Decimal("5"),
                              physical_quantity=Decimal("7"),
                              unit_price=Decimal("1000"))
        assert l.difference == Decimal("2")
        assert l.difference_amount == Decimal("2000")

    def test_deficit(self):
        l = CCDCInventoryLine(inventory_id=1, item_id=1,
                              book_quantity=Decimal("10"),
                              physical_quantity=Decimal("7"),
                              unit_price=Decimal("500"))
        assert l.difference == Decimal("-3")
        assert l.difference_amount == Decimal("-1500")


class TestCCDCWriteOff:
    def test_valid(self):
        wo = CCDCWriteOff(item_id=1, write_off_date=date(2026, 3, 1),
                          quantity=Decimal("1"),
                          remaining_value=Decimal("200000"),
                          reason="Hỏng không sử dụng được")
        assert wo.loss_amount == wo.remaining_value - wo.proceeds

    def test_loss_capped_at_zero(self):
        wo = CCDCWriteOff(item_id=1, write_off_date=date(2026, 3, 1),
                          quantity=Decimal("1"),
                          remaining_value=Decimal("200000"),
                          proceeds=Decimal("300000"),
                          reason="Bán thanh lý")
        assert wo.loss_amount == Decimal("0")


class TestCCDCSparePart:
    def test_valid(self):
        sp = CCDCSparePart(item_id=1, code="PK001", name="Phụ kiện A",
                           quantity=Decimal("10"), unit_price=Decimal("50000"))
        assert sp.total_value == Decimal("500000")


class TestCCDCImportLog:
    def test_valid(self):
        from datetime import datetime
        log = CCDCImportLog(filename="import.xlsx", import_date=datetime.now(),
                            total_rows=10, success_count=8, error_count=2,
                            errors=[{"row": 5, "error": "Duplicate code"}])
        assert log.filename == "import.xlsx"
        assert log.success_count == 8


class TestCCDCEnums:
    def test_ccdc_type_values(self):
        assert CCDCType.tool.value == "tool"
        assert CCDCType.equipment.value == "equipment"

    def test_allocation_method_values(self):
        assert AllocationMethod.one_time.value == "one_time"
        assert AllocationMethod.two_time.value == "two_time"
        assert AllocationMethod.multi_period.value == "multi_period"

    def test_status_values(self):
        assert CCDCStatus.in_stock.value == "in_stock"
        assert CCDCStatus.in_use.value == "in_use"
        assert CCDCStatus.disposed.value == "disposed"
