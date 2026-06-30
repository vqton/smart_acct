from decimal import Decimal
from datetime import date, datetime
import pytest

from domain.fs import (
    FinancialStatementType, FSStatus, FSCashFlowMethod,
    FSLineItem, FinancialStatement, FSAccountMapping,
    FSConsolidationGroup, FSConsolidationMember,
)
from domain.common import ValidationError
from infrastructure.repositories.fs_repository import FSRepository
from infrastructure.models.fs_models import Base

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

pytestmark = pytest.mark.skipif(not HAS_SQLALCHEMY, reason="SQLAlchemy not available")


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    s = TestSession()
    yield s
    s.close()


@pytest.fixture(scope="function")
def repo(session):
    return FSRepository(session)


def _make_fs(period="2026-06", stmt_type=FinancialStatementType.BALANCE_SHEET_GC):
    return FinancialStatement(
        entity_id=1, period=period, statement_type=stmt_type,
    )


def _make_fs_with_lines():
    fs = _make_fs()
    fs.lines.append(FSLineItem(
        ma_so="110", ten_chi_tieu="Tiền", so_thu_tu=1,
        current_year=Decimal("100000000"),
    ))
    fs.lines.append(FSLineItem(
        ma_so="120", ten_chi_tieu="Phải thu", so_thu_tu=2,
        current_year=Decimal("200000000"),
    ))
    return fs


