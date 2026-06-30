from decimal import Decimal
from datetime import date, datetime
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain import (
    CCDCType, AllocationMethod, CCDCStatus, AllocationStatus,
    TransactionType, ResponsibilityType,
    CCategory, CCDCItem, CCDCAllocation, CCDCAllocationLine,
    CCDCTransaction, CCDCTransfer, CCDCInventory, CCDCInventoryLine,
    CCDCWriteOff, CCDCSparePart, Result, AccountError,
)
from domain.cc import InventoryStatus as CCInventoryStatus
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import Base
from infrastructure.models.cc_models import (
    CCategoryModel, CCDCItemModel, CCDCAllocationModel, CCDCAllocationLineModel,
    CCDCTransactionModel, CCDCTransferModel, CCDCInventoryModel,
    CCDCInventoryLineModel, CCDCWriteOffModel, CCDCSparePartModel,
    CCDCImportLogModel, CCDCStatusDB, AllocationMethodDB,
)
from infrastructure.repositories.cc_repository import CCRepository
from use_cases.cc import CCUseCases


def _make_category_data(code="VP", name="Văn phòng phẩm", **kw) -> dict:
    data = {"code": code, "name": name,
            "default_allocation_method": AllocationMethod.one_time.value,
            "gl_asset_account": "153", "gl_expense_account": "627"}
    data.update(kw)
    return data


def _make_item_data(category_id: int, code="CC001", name="Búa", **kw) -> dict:
    data = {"code": code, "name": name, "category_id": category_id,
            "cc_type": CCDCType.tool.value, "unit": "cái",
            "quantity": Decimal("5"), "unit_price": Decimal("100000"),
            "total_cost": Decimal("500000"),
            "purchase_date": date(2026, 1, 15)}
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
    return CCRepository(session)


@pytest.fixture
def uc(session):
    return CCUseCases(session)


@pytest.fixture
def category(repo):
    data = _make_category_data()
    cat = CCategory(**data)
    return repo.create_category(cat).get_data()


class TestCategoryCRUD:
    def test_create_category(self, repo, session):
        data = _make_category_data(code="DC-SX", name="Dụng cụ sản xuất")
        cat = CCategory(**data)
        result = repo.create_category(cat)
        assert result.is_success()
        c = result.get_data()
        assert c.code == "DC-SX"
        assert c.default_allocation_method == AllocationMethod.one_time
        session.flush()

    def test_create_duplicate_code(self, repo, category):
        data = _make_category_data(code=category.code, name="Khác")
        cat = CCategory(**data)
        result = repo.create_category(cat)
        assert result.is_failure()
        assert result.error.msgid == ErrorCodes.CC_CATEGORY_CODE_DUPLICATE

    def test_get_category(self, repo, category):
        c = repo.get_category(category.id)
        assert c is not None
        assert c.id == category.id

    def test_get_category_not_found(self, repo):
        c = repo.get_category(9999)
        assert c is None

    def test_update_category(self, repo, session, category):
        result = repo.update_category(category.id, name="Văn phòng phẩm mới")
        assert result.is_success()
        c = result.get_data()
        assert c.name == "Văn phòng phẩm mới"
        session.flush()

    def test_delete_category(self, repo, session):
        data = _make_category_data(code="DEL", name="Xóa")
        cat = CCategory(**data)
        result = repo.create_category(cat)
        c = result.get_data()
        del_result = repo.delete_category(c.id)
        assert del_result.is_success()
        session.flush()

    def test_delete_category_with_items_fails(self, repo, session, category):
        item_data = _make_item_data(category.id)
        item = CCDCItem(**item_data)
        repo.create_item(item)
        session.flush()
        result = repo.delete_category(category.id)
        assert result.is_failure()
        assert result.error.msgid == ErrorCodes.CC_CATEGORY_HAS_ITEMS


