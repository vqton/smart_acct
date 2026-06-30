from decimal import Decimal
from datetime import date, datetime
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    InventoryType, ValuationMethod, CheckMethod,
    InventoryCheckStatus, BatchStatus, TransferStatus,
    InventoryCategory, Warehouse, InventoryItem, InventoryBatch,
    SerialNumber, InventoryReceipt, InventoryReceiptLine,
    InventoryIssue, InventoryIssueLine, InventoryTransfer,
    InventoryTransferLine, StockCard, InventoryCheck, InventoryCheckLine,
    InventoryAdjustment, InventoryAdjustmentLine,
    Result, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import Base
from infrastructure.models.inventory_models import (
    InventoryCategoryModel, WarehouseModel, InventoryItemModel,
    InventoryBatchModel, SerialNumberModel,
    InventoryReceiptModel, InventoryReceiptLineModel,
    InventoryIssueModel, InventoryIssueLineModel,
    InventoryTransferModel, InventoryTransferLineModel,
    StockCardModel,
    InventoryCheckModel, InventoryCheckLineModel,
    InventoryAdjustmentModel, InventoryAdjustmentLineModel,
    InventoryTypeDB, InventoryStatusDB, ValuationMethodDB,
    CheckMethodDB, InventoryCheckStatusDB, BatchStatusDB,
    AdjustmentTypeDB, TransferStatusDB,
)
from infrastructure.repositories.inventory_repository import InventoryRepository
from domain.inventory import AdjustmentType
from use_cases.inventory import InventoryUseCases


def _make_category_data(code="NVL", name="Nguyên vật liệu", **kw) -> dict:
    data = {"code": code, "name": name,
            "inventory_type": InventoryType.MERCHANDISE.value,
            "valuation_method": ValuationMethod.WEIGHTED_AVERAGE.value,
            "gl_inventory_account": "152", "gl_receipt_account": "331",
            "gl_issue_account": "621", "gl_sales_account": "632",
            "gl_cost_of_sales": "632", "gl_return_account": "521"}
    data.update(kw)
    return data


def _make_warehouse_data(code="KHO01", name="Kho chính", **kw) -> dict:
    data = {"code": code, "name": name, "check_method": CheckMethod.PERPETUAL.value}
    data.update(kw)
    return data


def _make_item_data(category_id: int, code="VT001", name="Vật tư 1", **kw) -> dict:
    data = {"code": code, "name": name, "category_id": category_id,
            "inventory_type": InventoryType.MERCHANDISE.value,
            "unit": "cái", "cost_price": Decimal("50000"),
            "selling_price": Decimal("75000"),
            "current_stock": Decimal("0"), "available_stock": Decimal("0")}
    data.update(kw)
    return data


def _make_receipt_data(code="NK0001", date_str="2026-06-15", warehouse_id=1, **kw) -> dict:
    data = {"receipt_code": code, "receipt_date": date.fromisoformat(date_str),
            "warehouse_id": warehouse_id}
    data.update(kw)
    return data


def _make_issue_data(code="XK0001", date_str="2026-06-20", warehouse_id=1, **kw) -> dict:
    data = {"issue_code": code, "issue_date": date.fromisoformat(date_str),
            "warehouse_id": warehouse_id}
    data.update(kw)
    return data


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    conn = engine.connect()
    trans = conn.begin()
    session = Session(bind=conn)
    yield session
    session.close()
    trans.rollback()
    conn.close()


@pytest.fixture
def repo(session):
    return InventoryRepository(session)


@pytest.fixture
def uc(session):
    return InventoryUseCases(session)


@pytest.fixture
def category(repo):
    data = _make_category_data()
    cat = InventoryCategory(**data)
    return repo.create_category(cat).get_data()


@pytest.fixture
def warehouse(repo):
    data = _make_warehouse_data()
    wh = Warehouse(**data)
    return repo.create_warehouse(wh).get_data()


@pytest.fixture
def item(repo, category, warehouse):
    data = _make_item_data(category_id=category.id)
    it = InventoryItem(**data)
    return repo.create_item(it).get_data()


