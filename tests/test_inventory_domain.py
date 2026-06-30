from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.inventory import (
    InventoryType, InventoryStatus, MovementType, ValuationMethod,
    CheckMethod, InventoryCheckStatus, BatchStatus, SerialStatus,
    AdjustmentType, TransferStatus,
    InventoryCategory, Warehouse, InventoryItem, InventoryBatch,
    SerialNumber, InventoryReceipt, InventoryReceiptLine,
    InventoryIssue, InventoryIssueLine, InventoryTransfer,
    InventoryTransferLine, StockCard, InventoryCheck, InventoryCheckLine,
    InventoryAdjustment, InventoryAdjustmentLine, InventoryConfig,
    InventoryDashboard,
)
from domain.common import AccountError


class TestInventoryEnums:
    def test_inventory_type_values(self):
        assert InventoryType.RAW_MATERIAL.value == "raw_material"
        assert InventoryType.MERCHANDISE.value == "merchandise"
        assert InventoryType.FINISHED_GOOD.value == "finished_good"

    def test_valuation_method_values(self):
        assert ValuationMethod.WEIGHTED_AVERAGE.value == "weighted_average"
        assert ValuationMethod.FIFO.value == "fifo"

    def test_adjustment_type_values(self):
        assert AdjustmentType.WRITE_OFF.value == "write_off"
        assert AdjustmentType.WRITE_ON.value == "write_on"

    def test_transfer_status_values(self):
        assert TransferStatus.DRAFT.value == "draft"
        assert TransferStatus.COMPLETED.value == "completed"


class TestInventoryCategory:
    def test_valid_minimal(self):
        c = InventoryCategory(code="NVL", name="Nguyên vật liệu")
        assert c.code == "NVL"
        assert c.inventory_type == InventoryType.MERCHANDISE
        assert c.valuation_method == ValuationMethod.WEIGHTED_AVERAGE
        assert c.is_active is True
        assert c.gl_inventory_account == "152"

    def test_valid_all_fields(self):
        c = InventoryCategory(code="TP", name="Thành phẩm",
                               inventory_type=InventoryType.FINISHED_GOOD,
                               valuation_method=ValuationMethod.FIFO,
                               gl_inventory_account="155", gl_sales_account="511")
        assert c.gl_inventory_account == "155"
        assert c.valuation_method == ValuationMethod.FIFO

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryCategory(code="", name="Test")

    def test_code_whitespace_raises(self):
        with pytest.raises(AccountError):
            InventoryCategory(code="   ", name="Test")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryCategory(code="T1", name="")

    def test_with_parent(self):
        c = InventoryCategory(code="NVL-P", name="Phụ liệu", parent_id=1)
        assert c.parent_id == 1


class TestWarehouse:
    def test_valid_minimal(self):
        w = Warehouse(code="KHO01", name="Kho số 1")
        assert w.is_active is True
        assert w.allow_negative_stock is False
        assert w.check_method == CheckMethod.PERPETUAL

    def test_valid_all_fields(self):
        w = Warehouse(code="KHO02", name="Kho số 2",
                       address="123 Lý Thường Kiệt", allow_negative_stock=True)
        assert w.allow_negative_stock is True
        assert w.address == "123 Lý Thường Kiệt"

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            Warehouse(code="", name="Test")

    def test_name_empty_raises(self):
        with pytest.raises(AccountError):
            Warehouse(code="KHO", name="")


