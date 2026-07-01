from decimal import Decimal
from datetime import date, datetime, timezone
import pytest

from domain.fs import (
    FinancialStatementType, FSStatus, FSCashFlowMethod,
    FSLineItem, FinancialStatement, FSAccountMapping,
    FSConsolidationGroup, FSConsolidationMember,
)
from domain.common import ValidationError
from domain import JournalEntry, JournalLine
from infrastructure.repositories.fs_repository import FSRepository
from infrastructure.repositories.gl_repository import GLRepository
from infrastructure.models.coa_models import Base, COAModel, AccountingRegime, AccountStatus
from infrastructure.models.gl_models import AccountingPeriodModel, PeriodType
from use_cases.fs import FSUseCases

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


# ── End-to-end B01-DN test with real GL journal entries ──────────────


def _seed_b01_accounts(sess):
    accounts = [
        COAModel(code="1111", name="Tiền mặt", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=2, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="1121", name="Tiền gửi ngân hàng", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=2, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="131", name="Phải thu khách hàng", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="152", name="Nguyên vật liệu", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="331", name="Phải trả người bán", account_type="liability",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="341", name="Vay dài hạn", account_type="liability",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="4111", name="Vốn đầu tư của chủ sở hữu", account_type="equity",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=2, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="421", name="Lợi nhuận chưa phân phối", account_type="equity",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=2, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
    ]
    for acc in accounts:
        sess.add(acc)
    sess.flush()


@pytest.fixture(scope="function")
def b01_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    _seed_b01_accounts(sess)
    sess.commit()
    yield sess
    sess.close()


class TestB01DNE2E:
    """End-to-end B01-DN generation with real GL journal entries."""

    def _post_entry(self, sess, journal_number: str, lines_data: list,
                     period: str = "2026-12") -> int:
        repo = GLRepository(sess)
        entry = JournalEntry(
            journal_number=journal_number,
            transaction_date=date(2026, 12, 31),
            description=f"Entry {journal_number}",
            period=period,
            lines=[
                JournalLine(
                    journal_entry_id=0,
                    account_id=ld["account_id"],
                    debit=Decimal(str(ld["debit"])),
                    credit=Decimal(str(ld["credit"])),
                    period=period,
                )
                for ld in lines_data
            ],
        )
        r = repo.create_entry(entry)
        assert r.is_success(), f"create_entry failed: {r.error}"
        entry_id = r.get_data().id
        pr = repo.post_entry(entry_id)
        assert pr.is_success(), f"post_entry failed: {pr.error}"
        return entry_id

    def test_generate_b01dn_with_gl_entries(self, b01_session):
        sess = b01_session

        # Create accounting period
        ap = AccountingPeriodModel(
            period="2026-12", type=PeriodType.YEARLY,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            is_closed=False, is_current=True,
        )
        sess.add(ap)
        sess.commit()

        # Post journal entries (each entry balances individually)
        # Entry 1: Owner capital contribution
        self._post_entry(sess, "JV000101", [
            {"account_id": "1111", "debit": "800000000", "credit": "0"},
            {"account_id": "4111", "debit": "0", "credit": "800000000"},
        ])

        # Entry 2: Long-term bank loan
        self._post_entry(sess, "JV000102", [
            {"account_id": "1121", "debit": "500000000", "credit": "0"},
            {"account_id": "341", "debit": "0", "credit": "500000000"},
        ])

        # Entry 3: Inventory purchase on credit
        self._post_entry(sess, "JV000103", [
            {"account_id": "152", "debit": "300000000", "credit": "0"},
            {"account_id": "331", "debit": "0", "credit": "300000000"},
        ])

        # Entry 4: Sales on credit
        self._post_entry(sess, "JV000104", [
            {"account_id": "131", "debit": "200000000", "credit": "0"},
            {"account_id": "5111", "debit": "0", "credit": "200000000"},
        ])

        # Entry 5: Close revenue to retained earnings
        self._post_entry(sess, "JV000105", [
            {"account_id": "5111", "debit": "200000000", "credit": "0"},
            {"account_id": "421", "debit": "0", "credit": "200000000"},
        ])

        sess.commit()

        # Generate B01-DN
        uc = FSUseCases(sess)
        result = uc.generate_b01_dn(period="2026-12", entity_id=1, generated_by="test")
        assert result.is_success(), f"B01-DN generation failed: {result.error}"
        fs = result.get_data()
        assert fs is not None
        assert fs.period == "2026-12"
        assert fs.statement_type == FinancialStatementType.BALANCE_SHEET_GC
        assert fs.status == FSStatus.DRAFT
        assert len(fs.lines) == 24  # 24 line items in B01_DN_LINE_ITEMS

        # Build lookup dict
        line_map = {l.ma_so: l for l in fs.lines}

        # ── Verify asset lines ──
        # Line 111 (Tiền): 1111 = 800,000,000
        assert line_map["111"].current_year == Decimal("800000000.00"), \
            f"Line 111 expected 800M got {line_map['111'].current_year}"

        # Line 112 (Tương đương tiền): 1121 = 500,000,000
        assert line_map["112"].current_year == Decimal("500000000.00"), \
            f"Line 112 expected 500M got {line_map['112'].current_year}"

        # Line 110 (Tiền & tương đương): 111 + 112 = 1,300,000,000
        assert line_map["110"].current_year == Decimal("1300000000.00"), \
            f"Line 110 expected 1.3B got {line_map['110'].current_year}"
        assert line_map["110"].is_calculated

        # Line 120 (Đầu tư TC ngắn hạn) = 0
        assert line_map["120"].current_year == Decimal("0.00")

        # Line 130 (Phải thu ngắn hạn): 131 = 200,000,000
        assert line_map["130"].current_year == Decimal("200000000.00"), \
            f"Line 130 expected 200M got {line_map['130'].current_year}"

        # Line 140 (Hàng tồn kho): 152 = 300,000,000
        assert line_map["140"].current_year == Decimal("300000000.00"), \
            f"Line 140 expected 300M got {line_map['140'].current_year}"

        # Line 150 (TSNH khác) = 0
        assert line_map["150"].current_year == Decimal("0.00")

        # Line 100 (TSNH subtotal): 110+120+130+140+150 = 1,300M+0+200M+300M+0 = 1,800M
        assert line_map["100"].current_year == Decimal("1800000000.00"), \
            f"Line 100 expected 1.8B got {line_map['100'].current_year}"
        assert line_map["100"].is_calculated

        # Line 200 (TSDH subtotal) = 0
        assert line_map["200"].current_year == Decimal("0.00")
        assert line_map["200"].is_calculated

        # Line 270 (Tổng TS): 100+200 = 1,800,000,000
        assert line_map["270"].current_year == Decimal("1800000000.00"), \
            f"Line 270 expected 1.8B got {line_map['270'].current_year}"
        assert line_map["270"].is_calculated

        # ── Verify liability lines ──
        # Line 310 (Nợ ngắn hạn): 331 = 300,000,000
        assert line_map["310"].current_year == Decimal("300000000.00"), \
            f"Line 310 expected 300M got {line_map['310'].current_year}"

        # Line 330 (Nợ dài hạn): 341 = 500,000,000
        assert line_map["330"].current_year == Decimal("500000000.00"), \
            f"Line 330 expected 500M got {line_map['330'].current_year}"

        # Line 300 (Nợ phải trả): 310+330 = 300M+500M = 800M
        assert line_map["300"].current_year == Decimal("800000000.00"), \
            f"Line 300 expected 800M got {line_map['300'].current_year}"
        assert line_map["300"].is_calculated

        # ── Verify equity lines ──
        # Line 410 (Vốn góp): 4111 = 800,000,000
        assert line_map["410"].current_year == Decimal("800000000.00"), \
            f"Line 410 expected 800M got {line_map['410'].current_year}"

        # Line 420 (Thặng dư) = 0
        assert line_map["420"].current_year == Decimal("0.00")

        # Line 430 (Lợi nhuận): 421 = 200,000,000
        assert line_map["430"].current_year == Decimal("200000000.00"), \
            f"Line 430 expected 200M got {line_map['430'].current_year}"

        # Line 400 (VCSH): 410+420+430 = 800M+0+200M = 1,000M
        assert line_map["400"].current_year == Decimal("1000000000.00"), \
            f"Line 400 expected 1B got {line_map['400'].current_year}"
        assert line_map["400"].is_calculated

        # Line 440 (Tổng NV): 300+400 = 800M+1,000M = 1,800M
        assert line_map["440"].current_year == Decimal("1800000000.00"), \
            f"Line 440 expected 1.8B got {line_map['440'].current_year}"
        assert line_map["440"].is_calculated

        # ── Balance sheet verification: Total assets = Total sources ──
        assert line_map["270"].current_year == line_map["440"].current_year, \
            f"Balance sheet imbalanced: assets={line_map['270'].current_year} sources={line_map['440'].current_year}"

    def test_generate_b01dn_invalid_period_format(self, b01_session):
        uc = FSUseCases(b01_session)
        result = uc.generate_b01_dn(period="invalid", entity_id=1)
        assert result.is_failure()

    def test_generate_b01dn_wrong_month(self, b01_session):
        uc = FSUseCases(b01_session)
        result = uc.generate_b01_dn(period="2026-13", entity_id=1)
        assert result.is_failure()

    def test_generate_b01dn_period_closed(self, b01_session):
        sess = b01_session
        ap = AccountingPeriodModel(
            period="2026-01", type=PeriodType.MONTHLY,
            start_date=date(2026, 1, 1), end_date=date(2026, 1, 31),
            is_closed=True, is_current=False,
        )
        sess.add(ap)
        sess.commit()
        uc = FSUseCases(sess)
        result = uc.generate_b01_dn(period="2026-01", entity_id=1)
        assert result.is_failure(), "Should reject closed period"
        assert "PERIOD_CLOSED" in str(result.error) or "FS_GEN_PERIOD_CLOSED" in str(result.error)


_B02_ACCOUNTS = [
    "1111", "5111", "632", "641", "642", "635", "515", "711", "811", "821",
]


def _seed_b02_accounts(sess):
    from infrastructure.models.coa_models import COAModel, AccountStatus, AccountingRegime
    accounts = [
        COAModel(code="1111", name="Tiền mặt", account_type="asset",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=2, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="5111", name="Doanh thu bán hàng", account_type="revenue",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=2, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="632", name="Giá vốn hàng bán", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="641", name="Chi phí bán hàng", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="642", name="Chi phí QLDN", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="635", name="Chi phí tài chính", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="515", name="Doanh thu tài chính", account_type="revenue",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="711", name="Thu nhập khác", account_type="revenue",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="credit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="811", name="Chi phí khác", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
        COAModel(code="821", name="Chi phí thuế TNDN", account_type="expense",
                 regime=AccountingRegime.TT133_2016, vas_compliant=True,
                 drcr_direction="debit", level=1, status=AccountStatus.ACTIVE,
                 currency="VND", unit="VND"),
    ]
    for acc in accounts:
        sess.add(acc)
    sess.flush()


@pytest.fixture(scope="function")
def b02_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    _seed_b02_accounts(sess)
    sess.commit()
    yield sess
    sess.close()


class TestB02DNE2E:
    def _post(self, sess, jn, lines, period="2026-11"):
        repo = GLRepository(sess)
        entry = JournalEntry(
            journal_number=jn, transaction_date=date(2026, 11, 30),
            description=f"Entry {jn}", period=period,
            lines=[JournalLine(journal_entry_id=0, account_id=ld["a"],
                               debit=Decimal(str(ld["d"])), credit=Decimal(str(ld["c"])),
                               period=period) for ld in lines],
        )
        r = repo.create_entry(entry)
        eid = r.get_data().id
        repo.post_entry(eid)
        return eid

    def test_generate_b02dn_revenue_and_cogs(self, b02_session):
        sess = b02_session
        ap = AccountingPeriodModel(
            period="2026-11", type=PeriodType.MONTHLY,
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 30),
            is_closed=False, is_current=True,
        )
        sess.add(ap)
        sess.commit()

        self._post(sess, "JV000100", [{"a": "1111", "d": "30000000", "c": "0"},
                                       {"a": "5111", "d": "0", "c": "30000000"}])
        self._post(sess, "JV000101", [{"a": "632", "d": "18000000", "c": "0"},
                                       {"a": "1111", "d": "0", "c": "18000000"}])
        self._post(sess, "JV000102", [{"a": "641", "d": "2000000", "c": "0"},
                                       {"a": "1111", "d": "0", "c": "2000000"}])
        self._post(sess, "JV000103", [{"a": "642", "d": "3000000", "c": "0"},
                                       {"a": "1111", "d": "0", "c": "3000000"}])
        sess.commit()

        uc = FSUseCases(sess)
        result = uc.generate_b02_dn(period="2026-11", entity_id=1, generated_by="test")
        assert result.is_success(), f"B02-DN failed: {result.error}"
        fs = result.get_data()
        lm = {l.ma_so: l for l in fs.lines}

        assert lm["01"].current_year == Decimal("30000000.00")    # Revenue
        assert lm["11"].current_year == Decimal("18000000.00")    # COGS
        assert lm["23"].current_year == Decimal("2000000.00")     # Selling
        assert lm["24"].current_year == Decimal("3000000.00")     # Admin
        assert lm["10"].current_year == Decimal("30000000.00")    # Net revenue = 01-02 = 30M-0
        assert lm["20"].current_year == Decimal("12000000.00")    # Gross profit = 10-11 = 30M-18M
        assert lm["30"].current_year == Decimal("7000000.00")     # Profit from ops = 20+21-22-23-24 = 12M+0-0-2M-3M
        assert lm["50"].current_year == Decimal("7000000.00")     # Profit before tax = 30+40-41
        assert lm["60"].current_year == Decimal("7000000.00")     # Net profit = 50-51-52


class TestB03DNE2E:
    def test_generate_b03dn_indirect(self, b02_session):
        sess = b02_session
        ap = AccountingPeriodModel(
            period="2026-11", type=PeriodType.MONTHLY,
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 30),
            is_closed=False, is_current=True,
        )
        sess.add(ap)
        sess.commit()

        repo = GLRepository(sess)
        r = repo.create_entry(JournalEntry(
            journal_number="JV000200", transaction_date=date(2026, 11, 30),
            description="Sales", period="2026-11",
            lines=[JournalLine(journal_entry_id=0, account_id="1111",
                               debit=Decimal("50000000"), credit=Decimal("0"),
                               period="2026-11"),
                   JournalLine(journal_entry_id=0, account_id="5111",
                               debit=Decimal("0"), credit=Decimal("50000000"),
                               period="2026-11")],
        ))
        repo.post_entry(r.get_data().id)
        sess.commit()

        uc = FSUseCases(sess)
        result = uc.generate_b03_dn(period="2026-11",
                                     method=FSCashFlowMethod.INDIRECT,
                                     entity_id=1, generated_by="test")
        assert result.is_success(), f"B03-DN indirect failed: {result.error}"
        assert result.get_data().cash_flow_method == FSCashFlowMethod.INDIRECT