@pytest.fixture
def batch(repo, item, warehouse):
    b = InventoryBatch(item_id=item.id, warehouse_id=warehouse.id,
                        batch_code="LÔ001",
                        received_date=date(2026, 6, 1),
                        quantity=Decimal("100"), remaining_quantity=Decimal("100"),
                        unit_cost=Decimal("50000"), total_cost=Decimal("5000000"))
    return repo.create_batch(b).get_data()


# ═══════════════════════════════════════════════════════════════════
# Category Tests (UC-INV-01)
# ═══════════════════════════════════════════════════════════════════

class TestCategoryCRUD:
    def test_create(self, repo):
        data = _make_category_data()
        cat = InventoryCategory(**data)
        result = repo.create_category(cat)
        assert result.is_success()
        c = result.get_data()
        assert c.code == "NVL"
        assert c.id is not None

    def test_create_duplicate_code(self, repo, category):
        data = _make_category_data(code=category.code)
        cat = InventoryCategory(**data)
        result = repo.create_category(cat)
        assert result.is_failure()

    def test_get_by_id(self, repo, category):
        c = repo.get_category(category.id)
        assert c is not None
        assert c.id == category.id

    def test_get_by_code(self, repo, category):
        c = repo.get_category_by_code(category.code)
        assert c is not None
        assert c.code == category.code

    def test_list(self, repo, category):
        cats = repo.list_categories()
        assert len(cats) >= 1

    def test_update(self, repo, category):
        result = repo.update_category(category.id, name="Updated")
        assert result.is_success()
        assert repo.get_category(category.id).name == "Updated"

    def test_delete(self, repo, category):
        result = repo.delete_category(category.id)
        assert result.is_success()
        assert repo.get_category(category.id) is None

    def test_delete_with_items_fails(self, repo, category, item):
        result = repo.delete_category(category.id)
        assert result.is_failure()


class TestCategoryUseCases:
    def test_create_uc(self, uc):
        data = _make_category_data(code="TP", name="Thành phẩm",
                                    inventory_type="finished_good")
        result = uc.create_category(**data)
        assert result.is_success()
        assert result.get_data().code == "TP"

    def test_list_uc(self, uc, category):
        cats = uc.list_categories()
        assert len(cats) >= 1

    def test_list_filter_type(self, uc, category):
        cats = uc.list_categories(inventory_type="merchandise")
        assert len(cats) >= 1

    def test_update_uc(self, uc, category):
        result = uc.update_category(category.id, name="Updated Name")
        assert result.is_success()

    def test_delete_uc(self, uc):
        result = uc.create_category(**{"code": "DEL", "name": "To Delete"})
        cat = result.get_data()
        result = uc.delete_category(cat.id)
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Warehouse Tests (UC-INV-03)
# ═══════════════════════════════════════════════════════════════════

class TestWarehouseCRUD:
    def test_create(self, repo):
        data = _make_warehouse_data()
        wh = Warehouse(**data)
        result = repo.create_warehouse(wh)
        assert result.is_success()
        assert result.get_data().code == "KHO01"

    def test_create_duplicate_code(self, repo, warehouse):
        data = _make_warehouse_data(code=warehouse.code)
        wh = Warehouse(**data)
        result = repo.create_warehouse(wh)
        assert result.is_failure()

    def test_get(self, repo, warehouse):
        w = repo.get_warehouse(warehouse.id)
        assert w is not None

    def test_list(self, repo, warehouse):
        whs = repo.list_warehouses()
        assert len(whs) >= 1

    def test_update(self, repo, warehouse):
        result = repo.update_warehouse(warehouse.id, name="Updated WH")
        assert result.is_success()

    def test_delete(self, repo, warehouse):
        result = repo.delete_warehouse(warehouse.id)
        assert result.is_success()

    def test_create_uc(self, uc):
        data = _make_warehouse_data(code="KHO-A", name="Kho A")
        result = uc.create_warehouse(**data)
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Item Tests (UC-INV-02)
# ═══════════════════════════════════════════════════════════════════