class TestInventoryItem:
    def test_valid_minimal(self):
        i = InventoryItem(code="VT001", name="Vật tư 1", category_id=1)
        assert i.status == InventoryStatus.ACTIVE
        assert i.unit == "cái"
        assert i.current_stock == Decimal("0")
        assert i.available_stock == Decimal("0")

    def test_valid_all_fields(self):
        i = InventoryItem(code="VT002", name="Vật tư 2", category_id=1,
                           inventory_type=InventoryType.RAW_MATERIAL,
                           unit="kg", cost_price=Decimal("50000"),
                           selling_price=Decimal("75000"),
                           current_stock=Decimal("100"),
                           batch_tracking=True, barcode="8934567890123")
        assert i.cost_price == Decimal("50000")
        assert i.current_stock == Decimal("100")
        assert i.batch_tracking is True

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryItem(code="", name="Test", category_id=1)

    def test_negative_cost_price_raises(self):
        with pytest.raises(AccountError):
            InventoryItem(code="VT003", name="Test", category_id=1,
                          cost_price=Decimal("-1000"))

    def test_available_stock_auto_calc(self):
        i = InventoryItem(code="VT004", name="Test", category_id=1,
                           current_stock=Decimal("50"), reserved_stock=Decimal("10"))
        assert i.available_stock == Decimal("40")

    def test_available_stock_negative_reserved(self):
        i = InventoryItem(code="VT005", name="Test", category_id=1,
                           available_stock=Decimal("999"))
        assert i.available_stock == Decimal("0")


class TestInventoryBatch:
    def test_valid(self):
        b = InventoryBatch(item_id=1, batch_code="LÔ20260101",
                            received_date=date(2026, 1, 1))
        assert b.status == BatchStatus.ACTIVE
        assert b.remaining_quantity == Decimal("0")

    def test_valid_with_expiry(self):
        b = InventoryBatch(item_id=1, batch_code="LÔ202601",
                            received_date=date(2026, 1, 1),
                            manufacturing_date=date(2026, 1, 1),
                            expiry_date=date(2027, 1, 1))
        assert b.expiry_date == date(2027, 1, 1)

    def test_expiry_before_manufacturing_raises(self):
        with pytest.raises(AccountError):
            InventoryBatch(item_id=1, batch_code="LÔ002",
                           received_date=date(2026, 1, 15),
                           manufacturing_date=date(2026, 1, 15),
                           expiry_date=date(2025, 12, 31))

    def test_batch_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryBatch(item_id=1, batch_code="",
                           received_date=date(2026, 1, 1))


class TestSerialNumber:
    def test_valid(self):
        s = SerialNumber(item_id=1, serial_code="SN001")
        assert s.status == SerialStatus.IN_STOCK

    def test_serial_empty_raises(self):
        with pytest.raises(AccountError):
            SerialNumber(item_id=1, serial_code="")


class TestInventoryReceipt:
    def test_valid_minimal(self):
        r = InventoryReceipt(receipt_code="NK0001", receipt_date=date(2026, 6, 1),
                              warehouse_id=1)
        assert r.is_posted is False

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryReceipt(receipt_code="", receipt_date=date(2026, 6, 1),
                             warehouse_id=1)


class TestInventoryReceiptLine:
    def test_total_auto_calc(self):
        l = InventoryReceiptLine(receipt_id=1, item_id=1, warehouse_id=1,
                                  quantity=Decimal("10"), unit_price=Decimal("50000"))
        assert l.total_amount == Decimal("500000")

    def test_quantity_zero_raises(self):
        with pytest.raises(Exception):
            InventoryReceiptLine(receipt_id=1, item_id=1, warehouse_id=1,
                                 quantity=Decimal("0"), unit_price=Decimal("50000"))


class TestInventoryIssue:
    def test_valid_minimal(self):
        i = InventoryIssue(issue_code="XK0001", issue_date=date(2026, 6, 1),
                            warehouse_id=1)
        assert i.is_posted is False

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryIssue(issue_code="", issue_date=date(2026, 6, 1),
                           warehouse_id=1)


class TestInventoryIssueLine:
    def test_totals_auto_calc(self):
        l = InventoryIssueLine(issue_id=1, item_id=1, warehouse_id=1,
                                quantity=Decimal("5"), unit_price=Decimal("50000"),
                                cost_price=Decimal("45000"))
        assert l.total_amount == Decimal("250000")
        assert l.cost_amount == Decimal("225000")