class TestB09DNE2E:
    def test_generate_b09dn(self, b02_session):
        sess = b02_session
        ap = AccountingPeriodModel(
            period="2026-11", type=PeriodType.MONTHLY,
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 30),
            is_closed=False, is_current=True,
        )
        sess.add(ap)
        sess.commit()

        repo = GLRepository(sess)
        entry = JournalEntry(
            journal_number="JV000300", transaction_date=date(2026, 11, 30),
            description="Sales entry", period="2026-11",
            lines=[JournalLine(journal_entry_id=0, account_id="1111",
                               debit=Decimal("50000000"), credit=Decimal("0"), period="2026-11"),
                   JournalLine(journal_entry_id=0, account_id="5111",
                               debit=Decimal("0"), credit=Decimal("50000000"), period="2026-11")],
        )
        r = repo.create_entry(entry)
        repo.post_entry(r.get_data().id)
        sess.commit()

        uc = FSUseCases(sess)
        result = uc.generate_b09_dn(period="2026-11", entity_id=1, generated_by="test")
        assert result.is_success(), f"B09-DN failed: {result.error}"
        fs = result.get_data()
        assert len(fs.lines) == 16
        lm = {l.ma_so: l for l in fs.lines}
        assert "I" in lm
        assert "V.01" in lm
        assert "VII" in lm