class TestItemCRUD:
    def test_create(self, repo, category):
        data = _make_item_data(category_id=category.id)
        item = InventoryItem(**data)
        result = repo.create_item(item)
        assert result.is_success()
        assert result.get_data().code == "VT001"

    def test_create_duplicate_code(self, repo, category, item):
        data = _make_item_data(category_id=category.id, code=item.code)
        i = InventoryItem(**data)
        result = repo.create_item(i)
        assert result.is_failure()

    def test_get(self, repo, item):
        it = repo.get_item(item.id)
        assert it is not None
        assert it.id == item.id

    def test_list(self, repo, item):
        items = repo.list_items()
        assert len(items) >= 1

    def test_list_by_category(self, repo, category, item):
        items = repo.list_items(category_id=category.id)
        assert len(items) >= 1

    def test_list_search(self, repo, item):
        items = repo.list_items(search="VT001")
        assert len(items) >= 1

    def test_update(self, repo, item):
        result = repo.update_item(item.id, name="Updated Item")
        assert result.is_success()
        assert repo.get_item(item.id).name == "Updated Item"

    def test_adjust_stock(self, repo, item):
        result = repo.adjust_stock(item.id, 1, Decimal("50"))
        assert result.is_success()
        assert repo.get_item(item.id).current_stock == Decimal("50")

    def test_adjust_stock_negative_allowed(self, repo, category):
        wh = Warehouse(**_make_warehouse_data(code="KHO-NEG", name="Neg WH",
                                               allow_negative_stock=True))
        wh_result = repo.create_warehouse(wh)
        wh_id = wh_result.get_data().id
        item_data = _make_item_data(category_id=category.id, code="VT-NEG", name="Neg Item",
                                     current_stock=Decimal("10"))
        item = InventoryItem(**item_data)
        item_result = repo.create_item(item)
        it = item_result.get_data()
        result = repo.adjust_stock(it.id, wh_id, Decimal("-20"))
        assert result.is_success()


class TestItemUseCases:
    def test_create_uc(self, uc, category):
        result = uc.create_item(code="VT-UC", name="UC Item", category_id=category.id)
        assert result.is_success()

    def test_list_filter_type(self, uc, item):
        items = uc.list_items(inventory_type="merchandise")
        assert len(items) >= 1


# ═══════════════════════════════════════════════════════════════════
# Batch Tests (UC-INV-07)
# ═══════════════════════════════════════════════════════════════════

class TestBatchCRUD:
    def test_create(self, repo, item):
        b = InventoryBatch(item_id=item.id, batch_code="LÔ-A",
                            received_date=date(2026, 6, 1),
                            quantity=Decimal("50"), remaining_quantity=Decimal("50"),
                            unit_cost=Decimal("10000"), total_cost=Decimal("500000"))
        result = repo.create_batch(b)
        assert result.is_success()
        assert result.get_data().batch_code == "LÔ-A"

    def test_duplicate_batch_code(self, repo, item, batch):
        b = InventoryBatch(item_id=item.id, batch_code=batch.batch_code,
                            received_date=date(2026, 6, 1))
        result = repo.create_batch(b)
        assert result.is_failure()

    def test_list_by_item(self, repo, item, batch):
        batches = repo.list_batches(item_id=item.id)
        assert len(batches) >= 1

    def test_update_quantity(self, repo, batch):
        result = repo.update_batch_quantity(batch.id, Decimal("-10"))
        assert result.is_success()

    def test_get_batch_uc(self, uc, batch):
        result = uc.get_batch(batch.id)
        assert result.is_success()


class TestSerialCRUD:
    def test_create(self, repo, item):
        s = SerialNumber(item_id=item.id, serial_code="SN-001")
        result = repo.create_serial(s)
        assert result.is_success()

    def test_duplicate_serial(self, repo, item):
        s = SerialNumber(item_id=item.id, serial_code="SN-002")
        repo.create_serial(s)
        s2 = SerialNumber(item_id=item.id, serial_code="SN-002")
        result = repo.create_serial(s2)
        assert result.is_failure()

    def test_list_serials(self, repo, item):
        serials = repo.list_serials(item_id=item.id)
        assert len(serials) >= 0

    def test_create_serial_uc(self, uc, item):
        result = uc.create_serial(item_id=item.id, serial_code="SN-UC-001")
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Receipt Tests (UC-INV-04)
# ═══════════════════════════════════════════════════════════════════