class TestItemCRUD:
    def test_create_item(self, repo, session, category):
        data = _make_item_data(category.id)
        item = CCDCItem(**data)
        result = repo.create_item(item)
        assert result.is_success()
        i = result.get_data()
        assert i.code == "CC001"
        assert i.status == CCDCStatus.in_stock
        session.flush()

    def test_create_duplicate_code(self, repo, session, category):
        data = _make_item_data(category.id)
        item = CCDCItem(**data)
        repo.create_item(item)
        session.flush()
        data2 = _make_item_data(category.id, code="CC001")
        item2 = CCDCItem(**data2)
        result = repo.create_item(item2)
        assert result.is_failure()

    def test_get_item(self, repo, session, category):
        data = _make_item_data(category.id)
        result = repo.create_item(CCDCItem(**data))
        item = result.get_data()
        session.flush()
        fetched = repo.get_item(item.id)
        assert fetched is not None
        assert fetched.code == "CC001"

    def test_update_item(self, repo, session, category):
        result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = result.get_data()
        session.flush()
        up = repo.update_item(item.id, name="Búa mới")
        assert up.is_success()
        assert up.get_data().name == "Búa mới"

    def test_list_items_by_category(self, repo, session, category):
        repo.create_item(CCDCItem(**_make_item_data(category.id, code="CC010")))
        repo.create_item(CCDCItem(**_make_item_data(category.id, code="CC011")))
        session.flush()
        items = repo.list_items(category_id=category.id)
        assert len(items) >= 2