class TestInventoryTransfer:
    def test_valid(self):
        t = InventoryTransfer(transfer_code="CK0001", transfer_date=date(2026, 6, 1),
                               from_warehouse_id=1, to_warehouse_id=2)
        assert t.status == TransferStatus.DRAFT

    def test_same_warehouse_raises(self):
        with pytest.raises(AccountError):
            InventoryTransfer(transfer_code="CK0002", transfer_date=date(2026, 6, 1),
                              from_warehouse_id=1, to_warehouse_id=1)

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryTransfer(transfer_code="", transfer_date=date(2026, 6, 1),
                              from_warehouse_id=1, to_warehouse_id=2)


class TestInventoryTransferLine:
    def test_total_auto_calc(self):
        l = InventoryTransferLine(transfer_id=1, item_id=1,
                                   quantity=Decimal("10"), unit_price=Decimal("30000"))
        assert l.total_amount == Decimal("300000")


class TestStockCard:
    def test_valid(self):
        c = StockCard(item_id=1, warehouse_id=1, period="2026-06")
        assert c.opening_quantity == Decimal("0")

    def test_with_data(self):
        c = StockCard(item_id=1, warehouse_id=1, period="2026-06",
                       opening_quantity=Decimal("50"), opening_value=Decimal("2500000"),
                       receipt_quantity=Decimal("30"), receipt_value=Decimal("1500000"),
                       issue_quantity=Decimal("10"), issue_value=Decimal("500000"))
        assert c.closing_quantity == Decimal("0")


class TestInventoryCheck:
    def test_valid(self):
        c = InventoryCheck(check_code="KK0001", check_date=date(2026, 6, 30),
                            warehouse_id=1)
        assert c.status == InventoryCheckStatus.DRAFT

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryCheck(check_code="", check_date=date(2026, 6, 30),
                           warehouse_id=1)


class TestInventoryCheckLine:
    def test_difference_auto_calc(self):
        l = InventoryCheckLine(check_id=1, item_id=1, warehouse_id=1,
                                book_quantity=Decimal("100"), physical_quantity=Decimal("98"),
                                unit_price=Decimal("50000"))
        assert l.difference_quantity == Decimal("-2")
        assert l.difference_value == Decimal("-100000")

    def test_zero_diff(self):
        l = InventoryCheckLine(check_id=1, item_id=1, warehouse_id=1,
                                book_quantity=Decimal("50"), physical_quantity=Decimal("50"),
                                unit_price=Decimal("10000"))
        assert l.difference_quantity == Decimal("0")
        assert l.difference_value == Decimal("0")


class TestInventoryAdjustment:
    def test_valid(self):
        a = InventoryAdjustment(adjustment_code="DC0001", adjustment_date=date(2026, 6, 30),
                                 warehouse_id=1, reason="Hao hụt tự nhiên",
                                 adjustment_type=AdjustmentType.WRITE_OFF)
        assert a.is_posted is False

    def test_code_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryAdjustment(adjustment_code="", adjustment_date=date(2026, 6, 30),
                                warehouse_id=1, reason="Test")

    def test_reason_empty_raises(self):
        with pytest.raises(AccountError):
            InventoryAdjustment(adjustment_code="DC001", adjustment_date=date(2026, 6, 30),
                                warehouse_id=1, reason="")


class TestInventoryAdjustmentLine:
    def test_total_auto_calc(self):
        l = InventoryAdjustmentLine(adjustment_id=1, item_id=1, warehouse_id=1,
                                     quantity_change=Decimal("-5"),
                                     unit_price=Decimal("100000"))
        assert l.total_amount == Decimal("500000")

    def test_positive_change(self):
        l = InventoryAdjustmentLine(adjustment_id=1, item_id=2, warehouse_id=1,
                                     quantity_change=Decimal("10"),
                                     unit_price=Decimal("50000"))
        assert l.total_amount == Decimal("500000")


class TestInventoryConfig:
    def test_defaults(self):
        c = InventoryConfig()
        assert c.default_valuation_method == ValuationMethod.WEIGHTED_AVERAGE
        assert c.auto_post_gl is True
        assert c.receipt_number_prefix == "NK"


class TestInventoryDashboard:
    def test_defaults(self):
        d = InventoryDashboard()
        assert d.total_items == 0
        assert d.total_stock_value == Decimal("0")