class TestReceiptCRUD:
    def test_create(self, repo, item, warehouse):
        line = InventoryReceiptLine(item_id=item.id, warehouse_id=warehouse.id,
                                     quantity=Decimal("100"), unit_price=Decimal("50000"))
        receipt = InventoryReceipt(receipt_code="NK-TEST-01",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=[line])
        result = repo.create_receipt(receipt)
        assert result.is_success()
        r = result.get_data()
        assert r.receipt_code == "NK-TEST-01"
        assert len(r.lines) == 1

    def test_get(self, repo, item, warehouse):
        line = InventoryReceiptLine(item_id=item.id, warehouse_id=warehouse.id,
                                     quantity=Decimal("10"), unit_price=Decimal("50000"))
        receipt = InventoryReceipt(receipt_code="NK-GET",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=[line])
        result = repo.create_receipt(receipt)
        r = repo.get_receipt(result.get_data().id)
        assert r is not None

    def test_list(self, repo, item, warehouse):
        line = InventoryReceiptLine(item_id=item.id, warehouse_id=warehouse.id,
                                     quantity=Decimal("5"), unit_price=Decimal("50000"))
        receipt = InventoryReceipt(receipt_code="NK-LIST",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=[line])
        repo.create_receipt(receipt)
        receipts, total = repo.list_receipts()
        assert total >= 1

    def test_post(self, repo, item, warehouse):
        line = InventoryReceiptLine(item_id=item.id, warehouse_id=warehouse.id,
                                     quantity=Decimal("100"), unit_price=Decimal("50000"))
        receipt = InventoryReceipt(receipt_code="NK-POST",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=[line])
        result = repo.create_receipt(receipt)
        assert result.is_success()
        r = result.get_data()
        result = repo.post_receipt(r.id, gl_ref="GL-001")
        assert result.is_success()
        assert result.get_data().is_posted is True

    def test_double_post_fails(self, repo, item, warehouse):
        line = InventoryReceiptLine(item_id=item.id, warehouse_id=warehouse.id,
                                     quantity=Decimal("10"), unit_price=Decimal("10000"))
        receipt = InventoryReceipt(receipt_code="NK-DBL",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=[line])
        result = repo.create_receipt(receipt)
        r = result.get_data()
        repo.post_receipt(r.id)
        result = repo.post_receipt(r.id)
        assert result.is_failure()


class TestReceiptUseCases:
    def test_create_and_post_uc(self, uc, item, warehouse):
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "quantity": 200, "unit_price": 50000}]
        result = uc.create_receipt(receipt_code="NK-UC-POST",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=lines)
        assert result.is_success()
        receipt = result.get_data()
        result = uc.post_receipt(receipt.id)
        assert result.is_success()
        updated_item = uc.get_item(item.id).get_data()
        assert updated_item.current_stock == Decimal("200")


# ═══════════════════════════════════════════════════════════════════
# Issue Tests (UC-INV-05)
# ═══════════════════════════════════════════════════════════════════

class TestIssueCRUD:
    def test_create(self, repo, item, warehouse):
        line = InventoryIssueLine(item_id=item.id, warehouse_id=warehouse.id,
                                   quantity=Decimal("5"), unit_price=Decimal("75000"),
                                   cost_price=Decimal("50000"))
        issue = InventoryIssue(issue_code="XK-TEST-01",
                                issue_date=date(2026, 6, 20),
                                warehouse_id=warehouse.id,
                                lines=[line])
        result = repo.create_issue(issue)
        assert result.is_success()
        assert result.get_data().issue_code == "XK-TEST-01"

    def test_list(self, repo, item, warehouse):
        line = InventoryIssueLine(item_id=item.id, warehouse_id=warehouse.id,
                                   quantity=Decimal("3"), unit_price=Decimal("75000"),
                                   cost_price=Decimal("50000"))
        issue = InventoryIssue(issue_code="XK-LIST",
                                issue_date=date(2026, 6, 20),
                                warehouse_id=warehouse.id,
                                lines=[line])
        repo.create_issue(issue)
        issues, total = repo.list_issues()
        assert total >= 1

    def test_post(self, repo, item, warehouse):
        repo.adjust_stock(item.id, warehouse.id, Decimal("100"))
        line = InventoryIssueLine(item_id=item.id, warehouse_id=warehouse.id,
                                   quantity=Decimal("10"), unit_price=Decimal("75000"),
                                   cost_price=Decimal("50000"))
        issue = InventoryIssue(issue_code="XK-POST",
                                issue_date=date(2026, 6, 20),
                                warehouse_id=warehouse.id,
                                lines=[line])
        result = repo.create_issue(issue)
        r = result.get_data()
        result = repo.post_issue(r.id)
        assert result.is_success()
        assert result.get_data().is_posted is True

    def test_double_post_fails(self, repo, item, warehouse):
        repo.adjust_stock(item.id, warehouse.id, Decimal("50"))
        line = InventoryIssueLine(item_id=item.id, warehouse_id=warehouse.id,
                                   quantity=Decimal("5"), unit_price=Decimal("75000"),
                                   cost_price=Decimal("50000"))
        issue = InventoryIssue(issue_code="XK-DBL",
                                issue_date=date(2026, 6, 20),
                                warehouse_id=warehouse.id,
                                lines=[line])
        result = repo.create_issue(issue)
        r = result.get_data()
        repo.post_issue(r.id)
        result = repo.post_issue(r.id)
        assert result.is_failure()