class TestStatementCRUD:
    def test_create(self, repo):
        result = repo.create_statement(_make_fs())
        assert result.is_success()
        fs = result.get_data()
        assert fs.id is not None
        assert fs.status == FSStatus.DRAFT
        assert fs.version == 1

    def test_create_with_lines(self, repo):
        result = repo.create_statement(_make_fs_with_lines())
        assert result.is_success()
        fs = result.get_data()
        assert len(fs.lines) == 2

    def test_get_by_id(self, repo):
        r = repo.create_statement(_make_fs())
        fs = repo.get_statement(r.get_data().id)
        assert fs is not None
        assert fs.period == "2026-06"

    def test_get_by_id_not_found(self, repo):
        assert repo.get_statement(9999) is None

    def test_list(self, repo):
        for i in range(3):
            repo.create_statement(_make_fs(period=f"2026-0{i+1}"))
        results = repo.list_statements()
        assert len(results) == 3

    def test_list_filter_by_type(self, repo):
        repo.create_statement(_make_fs(stmt_type=FinancialStatementType.BALANCE_SHEET_GC))
        repo.create_statement(_make_fs(stmt_type=FinancialStatementType.INCOME_STATEMENT_GC))
        results = repo.list_statements(
            statement_type=FinancialStatementType.BALANCE_SHEET_GC)
        assert len(results) == 1

    def test_list_filter_by_status(self, repo):
        repo.create_statement(_make_fs())
        results = repo.list_statements(status=FSStatus.DRAFT)
        assert len(results) == 1
        results = repo.list_statements(status=FSStatus.SIGNED)
        assert len(results) == 0

    def test_list_filter_by_period(self, repo):
        repo.create_statement(_make_fs(period="2026-06"))
        repo.create_statement(_make_fs(period="2026-12"))
        results = repo.list_statements(period="2026-06")
        assert len(results) == 1

    def test_list_empty(self, repo):
        assert len(repo.list_statements()) == 0

    def test_list_with_limit(self, repo):
        for i in range(5):
            repo.create_statement(_make_fs(period=f"2026-0{i+1}"))
        results = repo.list_statements(limit=2)
        assert len(results) == 2

    def test_delete(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        result = repo.delete_statement(fs_id)
        assert result.is_success()
        assert repo.get_statement(fs_id) is None

    def test_delete_not_found(self, repo):
        result = repo.delete_statement(9999)
        assert not result.is_success()

    def test_line_items_cascade_on_delete(self, repo, session):
        r = repo.create_statement(_make_fs_with_lines())
        fs_id = r.get_data().id
        repo.delete_statement(fs_id)
        session.flush()
        from infrastructure.models.fs_models import FSLineItemModel
        remaining = session.query(FSLineItemModel).count()
        assert remaining == 0


class TestApprovalWorkflow:
    def _create(self, repo):
        r = repo.create_statement(_make_fs())
        return r.get_data().id

    def test_submit(self, repo):
        fs_id = self._create(repo)
        result = repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        assert result.is_success()
        fs = result.get_data()
        assert fs.status == FSStatus.IN_REVIEW

    def test_submit_then_review(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        result = repo.update_statement_status(fs_id, FSStatus.REVIEWED, "bgd")
        assert result.is_success()
        assert result.get_data().status == FSStatus.REVIEWED

    def test_full_flow(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "bgd")
        repo.update_statement_status(fs_id, FSStatus.APPROVED, "giamdoc")
        r = repo.update_statement_status(fs_id, FSStatus.SIGNED, "giamdoc")
        assert r.is_success()
        assert r.get_data().status == FSStatus.SIGNED

    def test_reject_from_submit(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        r = repo.update_statement_status(fs_id, FSStatus.REJECTED, "bgd", "Sai số liệu")
        assert r.is_success()
        assert r.get_data().status == FSStatus.REJECTED

    def test_reject_then_resubmit(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        repo.update_statement_status(fs_id, FSStatus.REJECTED, "bgd")
        r = repo.update_statement_status(fs_id, FSStatus.DRAFT, "kttruong")
        assert r.is_success()
        # now can submit again
        r = repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        assert r.is_success()

    def test_invalid_transition(self, repo):
        fs_id = self._create(repo)
        r = repo.update_statement_status(fs_id, FSStatus.SIGNED, "giamdoc")
        assert not r.is_success()

    def test_approval_sets_approved_by(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "bgd")
        r = repo.update_statement_status(fs_id, FSStatus.APPROVED, "giamdoc")
        assert r.get_data().approved_by == "giamdoc"
        assert r.get_data().approval_date is not None

    def test_sign_sets_signed_by(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "bgd")
        repo.update_statement_status(fs_id, FSStatus.APPROVED, "giamdoc")
        r = repo.update_statement_status(fs_id, FSStatus.SIGNED, "giamdoc")
        assert r.get_data().signed_by == "giamdoc"

    def test_amend_from_signed(self, repo):
        fs_id = self._create(repo)
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "bgd")
        repo.update_statement_status(fs_id, FSStatus.APPROVED, "giamdoc")
        repo.update_statement_status(fs_id, FSStatus.SIGNED, "giamdoc")
        r = repo.update_statement_status(fs_id, FSStatus.AMENDED, "kttruong")
        assert r.is_success()

    def test_not_found(self, repo):
        r = repo.update_statement_status(9999, FSStatus.IN_REVIEW, "user")
        assert not r.is_success()


class TestAuditLog:
    def _create_and_submit(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        return fs_id

    def test_log_created_on_status_change(self, repo):
        fs_id = self._create_and_submit(repo)
        logs = repo.get_audit_log(fs_id)
        assert len(logs) >= 1

    def test_log_details(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong", "Trình duyệt")
        logs = repo.get_audit_log(fs_id)
        log = logs[0]
        assert log["action"] == "IN_REVIEW"
        assert log["user"] == "kttruong"

    def test_log_order(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "kttruong")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "bgd")
        logs = repo.get_audit_log(fs_id)
        assert len(logs) == 2
        assert logs[0]["action"] == "IN_REVIEW"
        assert logs[1]["action"] == "REVIEWED"

    def test_manual_log(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        repo.log_audit(fs_id, "CREATED", "system", "B01-DN generated")
        logs = repo.get_audit_log(fs_id)
        assert len(logs) == 1
        assert logs[0]["action"] == "CREATED"

    def test_log_empty(self, repo):
        assert repo.get_audit_log(9999) == []


class TestVersioning:
    def test_version_starts_at_one(self, repo):
        r = repo.create_statement(_make_fs())
        assert r.get_data().version == 1

    def test_increment_version(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "user")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "user")
        repo.update_statement_status(fs_id, FSStatus.APPROVED, "user")
        repo.update_statement_status(fs_id, FSStatus.SIGNED, "user")
        repo.update_statement_status(fs_id, FSStatus.AMENDED, "user")
        repo.increment_version(fs_id)
        fs = repo.get_statement(fs_id)
        assert fs.version == 2

    def test_increment_not_found(self, repo):
        r = repo.increment_version(9999)
        assert not r.is_success()


class TestAccountMappings:
    def test_create_mapping(self, repo):
        m = FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        r = repo.create_mapping(m)
        assert r.is_success()

    def test_get_mappings(self, repo):
        m = FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        repo.create_mapping(m)
        results = repo.get_mappings(statement_type=FinancialStatementType.BALANCE_SHEET_GC)
        assert len(results) >= 1

    def test_get_mappings_filter_by_ma_so(self, repo):
        repo.create_mapping(FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        ))
        repo.create_mapping(FSAccountMapping(
            fs_ma_so="120", account_code="1121",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        ))
        results = repo.get_mappings(
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
            fs_ma_so="110",
        )
        assert len(results) == 1

    def test_duplicate_mapping_fails(self, repo):
        m = FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        repo.create_mapping(m)
        r = repo.create_mapping(m)
        assert not r.is_success()

    def test_delete_mapping(self, repo):
        m = FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        r = repo.create_mapping(m)
        d = repo.delete_mapping(r.get_data().id)
        assert d.is_success()

    def test_delete_mapping_not_found(self, repo):
        r = repo.delete_mapping(9999)
        assert not r.is_success()

    def test_get_mapping_for_account(self, repo):
        repo.create_mapping(FSAccountMapping(
            fs_ma_so="110", account_code="1111",
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        ))
        results = repo.get_mapping_for_account(
            "1111", FinancialStatementType.BALANCE_SHEET_GC)
        assert len(results) == 1
        assert results[0].fs_ma_so == "110"


class TestPriorPeriod:
    def test_no_prior_period(self, repo):
        r = repo.create_statement(_make_fs(period="2026-06"))
        prior = repo.get_prior_period_fs(
            "2026-12", FinancialStatementType.BALANCE_SHEET_GC, 1)
        assert prior is None

    def test_with_prior_period(self, repo):
        repo.create_statement(_make_fs(period="2026-06"))
        # need approved/signed status for prior to be found
        r = repo.create_statement(_make_fs(period="2026-12"))
        fs_id = r.get_data().id
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "u")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "u")
        repo.update_statement_status(fs_id, FSStatus.APPROVED, "u")
        prior = repo.get_prior_period_fs(
            "2026-12", FinancialStatementType.BALANCE_SHEET_GC, 1)
        # prior period is 2026-06 but it's DRAFT so not found
        assert prior is None

    def test_prior_period_must_be_approved(self, repo):
        r = repo.create_statement(_make_fs(period="2026-06"))
        fs_id = r.get_data().id
        repo.update_statement_status(fs_id, FSStatus.IN_REVIEW, "u")
        repo.update_statement_status(fs_id, FSStatus.REVIEWED, "u")
        repo.update_statement_status(fs_id, FSStatus.APPROVED, "u")
        r = repo.create_statement(_make_fs(period="2026-12"))
        fs_id_2 = r.get_data().id
        repo.update_statement_status(fs_id_2, FSStatus.IN_REVIEW, "u")
        repo.update_statement_status(fs_id_2, FSStatus.REVIEWED, "u")
        repo.update_statement_status(fs_id_2, FSStatus.APPROVED, "u")
        prior = repo.get_prior_period_fs(
            "2026-12", FinancialStatementType.BALANCE_SHEET_GC, 1)
        # 2026-06 is approved, so found
        assert prior is not None
        assert prior.period == "2026-06"


class TestConsolidation:
    def test_consolidated_fs(self, repo):
        fs = FinancialStatement(
            period="2026-12", is_consolidated=True,
            statement_type=FinancialStatementType.BALANCE_SHEET_GC,
        )
        r = repo.create_statement(fs)
        assert r.is_success()
        assert r.get_data().is_consolidated

    def test_create_consolidation_group(self, repo):
        g = FSConsolidationGroup(name="Tap doan", parent_entity_id=1)
        r = repo.create_consolidation_group(g)
        assert r.is_success()
        assert r.get_data().id is not None

    def test_get_consolidation_group(self, repo):
        g = FSConsolidationGroup(name="Tap doan", parent_entity_id=1)
        r = repo.create_consolidation_group(g)
        fetched = repo.get_consolidation_group(r.get_data().id)
        assert fetched is not None
        assert fetched.name == "Tap doan"

    def test_get_consolidation_group_not_found(self, repo):
        assert repo.get_consolidation_group(9999) is None


class TestLineItems:
    def test_update_line_items(self, repo):
        r = repo.create_statement(_make_fs())
        fs_id = r.get_data().id
        lines = [
            FSLineItem(ma_so="110", ten_chi_tieu="Tiền", so_thu_tu=1,
                       current_year=Decimal("50000000")),
        ]
        r2 = repo.update_line_items(fs_id, lines)
        assert r2.is_success()
        fs = repo.get_statement(fs_id)
        assert len(fs.lines) == 1
        assert fs.lines[0].current_year == Decimal("50000000.00")

    def test_update_line_items_not_found(self, repo):
        r = repo.update_line_items(9999, [])
        assert not r.is_success()


class TestB03Generation:
    def test_create_b03_direct(self, repo):
        fs = FinancialStatement(
            period="2026-12", cash_flow_method=FSCashFlowMethod.DIRECT,
            statement_type=FinancialStatementType.CASH_FLOW_GC,
        )
        r = repo.create_statement(fs)
        assert r.is_success()
        assert r.get_data().cash_flow_method == FSCashFlowMethod.DIRECT

    def test_create_b03_indirect(self, repo):
        fs = FinancialStatement(
            period="2026-12", cash_flow_method=FSCashFlowMethod.INDIRECT,
            statement_type=FinancialStatementType.CASH_FLOW_GC,
        )
        r = repo.create_statement(fs)
        assert r.is_success()
        assert r.get_data().cash_flow_method == FSCashFlowMethod.INDIRECT