class TestAllocation:
    def test_create_one_time_allocation(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()

        alloc = CCDCAllocation(
            item_id=item.id, allocation_method=AllocationMethod.one_time,
            total_amount=Decimal("500000"), start_period="2026-01",
            gl_account_credit="153", gl_account_debit="627",
        )
        result = repo.create_allocation(alloc)
        assert result.is_success()
        session.flush()

    def test_list_allocations(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        alloc = CCDCAllocation(
            item_id=item.id, allocation_method=AllocationMethod.one_time,
            total_amount=Decimal("500000"), start_period="2026-01",
        )
        repo.create_allocation(alloc)
        session.flush()
        allocs = repo.list_allocations(item_id=item.id)
        assert len(allocs) >= 1


class TestTransaction:
    def test_create_receipt(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        txn = CCDCTransaction(
            item_id=item.id, transaction_type=TransactionType.receipt,
            quantity=Decimal("10"), unit_price=Decimal("100000"),
            total_amount=Decimal("1000000"),
            transaction_date=date(2026, 1, 15), period="2026-01",
        )
        result = repo.create_transaction(txn)
        assert result.is_success()
        session.flush()

    def test_list_transactions(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        txns = repo.list_transactions(item_id=item.id)
        assert isinstance(txns, list)


class TestTransfer:
    def test_create_transfer(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        transfer = CCDCTransfer(
            item_id=item.id, transfer_date=date(2026, 2, 1),
            to_department_id=2, reason="Chuyển kho",
        )
        result = repo.create_transfer(transfer)
        assert result.is_success()
        session.flush()


class TestInventory:
    def test_create_inventory(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        line = CCDCInventoryLine(inventory_id=0, item_id=item.id,
                                  book_quantity=Decimal("5"),
                                  physical_quantity=Decimal("5"))
        inv = CCDCInventory(inventory_date=date(2026, 6, 30), lines=[line])
        result = repo.create_inventory(inv)
        assert result.is_success()
        session.flush()

    def test_get_inventory(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        line = CCDCInventoryLine(inventory_id=0, item_id=item.id,
                                  book_quantity=Decimal("5"),
                                  physical_quantity=Decimal("5"))
        inv = CCDCInventory(inventory_date=date(2026, 6, 30), lines=[line])
        result = repo.create_inventory(inv)
        inv_id = result.get_data().id
        session.flush()
        fetched = repo.get_inventory(inv_id)
        assert fetched is not None
        assert fetched.lines is not None


class TestWriteOff:
    def test_create_write_off(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        wo = CCDCWriteOff(
            item_id=item.id, write_off_date=date(2026, 3, 1),
            quantity=Decimal("1"), remaining_value=Decimal("200000"),
            reason="Hỏng",
        )
        result = repo.create_write_off(wo)
        assert result.is_success()
        session.flush()

    def test_list_write_offs(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        wos = repo.list_write_offs(item_id=item.id)
        assert isinstance(wos, list)


class TestSparePart:
    def test_create_spare_part(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        sp = CCDCSparePart(item_id=item.id, code="PK001", name="Phụ kiện A",
                           quantity=Decimal("10"), unit_price=Decimal("50000"))
        result = repo.create_spare_part(sp)
        assert result.is_success()
        session.flush()

    def test_get_spare_part(self, repo, session, category):
        item_result = repo.create_item(CCDCItem(**_make_item_data(category.id)))
        item = item_result.get_data()
        session.flush()
        sp = CCDCSparePart(item_id=item.id, code="PK002", name="Phụ kiện B",
                           quantity=Decimal("5"), unit_price=Decimal("30000"))
        result = repo.create_spare_part(sp)
        sp_id = result.get_data().id
        session.flush()
        fetched = repo.get_spare_part(sp_id)
        assert fetched is not None
        assert fetched.code == "PK002"


class TestUseCases:
    def test_create_category_uc(self, uc, session):
        result = uc.create_category(_make_category_data(code="UC1", name="UC Test"))
        assert result.is_success()
        assert result.get_data().code == "UC1"
        session.flush()

    def test_create_item_uc(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="UC2", name="UC Cat"))
        cat = cat_result.get_data()
        session.flush()
        data = _make_item_data(cat.id, code="UC-ITEM1")
        result = uc.create_item(data)
        assert result.is_success()
        assert result.get_data().code == "UC-ITEM1"
        session.flush()

    def test_create_allocation_uc(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="UC3", name="UC Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="UC-ITEM2",
                                                      total_cost=Decimal("1200000")))
        item = item_result.get_data()
        session.flush()
        alloc_data = {
            "item_id": item.id,
            "allocation_method": AllocationMethod.multi_period.value,
            "total_amount": Decimal("1200000"),
            "start_period": "2026-01",
            "total_periods": 12,
        }
        result = uc.create_allocation(alloc_data)
        assert result.is_success()
        payload = result.get_data()
        assert "allocation" in payload
        assert "lines" in payload
        assert len(payload["lines"]) == 12
        session.flush()

    def test_create_transaction_uc(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="UC4", name="UC Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="UC-ITEM3",
                                                      quantity=Decimal("10")))
        item = item_result.get_data()
        session.flush()
        txn_data = {
            "item_id": item.id, "transaction_type": TransactionType.issuance.value,
            "quantity": Decimal("3"), "unit_price": Decimal("100000"),
            "total_amount": Decimal("300000"),
            "transaction_date": "2026-02-01", "period": "2026-02",
        }
        result = uc.create_transaction(txn_data)
        assert result.is_success()

    def test_create_transfer_uc(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="UC5", name="UC Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="UC-ITEM4"))
        item = item_result.get_data()
        session.flush()
        transfer_data = {
            "item_id": item.id, "transfer_date": "2026-03-01",
            "to_department_id": 3, "reason": "Chuyển giao",
        }
        result = uc.create_transfer(transfer_data)
        assert result.is_success()

    def test_create_write_off_uc(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="UC6", name="UC Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="UC-ITEM5"))
        item = item_result.get_data()
        session.flush()
        wo_data = {
            "item_id": item.id, "write_off_date": "2026-04-01",
            "quantity": Decimal("1"), "remaining_value": Decimal("100000"),
            "reason": "Thanh lý",
        }
        result = uc.create_write_off(wo_data)
        assert result.is_success()

    def test_report_by_department(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="UC7", name="UC Cat"))
        cat = cat_result.get_data()
        session.flush()
        result = uc.report_by_department(1)
        assert result.is_success()
        assert "items" in result.get_data()
        assert "total_value" in result.get_data()

    def test_dashboard_summary(self, uc, session):
        result = uc.dashboard_summary()
        assert result.is_success()
        data = result.get_data()
        assert "total_items" in data
        assert "total_value" in data


class TestImportExport:
    def test_import_items(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="IMP1", name="Import Cat"))
        cat = cat_result.get_data()
        session.flush()
        rows = [
            {"code": "IMP-ITEM1", "name": "Item 1", "category_code": cat.code,
             "category_id": cat.id, "unit": "cái"},
        ]
        result = uc.import_items(rows, "test.xlsx")
        assert result.is_success()
        data = result.get_data()
        assert data["success"] == 1
        assert data["total"] == 1
        session.flush()

    def test_export_items(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="EXP1", name="Export Cat"))
        cat = cat_result.get_data()
        session.flush()
        uc.create_item(_make_item_data(cat.id, code="EXP-ITEM1"))
        session.flush()
        result = uc.export_items()
        assert result.is_success()
        rows = result.get_data()
        assert len(rows) >= 1


class TestUseCaseEdgeCases:
    def test_create_item_missing_category(self, uc):
        result = uc.create_item({"code": "MISS", "name": "No Cat", "category_id": 9999})
        assert result.is_failure()

    def test_create_allocation_exceeds_cost(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="EDGE1", name="Edge Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="EDGE-ITEM1",
                                                      total_cost=Decimal("100000")))
        item = item_result.get_data()
        session.flush()
        alloc_data = {
            "item_id": item.id,
            "allocation_method": AllocationMethod.one_time.value,
            "total_amount": Decimal("200000"),
            "start_period": "2026-01",
        }
        result = uc.create_allocation(alloc_data)
        assert result.is_failure()

    def test_insufficient_quantity(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="EDGE2", name="Edge Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="EDGE-ITEM2",
                                                      quantity=Decimal("2")))
        item = item_result.get_data()
        session.flush()
        txn_data = {
            "item_id": item.id, "transaction_type": TransactionType.issuance.value,
            "quantity": Decimal("10"), "unit_price": Decimal("1000"),
            "total_amount": Decimal("10000"),
            "transaction_date": "2026-02-01", "period": "2026-02",
        }
        result = uc.create_transaction(txn_data)
        assert result.is_failure()

    def test_write_off_already_disposed(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="EDGE3", name="Edge Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="EDGE-ITEM3"))
        item = item_result.get_data()
        session.flush()
        wo1 = {"item_id": item.id, "write_off_date": "2026-04-01",
               "quantity": Decimal("1"), "remaining_value": Decimal("100000"),
               "reason": "Hỏng"}
        uc.create_write_off(wo1)
        session.flush()
        wo2 = {"item_id": item.id, "write_off_date": "2026-05-01",
               "quantity": Decimal("1"), "remaining_value": Decimal("50000"),
               "reason": "Hỏng tiếp"}
        result = uc.create_write_off(wo2)
        assert result.is_failure()

    def test_inventory_resolved_twice(self, uc, session):
        cat_result = uc.create_category(_make_category_data(code="EDGE4", name="Edge Cat"))
        cat = cat_result.get_data()
        session.flush()
        item_result = uc.create_item(_make_item_data(cat.id, code="EDGE-ITEM4"))
        item = item_result.get_data()
        session.flush()
        inv_data = {"inventory_date": "2026-06-30"}
        lines = [{"item_id": item.id, "book_quantity": Decimal("5"),
                   "physical_quantity": Decimal("5")}]
        result = uc.create_inventory(inv_data, lines)
        assert result.is_success(), f"create_inventory failed: {result.error}"
        inv = result.get_data()
        session.flush()
        uc.resolve_inventory(inv.id, "OK")
        session.flush()
        result2 = uc.resolve_inventory(inv.id, "Again")
        assert result2.is_failure()