class TestIssueUseCases:
    def test_create_and_post_uc(self, uc, item, warehouse):
        uc.repo.adjust_stock(item.id, warehouse.id, Decimal("500"))
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "quantity": 50, "unit_price": 75000, "cost_price": 50000}]
        result = uc.create_issue(issue_code="XK-UC-POST",
                                  issue_date=date(2026, 6, 20),
                                  warehouse_id=warehouse.id,
                                  lines=lines)
        assert result.is_success()
        issue = result.get_data()
        result = uc.post_issue(issue.id)
        assert result.is_success()
        updated_item = uc.get_item(item.id).get_data()
        assert updated_item.current_stock == Decimal("450")

    def test_insufficient_stock_fails(self, uc, item, warehouse):
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "quantity": 999999, "unit_price": 75000, "cost_price": 50000}]
        result = uc.create_issue(issue_code="XK-INSUFF",
                                  issue_date=date(2026, 6, 20),
                                  warehouse_id=warehouse.id,
                                  lines=lines)
        assert result.is_success()
        issue = result.get_data()
        result = uc.post_issue(issue.id)
        assert result.is_failure()


# ═══════════════════════════════════════════════════════════════════
# Transfer Tests (UC-INV-06)
# ═══════════════════════════════════════════════════════════════════

class TestTransferCRUD:
    def test_create(self, repo, item):
        wh1 = repo.create_warehouse(Warehouse(**_make_warehouse_data(code="KHO-SRC", name="Source"))).get_data()
        wh2 = repo.create_warehouse(Warehouse(**_make_warehouse_data(code="KHO-DST", name="Dest"))).get_data()
        lines = [InventoryTransferLine(item_id=item.id, quantity=Decimal("10"),
                                        unit_price=Decimal("50000"))]
        transfer = InventoryTransfer(transfer_code="CK-TEST-01",
                                      transfer_date=date(2026, 6, 25),
                                      from_warehouse_id=wh1.id,
                                      to_warehouse_id=wh2.id,
                                      lines=[lines[0]])
        result = repo.create_transfer(transfer)
        assert result.is_success()
        assert result.get_data().transfer_code == "CK-TEST-01"

    def test_post(self, repo, item):
        wh1 = repo.create_warehouse(Warehouse(**_make_warehouse_data(code="KHO-SRC2", name="Src"))).get_data()
        wh2 = repo.create_warehouse(Warehouse(**_make_warehouse_data(code="KHO-DST2", name="Dst"))).get_data()
        repo.adjust_stock(item.id, wh1.id, Decimal("100"))
        lines = [InventoryTransferLine(item_id=item.id, quantity=Decimal("30"),
                                        unit_price=Decimal("50000"))]
        transfer = InventoryTransfer(transfer_code="CK-POST",
                                      transfer_date=date(2026, 6, 25),
                                      from_warehouse_id=wh1.id,
                                      to_warehouse_id=wh2.id,
                                      lines=lines)
        result = repo.create_transfer(transfer)
        r = result.get_data()
        result = repo.post_transfer(r.id)
        assert result.is_success()
        assert result.get_data().is_posted is True