class TestMapping:
    def _seed(self, sess):
        from infrastructure.models.fs_models import FSAccountMappingModel, FSStatementTypeDB
        sess.add(FSAccountMappingModel(fs_ma_so="111", account_code="1111",
                                        weight=1, direction="both",
                                        statement_type=FSStatementTypeDB.B01_DN))
        sess.commit()

    def test_update_mapping_partial(self, b01_session):
        sess = b01_session
        self._seed(sess)
        uc = FSUseCases(sess)
        result = uc.update_mapping(1, weight=Decimal("2.00"))
        assert result.is_success()
        assert result.get_data().weight == Decimal("2.00")

    def test_update_mapping_all_fields(self, b01_session):
        sess = b01_session
        self._seed(sess)
        uc = FSUseCases(sess)
        result = uc.update_mapping(1, fs_ma_so="112", account_code="1121",
                                    weight=Decimal("1.50"), direction="debit")
        assert result.is_success()
        m = result.get_data()
        assert m.fs_ma_so == "112"
        assert m.account_code == "1121"
        assert m.weight == Decimal("1.50")
        assert m.direction == "debit"

    def test_update_mapping_not_found(self, b01_session):
        uc = FSUseCases(b01_session)
        result = uc.update_mapping(999, weight=Decimal("1.00"))
        assert result.is_failure()
        assert "MAPPING_NOT_FOUND" in str(result.error)


class TestExport:
    def _make_fs(self, sess):
        uc = FSUseCases(sess)
        result = uc.generate_b01_dn(period="2026-12", entity_id=1, generated_by="test")
        return result.get_data() if result.is_success() else None

    def test_export_html(self, b01_session):
        sess = b01_session
        ap = AccountingPeriodModel(
            period="2026-12", type=PeriodType.YEARLY,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            is_closed=False, is_current=True,
        )
        sess.add(ap)
        sess.commit()
        fs = self._make_fs(sess)
        if not fs:
            return
        uc = FSUseCases(sess)
        result = uc.export_fs(fs.id, fmt="html")
        assert result.is_success()

    def test_export_xlsx(self, b01_session):
        sess = b01_session
        ap = AccountingPeriodModel(
            period="2026-12", type=PeriodType.YEARLY,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            is_closed=False, is_current=True,
        )
        sess.add(ap)
        sess.commit()
        fs = self._make_fs(sess)
        if not fs:
            return
        uc = FSUseCases(sess)
        result = uc.export_fs(fs.id, fmt="xlsx")
        assert result.is_success()