class TestTransferUseCases:
    def test_create_and_post_uc(self, uc, item):
        wh1 = uc.repo.create_warehouse(Warehouse(**_make_warehouse_data(code="KHO-A1", name="A"))).get_data()
        wh2 = uc.repo.create_warehouse(Warehouse(**_make_warehouse_data(code="KHO-B1", name="B"))).get_data()
        uc.repo.adjust_stock(item.id, wh1.id, Decimal("100"))
        lines = [{"item_id": item.id, "quantity": 20, "unit_price": 50000}]
        result = uc.create_transfer(transfer_code="CK-UC-POST",
                                     transfer_date=date(2026, 6, 25),
                                     from_warehouse_id=wh1.id,
                                     to_warehouse_id=wh2.id,
                                     lines=lines)
        assert result.is_success()
        result = uc.post_transfer(result.get_data().id)
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Stock Card / Balance Tests (UC-INV-08)
# ═══════════════════════════════════════════════════════════════════

class TestStockCard:
    def test_get_or_create_card(self, uc, item, warehouse):
        result = uc.get_stock_card(item.id, warehouse.id, "2026-06")
        assert result.is_success()

    def test_list_cards(self, repo, item, warehouse):
        cards = repo.list_stock_cards(item_id=item.id)
        assert len(cards) >= 0

    def test_upsert_card(self, repo, item, warehouse):
        card = StockCard(item_id=item.id, warehouse_id=warehouse.id, period="2026-06",
                          opening_quantity=Decimal("100"), opening_value=Decimal("5000000"),
                          receipt_quantity=Decimal("50"), receipt_value=Decimal("2500000"),
                          closing_quantity=Decimal("150"), closing_value=Decimal("7500000"))
        result = repo.upsert_stock_card(card)
        assert result.period == "2026-06"

    def test_balance(self, uc, item):
        result = uc.get_inventory_balance(item.id)
        assert result.is_success()
        balance = result.get_data()
        assert balance["item_id"] == item.id


# ═══════════════════════════════════════════════════════════════════
# Inventory Check Tests (UC-INV-09)
# ═══════════════════════════════════════════════════════════════════

class TestCheckCRUD:
    def test_create(self, repo, item, warehouse):
        lines = [InventoryCheckLine(item_id=item.id, warehouse_id=warehouse.id,
                                     book_quantity=Decimal("100"),
                                     physical_quantity=Decimal("98"),
                                     unit_price=Decimal("50000"))]
        check = InventoryCheck(check_code="KK-TEST-01",
                                check_date=date(2026, 6, 30),
                                warehouse_id=warehouse.id,
                                lines=lines)
        result = repo.create_check(check)
        assert result.is_success()
        assert result.get_data().check_code == "KK-TEST-01"

    def test_list(self, repo, item, warehouse):
        checks, total = repo.list_checks()
        assert total >= 0

    def test_update_status(self, repo, item, warehouse):
        lines = [InventoryCheckLine(item_id=item.id, warehouse_id=warehouse.id,
                                     book_quantity=Decimal("50"),
                                     physical_quantity=Decimal("50"),
                                     unit_price=Decimal("10000"))]
        check = InventoryCheck(check_code="KK-STATUS",
                                check_date=date(2026, 6, 30),
                                warehouse_id=warehouse.id,
                                lines=lines)
        result = repo.create_check(check)
        r = result.get_data()
        result = repo.update_check_status(r.id, InventoryCheckStatus.COMPLETED)
        assert result.is_success()


class TestCheckUseCases:
    def test_create_and_approve(self, uc, item, warehouse):
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "book_quantity": 100, "physical_quantity": 100, "unit_price": 50000}]
        result = uc.create_check(check_code="KK-UC-APR",
                                  check_date=date(2026, 6, 30),
                                  warehouse_id=warehouse.id,
                                  lines=lines)
        assert result.is_success()
        result = uc.approve_check(result.get_data().id, approved_by="admin")
        assert result.is_success()
        assert result.get_data().status == InventoryCheckStatus.APPROVED


# ═══════════════════════════════════════════════════════════════════
# Adjustment Tests (UC-INV-10)
# ═══════════════════════════════════════════════════════════════════

class TestAdjustmentCRUD:
    def test_create(self, repo, item, warehouse):
        lines = [InventoryAdjustmentLine(item_id=item.id, warehouse_id=warehouse.id,
                                          quantity_change=Decimal("-5"),
                                          unit_price=Decimal("50000"))]
        adj = InventoryAdjustment(adjustment_code="DC-TEST-01",
                                   adjustment_date=date(2026, 6, 30),
                                   warehouse_id=warehouse.id,
                                   adjustment_type=AdjustmentType.WRITE_OFF,
                                   reason="Hao hụt",
                                   lines=lines)
        result = repo.create_adjustment(adj)
        assert result.is_success()
        assert result.get_data().adjustment_code == "DC-TEST-01"

    def test_post(self, repo, item, warehouse):
        repo.adjust_stock(item.id, warehouse.id, Decimal("100"))
        lines = [InventoryAdjustmentLine(item_id=item.id, warehouse_id=warehouse.id,
                                          quantity_change=Decimal("-10"),
                                          unit_price=Decimal("50000"))]
        adj = InventoryAdjustment(adjustment_code="DC-POST",
                                   adjustment_date=date(2026, 6, 30),
                                   warehouse_id=warehouse.id,
                                   adjustment_type=AdjustmentType.DAMAGE,
                                   reason="Hư hỏng",
                                   lines=lines)
        result = repo.create_adjustment(adj)
        r = result.get_data()
        result = repo.post_adjustment(r.id)
        assert result.is_success()


class TestAdjustmentUseCases:
    def test_create_and_post_uc(self, uc, item, warehouse):
        uc.repo.adjust_stock(item.id, warehouse.id, Decimal("500"))
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "quantity_change": -50, "unit_price": 50000}]
        result = uc.create_adjustment(adjustment_code="DC-UC-POST",
                                       adjustment_date=date(2026, 6, 30),
                                       warehouse_id=warehouse.id,
                                       adjustment_type="write_off",
                                       reason="Thanh lý",
                                       lines=lines)
        assert result.is_success()
        result = uc.post_adjustment(result.get_data().id)
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Valuation Tests (UC-INV-11)
# ═══════════════════════════════════════════════════════════════════

class TestValuation:
    def test_moving_average(self, uc, item):
        result = uc.calculate_moving_average(item.id, Decimal("100"), Decimal("55000"))
        assert result.is_success()
        data = result.get_data()
        assert "unit_cost" in data

    def test_revalue(self, uc, item):
        result = uc.revalue_item(item.id, Decimal("48000"))
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# GL Posting Tests (UC-INV-12)
# ═══════════════════════════════════════════════════════════════════

class TestGLPosting:
    def test_get_gl_accounts(self, uc, item):
        result = uc.get_gl_accounts_for_item(item.id)
        assert result.is_success()

    def test_build_receipt_entries(self, uc, item, warehouse):
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "quantity": 100, "unit_price": 50000}]
        result = uc.create_receipt(receipt_code="NK-GL-ENTRY",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=lines)
        receipt = result.get_data()
        result = uc.build_receipt_gl_entries(receipt.id)
        assert result.is_success()
        entries = result.get_data()
        assert len(entries) >= 2

    def test_build_issue_entries(self, uc, item, warehouse):
        uc.repo.adjust_stock(item.id, warehouse.id, Decimal("100"))
        lines = [{"item_id": item.id, "warehouse_id": warehouse.id,
                   "quantity": 10, "unit_price": 75000, "cost_price": 50000}]
        result = uc.create_issue(issue_code="XK-GL-ENTRY",
                                  issue_date=date(2026, 6, 20),
                                  warehouse_id=warehouse.id,
                                  lines=lines)
        issue = result.get_data()
        result = uc.build_issue_gl_entries(issue.id)
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Report Tests (UC-INV-13)
# ═══════════════════════════════════════════════════════════════════

class TestReports:
    def test_inventory_report(self, uc, item):
        result = uc.get_inventory_report()
        assert result.is_success()
        data = result.get_data()
        assert data["total_items"] >= 1

    def test_low_stock_report(self, uc, item):
        result = uc.get_low_stock_report()
        assert result.is_success()

    def test_stock_movement(self, uc, item, warehouse):
        result = uc.get_stock_movement_report(
            item.id, date(2026, 1, 1), date(2026, 12, 31))
        assert result.is_success()


# ═══════════════════════════════════════════════════════════════════
# Import/Export Tests (UC-INV-14)
# ═══════════════════════════════════════════════════════════════════

class TestImportExport:
    def test_export(self, uc, item):
        items = uc.export_items()
        assert len(items) >= 1
        assert items[0]["code"] == item.code

    def test_import(self, uc, category):
        rows = [{"code": "IMP-001", "name": "Imported Item",
                  "category_code": category.code, "unit": "cái",
                  "cost_price": "30000", "unit_price": "35000",
                  "selling_price": "45000", "current_stock": "50"}]
        result = uc.import_items_from_csv(rows)
        assert result.is_success()
        assert result.get_data()["imported"] >= 1


# ═══════════════════════════════════════════════════════════════════
# Dashboard Tests (UC-INV-15)
# ═══════════════════════════════════════════════════════════════════

class TestDashboard:
    def test_dashboard(self, uc, item, warehouse):
        dash = uc.get_dashboard()
        assert dash["total_items"] >= 1
        assert dash["total_warehouses"] >= 1
        assert "total_stock_value" in dash


# ═══════════════════════════════════════════════════════════════════
# Edge Case Tests
# ═══════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_create_receipt_no_lines_raises(self, uc, warehouse):
        result = uc.create_receipt(receipt_code="NK-NO-LINES",
                                    receipt_date=date(2026, 6, 15),
                                    warehouse_id=warehouse.id,
                                    lines=[])
        assert result.is_failure()

    def test_create_issue_no_lines_raises(self, uc, warehouse):
        result = uc.create_issue(issue_code="XK-NO-LINES",
                                  issue_date=date(2026, 6, 20),
                                  warehouse_id=warehouse.id,
                                  lines=[])
        assert result.is_failure()

    def test_get_nonexistent_receipt(self, uc):
        result = uc.get_receipt(99999)
        assert result.is_failure()

    def test_get_nonexistent_issue(self, uc):
        result = uc.get_issue(99999)
        assert result.is_failure()

    def test_get_nonexistent_item(self, uc):
        result = uc.get_item(99999)
        assert result.is_failure()

    def test_get_nonexistent_warehouse(self, uc):
        result = uc.get_warehouse(99999)
        assert result.is_failure()

    def test_create_adjustment_no_lines_raises(self, uc, warehouse):
        result = uc.create_adjustment(adjustment_code="DC-NO-LINES",
                                       adjustment_date=date(2026, 6, 30),
                                       warehouse_id=warehouse.id,
                                       adjustment_type="write_off",
                                       reason="Test",
                                       lines=[])
        assert result.is_failure()

    def test_list_with_filters(self, uc, item):
        items = uc.list_items(status="active")
        assert len(items) >= 1
        items = uc.list_items(inventory_type="merchandise")
        assert len(items) >= 1

    def test_list_receipts_pagination(self, repo, item, warehouse):
        for i in range(3):
            line = InventoryReceiptLine(item_id=item.id, warehouse_id=warehouse.id,
                                         quantity=Decimal("10"), unit_price=Decimal("50000"))
            receipt = InventoryReceipt(
                receipt_code=f"NK-PAG-{i:03d}",
                receipt_date=date(2026, 6, 15),
                warehouse_id=warehouse.id,
                lines=[line],
            )
            repo.create_receipt(receipt)
        receipts, total = repo.list_receipts(limit=2)
        assert len(receipts) <= 2
        assert total >= 3

    def test_list_issues_pagination(self, repo, item, warehouse):
        repo.adjust_stock(item.id, warehouse.id, Decimal("1000"))
        for i in range(3):
            line = InventoryIssueLine(item_id=item.id, warehouse_id=warehouse.id,
                                       quantity=Decimal("5"), unit_price=Decimal("75000"),
                                       cost_price=Decimal("50000"))
            issue = InventoryIssue(
                issue_code=f"XK-PAG-{i:03d}",
                issue_date=date(2026, 6, 20),
                warehouse_id=warehouse.id,
                lines=[line],
            )
            repo.create_issue(issue)
        issues, total = repo.list_issues(limit=2)
        assert len(issues) <= 2
        assert total >= 3

    def test_get_item_gl_accounts(self, repo, item, category):
        accounts = repo.get_item_gl_accounts(item.id)
        assert accounts.get("gl_inventory_account") == "152"

    def test_dashboard_metrics(self, repo, item, warehouse):
        dash = repo.get_dashboard()
        assert isinstance(dash["total_items"], int)
        assert isinstance(dash["total_warehouses"], int)
