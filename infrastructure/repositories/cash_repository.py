from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_

from domain import (
    CashReceipt, CashPayment, BankAccount, BankTransaction, BankStatement,
    ReconciliationDiscrepancy, BankReconciliation, PettyCashFund,
    PettyCashTransaction, CashTransfer, ChequeBook, Cheque,
    DailyCashCount, Advance, CashForecast, CashForecastLine,
    CashReceiptType, CashPaymentType, CashVoucherStatus, BankAccountStatus,
    BankSubAccountType, ChequeStatus, CashTransferStatus, PettyCashFundStatus,
    ReconciliationDiscrepancyType,
    Result, ValidationError, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.models.cash_models import (
    CashReceiptModel, CashPaymentModel, BankAccountModel,
    BankStatementModel, BankTransactionModel, BankReconciliationModel,
    ReconciliationDiscrepancyModel, PettyCashFundModel, PettyCashTransactionModel,
    CashTransferModel, ChequeBookModel, ChequeModel,
    DailyCashCountModel, AdvanceModel,
    CashVoucherStatusDB, BankAccountStatusDB, ChequeStatusDB,
    CashTransferStatusDB, PettyCashFundStatusDB,
)
from infrastructure.models.gl_models import JournalEntryModel, JournalLineModel
from infrastructure.models.coa_models import COAModel


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class CashRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Cash Receipts ──────────────────────────────────────────────────

    def _receipt_to_domain(self, m: CashReceiptModel) -> CashReceipt:
        r = CashReceipt(
            receipt_number=m.receipt_number,
            receipt_date=m.receipt_date,
            receipt_type=CashReceiptType(m.receipt_type),
            payer_name=m.payer_name,
            amount=m.amount,
            amount_in_words=m.amount_in_words,
            currency=m.currency,
            fx_rate=m.fx_rate,
            account_code=m.account_code,
            counter_account=m.counter_account,
            reference_number=m.reference_number,
            description=m.description,
            status=CashVoucherStatus(m.status.value),
            created_by=m.created_by,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        r.id = m.id
        return r

    def _receipt_to_model(self, d: CashReceipt) -> CashReceiptModel:
        return CashReceiptModel(
            receipt_number=d.receipt_number,
            receipt_date=d.receipt_date,
            receipt_type=d.receipt_type.value,
            payer_name=d.payer_name,
            amount=d.amount,
            amount_in_words=d.amount_in_words,
            currency=d.currency,
            fx_rate=d.fx_rate,
            account_code=d.account_code,
            counter_account=d.counter_account,
            reference_number=d.reference_number,
            description=d.description,
            status=CashVoucherStatusDB(d.status.value) if isinstance(d.status, CashVoucherStatus) else CashVoucherStatusDB(d.status),
            created_by=d.created_by,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
        )

    def create_receipt(self, receipt: CashReceipt) -> Result:
        model = self._receipt_to_model(receipt)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._receipt_to_domain(model))

    def get_receipt(self, receipt_id: int) -> Optional[CashReceipt]:
        m = self.session.get(CashReceiptModel, receipt_id)
        return self._receipt_to_domain(m) if m else None

    def get_receipt_by_number(self, number: str) -> Optional[CashReceipt]:
        m = self.session.execute(
            select(CashReceiptModel).where(CashReceiptModel.receipt_number == number)
        ).scalar_one_or_none()
        return self._receipt_to_domain(m) if m else None

    def list_receipts(self, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[CashReceipt]:
        stmt = select(CashReceiptModel).order_by(CashReceiptModel.created_at.desc())
        if status:
            stmt = stmt.where(CashReceiptModel.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return [self._receipt_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def update_receipt_status(self, receipt_id: int, status: CashVoucherStatus, approved_by: Optional[str] = None) -> Result:
        m = self.session.get(CashReceiptModel, receipt_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        m.status = CashVoucherStatusDB(status.value) if isinstance(status, CashVoucherStatus) else CashVoucherStatusDB(status)
        if approved_by:
            m.approved_by = approved_by
            m.approved_at = datetime.now(timezone.utc)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._receipt_to_domain(m))

    # ── Cash Payments ──────────────────────────────────────────────────

    def _payment_to_domain(self, m: CashPaymentModel) -> CashPayment:
        p = CashPayment(
            payment_number=m.payment_number,
            payment_date=m.payment_date,
            payment_type=CashPaymentType(m.payment_type),
            receiver_name=m.receiver_name,
            amount=m.amount,
            amount_in_words=m.amount_in_words,
            currency=m.currency,
            fx_rate=m.fx_rate,
            account_code=m.account_code,
            counter_account=m.counter_account,
            reference_number=m.reference_number,
            supporting_doc_ref=m.supporting_doc_ref,
            description=m.description,
            status=CashVoucherStatus(m.status.value),
            created_by=m.created_by,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        p.id = m.id
        return p

    def _payment_to_model(self, d: CashPayment) -> CashPaymentModel:
        return CashPaymentModel(
            payment_number=d.payment_number,
            payment_date=d.payment_date,
            payment_type=d.payment_type.value,
            receiver_name=d.receiver_name,
            amount=d.amount,
            amount_in_words=d.amount_in_words,
            currency=d.currency,
            fx_rate=d.fx_rate,
            account_code=d.account_code,
            counter_account=d.counter_account,
            reference_number=d.reference_number,
            supporting_doc_ref=d.supporting_doc_ref,
            description=d.description,
            status=CashVoucherStatusDB(d.status.value) if isinstance(d.status, CashVoucherStatus) else CashVoucherStatusDB(d.status),
            created_by=d.created_by,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
        )

    def create_payment(self, payment: CashPayment) -> Result:
        model = self._payment_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._payment_to_domain(model))

    def get_payment(self, payment_id: int) -> Optional[CashPayment]:
        m = self.session.get(CashPaymentModel, payment_id)
        return self._payment_to_domain(m) if m else None

    def get_payment_by_number(self, number: str) -> Optional[CashPayment]:
        m = self.session.execute(
            select(CashPaymentModel).where(CashPaymentModel.payment_number == number)
        ).scalar_one_or_none()
        return self._payment_to_domain(m) if m else None

    def list_payments(self, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[CashPayment]:
        stmt = select(CashPaymentModel).order_by(CashPaymentModel.created_at.desc())
        if status:
            stmt = stmt.where(CashPaymentModel.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return [self._payment_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def update_payment_status(self, payment_id: int, status: CashVoucherStatus, approved_by: Optional[str] = None) -> Result:
        m = self.session.get(CashPaymentModel, payment_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.PAYMENT_NOT_FOUND, payment_id=payment_id))
        m.status = CashVoucherStatusDB(status.value) if isinstance(status, CashVoucherStatus) else CashVoucherStatusDB(status)
        if approved_by:
            m.approved_by = approved_by
            m.approved_at = datetime.now(timezone.utc)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._payment_to_domain(m))

    # ── Bank Accounts ──────────────────────────────────────────────────

    def _ba_to_domain(self, m: BankAccountModel) -> BankAccount:
        ba = BankAccount(
            bank_name=m.bank_name,
            branch=m.branch,
            account_number=m.account_number,
            account_holder=m.account_holder,
            currency=m.currency,
            coa_code=m.coa_code,
            sub_account_type=BankSubAccountType(m.sub_account_type) if m.sub_account_type else None,
            swift_code=m.swift_code,
            iban=m.iban,
            opening_balance=m.opening_balance,
            status=BankAccountStatus(m.status.value) if isinstance(m.status, BankAccountStatusDB) else BankAccountStatus(m.status),
            signatories=m.signatories or [],
            authorization_limit=m.authorization_limit,
            last_reconciled_period=m.last_reconciled_period,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        ba.id = m.id
        return ba

    def _ba_to_model(self, d: BankAccount) -> BankAccountModel:
        return BankAccountModel(
            bank_name=d.bank_name,
            branch=d.branch,
            account_number=d.account_number,
            account_holder=d.account_holder,
            currency=d.currency,
            coa_code=d.coa_code,
            sub_account_type=d.sub_account_type.value if d.sub_account_type else None,
            swift_code=d.swift_code,
            iban=d.iban,
            opening_balance=d.opening_balance,
            status=BankAccountStatusDB(d.status.value) if isinstance(d.status, BankAccountStatus) else BankAccountStatusDB(d.status),
            signatories=d.signatories,
            authorization_limit=d.authorization_limit,
            last_reconciled_period=d.last_reconciled_period,
        )

    def create_bank_account(self, ba: BankAccount) -> Result:
        model = self._ba_to_model(ba)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ba_to_domain(model))

    def get_bank_account(self, ba_id: int) -> Optional[BankAccount]:
        m = self.session.get(BankAccountModel, ba_id)
        return self._ba_to_domain(m) if m else None

    def list_bank_accounts(self, status: Optional[str] = None) -> List[BankAccount]:
        stmt = select(BankAccountModel).order_by(BankAccountModel.bank_name)
        if status:
            stmt = stmt.where(BankAccountModel.status == status)
        return [self._ba_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def update_bank_account_last_reconciled_period(self, ba_id: int, period: str) -> Result:
        m = self.session.get(BankAccountModel, ba_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.BANK_ACCOUNT_NOT_FOUND, ba_id=ba_id))
        m.last_reconciled_period = period
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._ba_to_domain(m))

    # ── Bank Statements / Transactions ─────────────────────────────────

    def _stmt_to_domain(self, m: BankStatementModel) -> BankStatement:
        s = BankStatement(
            bank_account_id=m.bank_account_id,
            statement_date=m.statement_date,
            opening_balance=m.opening_balance,
            closing_balance=m.closing_balance,
            imported_at=m.imported_at,
            source=m.source,
            transactions=[self._tx_to_domain(t) for t in m.transactions],
        )
        s.id = m.id
        return s

    def _tx_to_domain(self, m: BankTransactionModel) -> BankTransaction:
        return BankTransaction(
            bank_account_id=m.bank_account_id,
            transaction_date=m.transaction_date,
            value_date=m.value_date,
            amount=m.amount,
            is_debit=m.is_debit,
            reference=m.reference,
            description=m.description,
            matched_entry_id=m.matched_entry_id,
            statement_id=m.statement_id,
        )

    def create_statement(self, stmt: BankStatement) -> Result:
        model = BankStatementModel(
            bank_account_id=stmt.bank_account_id,
            statement_date=stmt.statement_date,
            opening_balance=stmt.opening_balance,
            closing_balance=stmt.closing_balance,
            source=stmt.source,
        )
        self.session.add(model)
        self.session.flush()
        for tx in stmt.transactions:
            tx_model = BankTransactionModel(
                bank_account_id=tx.bank_account_id,
                statement_id=model.id,
                transaction_date=tx.transaction_date,
                value_date=tx.value_date,
                amount=tx.amount,
                is_debit=tx.is_debit,
                reference=tx.reference,
                description=tx.description,
                matched_entry_id=tx.matched_entry_id,
            )
            self.session.add(tx_model)
        self.session.flush()
        return Result.success(self._stmt_to_domain(model))

    def get_statement(self, stmt_id: int) -> Optional[BankStatement]:
        m = self.session.get(BankStatementModel, stmt_id)
        return self._stmt_to_domain(m) if m else None

    def list_statements(self, bank_account_id: Optional[int] = None) -> List[BankStatement]:
        stmt = select(BankStatementModel).order_by(BankStatementModel.statement_date.desc())
        if bank_account_id:
            stmt = stmt.where(BankStatementModel.bank_account_id == bank_account_id)
        return [self._stmt_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Bank Reconciliations ───────────────────────────────────────────

    def _disc_to_domain(self, m: ReconciliationDiscrepancyModel) -> ReconciliationDiscrepancy:
        return ReconciliationDiscrepancy(
            id=m.id,
            reconciliation_id=m.reconciliation_id,
            discrepancy_type=ReconciliationDiscrepancyType(m.discrepancy_type),
            amount=m.amount,
            entry_side=m.entry_side,
            reference=m.reference,
            description=m.description,
            status=m.status,
            resolution_entry_id=m.resolution_entry_id,
        )

    def _recon_to_domain(self, m: BankReconciliationModel) -> BankReconciliation:
        r = BankReconciliation(
            bank_account_id=m.bank_account_id,
            period=m.period,
            book_balance=m.book_balance,
            bank_balance=m.bank_balance,
            deposits_in_transit=m.deposits_in_transit,
            outstanding_checks=m.outstanding_checks,
            unrecorded_credits=m.unrecorded_credits,
            unrecorded_debits=m.unrecorded_debits,
            adjusted_book_balance=m.adjusted_book_balance,
            adjusted_bank_balance=m.adjusted_bank_balance,
            is_balanced=m.is_balanced,
            reconciled_at=m.reconciled_at,
            reconciled_by=m.reconciled_by,
            discrepancies=[self._disc_to_domain(d) for d in m.discrepancies],
        )
        r.id = m.id
        return r

    def create_reconciliation(self, recon: BankReconciliation) -> Result:
        model = BankReconciliationModel(
            bank_account_id=recon.bank_account_id,
            period=recon.period,
            book_balance=recon.book_balance,
            bank_balance=recon.bank_balance,
            deposits_in_transit=recon.deposits_in_transit,
            outstanding_checks=recon.outstanding_checks,
            unrecorded_credits=recon.unrecorded_credits,
            unrecorded_debits=recon.unrecorded_debits,
            adjusted_book_balance=recon.adjusted_book_balance,
            adjusted_bank_balance=recon.adjusted_bank_balance,
            is_balanced=recon.is_balanced,
            reconciled_at=recon.reconciled_at,
            reconciled_by=recon.reconciled_by,
        )
        self.session.add(model)
        self.session.flush()
        for d in recon.discrepancies:
            disc_model = ReconciliationDiscrepancyModel(
                reconciliation_id=model.id,
                discrepancy_type=d.discrepancy_type.value,
                amount=d.amount,
                entry_side=d.entry_side,
                reference=d.reference,
                description=d.description,
                status=d.status,
                resolution_entry_id=d.resolution_entry_id,
            )
            self.session.add(disc_model)
        self.session.flush()
        return Result.success(self._recon_to_domain(model))

    def get_reconciliation(self, recon_id: int) -> Optional[BankReconciliation]:
        m = self.session.get(BankReconciliationModel, recon_id)
        return self._recon_to_domain(m) if m else None

    def list_reconciliations(self, bank_account_id: Optional[int] = None) -> List[BankReconciliation]:
        stmt = select(BankReconciliationModel).order_by(BankReconciliationModel.period.desc())
        if bank_account_id:
            stmt = stmt.where(BankReconciliationModel.bank_account_id == bank_account_id)
        return [self._recon_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Petty Cash ─────────────────────────────────────────────────────

    def _pc_to_domain(self, m: PettyCashFundModel) -> PettyCashFund:
        p = PettyCashFund(
            fund_code=m.fund_code,
            custodian=m.custodian,
            limit_amount=m.limit_amount,
            current_balance=m.current_balance,
            currency=m.currency,
            established_date=m.established_date,
            status=PettyCashFundStatus(m.status.value) if isinstance(m.status, PettyCashFundStatusDB) else PettyCashFundStatus(m.status),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        p.id = m.id
        return p

    def _pc_to_model(self, d: PettyCashFund) -> PettyCashFundModel:
        return PettyCashFundModel(
            fund_code=d.fund_code,
            custodian=d.custodian,
            limit_amount=d.limit_amount,
            current_balance=d.current_balance,
            currency=d.currency,
            established_date=d.established_date,
            status=PettyCashFundStatusDB(d.status.value) if isinstance(d.status, PettyCashFundStatus) else PettyCashFundStatusDB(d.status),
        )

    def create_petty_cash_fund(self, fund: PettyCashFund) -> Result:
        model = self._pc_to_model(fund)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._pc_to_domain(model))

    def get_petty_cash_fund(self, fund_id: int) -> Optional[PettyCashFund]:
        m = self.session.get(PettyCashFundModel, fund_id)
        return self._pc_to_domain(m) if m else None

    def list_petty_cash_funds(self) -> List[PettyCashFund]:
        stmt = select(PettyCashFundModel).order_by(PettyCashFundModel.fund_code)
        return [self._pc_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def update_petty_cash_balance(self, fund_id: int, new_balance: Decimal) -> Result:
        m = self.session.get(PettyCashFundModel, fund_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.PETTY_CASH_FUND_NOT_FOUND, fund_id=fund_id))
        m.current_balance = _vnd(new_balance)
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._pc_to_domain(m))

    # ── Cash Transfers ─────────────────────────────────────────────────

    def _ct_to_domain(self, m: CashTransferModel) -> CashTransfer:
        c = CashTransfer(
            source_account=m.source_account,
            destination_account=m.destination_account,
            amount=m.amount,
            transfer_date=m.transfer_date,
            fx_rate=m.fx_rate,
            reference=m.reference,
            status=CashTransferStatus(m.status.value),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        c.id = m.id
        return c

    def create_transfer(self, transfer: CashTransfer) -> Result:
        model = CashTransferModel(
            source_account=transfer.source_account,
            destination_account=transfer.destination_account,
            amount=transfer.amount,
            transfer_date=transfer.transfer_date,
            fx_rate=transfer.fx_rate,
            reference=transfer.reference,
            status=CashTransferStatusDB(transfer.status.value) if isinstance(transfer.status, CashTransferStatus) else CashTransferStatusDB(transfer.status),
            created_by=transfer.created_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ct_to_domain(model))

    def get_transfer(self, transfer_id: int) -> Optional[CashTransfer]:
        m = self.session.get(CashTransferModel, transfer_id)
        return self._ct_to_domain(m) if m else None

    def list_transfers(self, limit: int = 100) -> List[CashTransfer]:
        stmt = select(CashTransferModel).order_by(CashTransferModel.transfer_date.desc()).limit(limit)
        return [self._ct_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Cheques ────────────────────────────────────────────────────────

    def _cheque_to_domain(self, m: ChequeModel) -> Cheque:
        c = Cheque(
            cheque_number=m.cheque_number,
            cheque_book_id=m.cheque_book_id,
            payee=m.payee,
            amount=m.amount,
            issue_date=m.issue_date,
            status=ChequeStatus(m.status.value),
            bank_account_id=m.bank_account_id,
            cleared_date=m.cleared_date,
            cancelled_reason=m.cancelled_reason,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        c.id = m.id
        return c

    def create_cheque(self, cheque: Cheque) -> Result:
        model = ChequeModel(
            cheque_number=cheque.cheque_number,
            cheque_book_id=cheque.cheque_book_id,
            payee=cheque.payee,
            amount=cheque.amount,
            issue_date=cheque.issue_date,
            status=ChequeStatusDB(cheque.status.value) if isinstance(cheque.status, ChequeStatus) else ChequeStatusDB(cheque.status),
            bank_account_id=cheque.bank_account_id,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._cheque_to_domain(model))

    def get_cheque(self, cheque_id: int) -> Optional[Cheque]:
        m = self.session.get(ChequeModel, cheque_id)
        return self._cheque_to_domain(m) if m else None

    def list_cheques(self) -> List[Cheque]:
        q = select(ChequeModel).order_by(ChequeModel.issue_date.desc())
        return [self._cheque_to_domain(m) for m in self.session.execute(q).scalars().all()]

    def update_cheque_status(
        self,
        cheque_id: int,
        status: ChequeStatus,
        cleared_date: Optional[date] = None,
        payee: Optional[str] = None,
        amount: Optional[Decimal] = None,
        bank_account_id: Optional[int] = None,
        cancel_reason: Optional[str] = None,
    ) -> Result:
        m = self.session.get(ChequeModel, cheque_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        m.status = ChequeStatusDB(status.value) if isinstance(status, ChequeStatus) else ChequeStatusDB(status)
        if cleared_date:
            m.cleared_date = cleared_date
        if payee is not None:
            m.payee = payee
        if amount is not None:
            m.amount = _vnd(amount)
        if bank_account_id is not None:
            m.bank_account_id = bank_account_id
        if cancel_reason is not None:
            m.cancelled_reason = cancel_reason
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._cheque_to_domain(m))

    # ── Daily Cash Counts ──────────────────────────────────────────────

    def _dcc_to_domain(self, m: DailyCashCountModel) -> DailyCashCount:
        d = DailyCashCount(
            count_date=m.count_date,
            account_code=m.account_code,
            expected_balance=m.expected_balance,
            actual_balance=m.actual_balance,
            difference=m.difference,
            denomination_breakdown=m.denomination_breakdown or {},
            notes=m.notes,
            counted_by=m.counted_by,
            witnessed_by=m.witnessed_by,
            created_at=m.created_at,
        )
        d.id = m.id
        return d

    def create_daily_cash_count(self, count: DailyCashCount) -> Result:
        model = DailyCashCountModel(
            count_date=count.count_date,
            account_code=count.account_code,
            expected_balance=count.expected_balance,
            actual_balance=count.actual_balance,
            difference=count.difference,
            denomination_breakdown=count.denomination_breakdown,
            notes=count.notes,
            counted_by=count.counted_by,
            witnessed_by=count.witnessed_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._dcc_to_domain(model))

    def list_daily_cash_counts(self, account_code: Optional[str] = None, limit: int = 100) -> List[DailyCashCount]:
        stmt = select(DailyCashCountModel).order_by(DailyCashCountModel.count_date.desc()).limit(limit)
        if account_code:
            stmt = stmt.where(DailyCashCountModel.account_code == account_code)
        return [self._dcc_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    # ── Advances (TK 141) ──────────────────────────────────────────────

    def _adv_to_domain(self, m: AdvanceModel) -> Advance:
        a = Advance(
            employee_name=m.employee_name,
            employee_id=m.employee_id,
            amount=m.amount,
            advance_date=m.advance_date,
            purpose=m.purpose,
            settlement_deadline=m.settlement_deadline,
            settlement_amount=m.settlement_amount,
            remaining_balance=m.remaining_balance,
            status=m.status,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        a.id = m.id
        return a

    def create_advance(self, advance: Advance) -> Result:
        model = AdvanceModel(
            employee_name=advance.employee_name,
            employee_id=advance.employee_id,
            amount=advance.amount,
            advance_date=advance.advance_date,
            purpose=advance.purpose,
            settlement_deadline=advance.settlement_deadline,
            settlement_amount=advance.settlement_amount,
            remaining_balance=advance.remaining_balance,
            status=advance.status,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._adv_to_domain(model))

    def get_advance(self, advance_id: int) -> Optional[Advance]:
        m = self.session.get(AdvanceModel, advance_id)
        return self._adv_to_domain(m) if m else None

    def list_advances(self, employee_id: Optional[str] = None, status: Optional[str] = None) -> List[Advance]:
        stmt = select(AdvanceModel).order_by(AdvanceModel.advance_date.desc())
        if employee_id:
            stmt = stmt.where(AdvanceModel.employee_id == employee_id)
        if status:
            stmt = stmt.where(AdvanceModel.status == status)
        return [self._adv_to_domain(m) for m in self.session.execute(stmt).scalars().all()]

    def update_advance_settlement(self, advance_id: int, settlement_amount: Decimal) -> Result:
        m = self.session.get(AdvanceModel, advance_id)
        if not m:
            return Result.failure(AccountError(ErrorCodes.ADVANCE_NOT_FOUND, advance_id=advance_id))
        m.settlement_amount += _vnd(settlement_amount)
        m.remaining_balance = m.amount - m.settlement_amount
        if m.remaining_balance <= Decimal("0.001"):
            m.status = "settled"
        m.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._adv_to_domain(m))

    # ── Cash Balance ──────────────────────────────────────────────────

    def calculate_bank_balance(self, ba_id: int, as_of: Optional[date] = None) -> Decimal:
        ba = self.get_bank_account(ba_id)
        if not ba:
            return Decimal("0")
        coa = ba.coa_code
        balance = ba.opening_balance

        receipts = self.session.execute(
            select(func.coalesce(func.sum(CashReceiptModel.amount), 0)).where(
                CashReceiptModel.account_code == coa,
                CashReceiptModel.status.in_([CashVoucherStatusDB.DRAFT, CashVoucherStatusDB.APPROVED, CashVoucherStatusDB.PAID]),
            )
        ).scalar() or Decimal("0")

        payments = self.session.execute(
            select(func.coalesce(func.sum(CashPaymentModel.amount), 0)).where(
                CashPaymentModel.account_code == coa,
                CashPaymentModel.status.in_([CashVoucherStatusDB.DRAFT, CashVoucherStatusDB.APPROVED, CashVoucherStatusDB.PAID]),
            )
        ).scalar() or Decimal("0")

        transfers_in = self.session.execute(
            select(func.coalesce(func.sum(CashTransferModel.amount), 0)).where(
                CashTransferModel.destination_account == coa,
                CashTransferModel.status.in_([CashTransferStatusDB.COMPLETED]),
            )
        ).scalar() or Decimal("0")

        transfers_out = self.session.execute(
            select(func.coalesce(func.sum(CashTransferModel.amount), 0)).where(
                CashTransferModel.source_account == coa,
                CashTransferModel.status.in_([CashTransferStatusDB.COMPLETED, CashTransferStatusDB.PENDING]),
            )
        ).scalar() or Decimal("0")

        return _vnd(balance + receipts + transfers_in - payments - transfers_out)

    def get_cash_balance(self, account_code: str) -> Decimal:
        receipts_total = self.session.execute(
            select(func.coalesce(func.sum(CashReceiptModel.amount), 0)).where(
                CashReceiptModel.account_code == account_code,
                CashReceiptModel.status.in_([CashVoucherStatusDB.DRAFT, CashVoucherStatusDB.APPROVED, CashVoucherStatusDB.PAID]),
            )
        ).scalar() or Decimal("0")

        payments_total = self.session.execute(
            select(func.coalesce(func.sum(CashPaymentModel.amount), 0)).where(
                CashPaymentModel.account_code == account_code,
                CashPaymentModel.status.in_([CashVoucherStatusDB.DRAFT, CashVoucherStatusDB.APPROVED, CashVoucherStatusDB.PAID]),
            )
        ).scalar() or Decimal("0")

        transfers_in = self.session.execute(
            select(func.coalesce(func.sum(CashTransferModel.amount), 0)).where(
                CashTransferModel.destination_account == account_code,
                CashTransferModel.status.in_([CashTransferStatusDB.COMPLETED]),
            )
        ).scalar() or Decimal("0")

        transfers_out = self.session.execute(
            select(func.coalesce(func.sum(CashTransferModel.amount), 0)).where(
                CashTransferModel.source_account == account_code,
                CashTransferModel.status.in_([CashTransferStatusDB.COMPLETED, CashTransferStatusDB.PENDING]),
            )
        ).scalar() or Decimal("0")

        return _vnd(receipts_total + transfers_in - payments_total - transfers_out)

    # ── Cash Book Report ──────────────────────────────────────────────

    def get_cash_book_entries(
        self,
        account_code: str,
        from_date: date,
        to_date: date,
    ) -> List[Dict[str, Any]]:
        receipts = self.session.execute(
            select(CashReceiptModel).where(
                CashReceiptModel.account_code == account_code,
                CashReceiptModel.receipt_date.between(from_date, to_date),
            ).order_by(CashReceiptModel.receipt_date, CashReceiptModel.id)
        ).scalars().all()

        payments = self.session.execute(
            select(CashPaymentModel).where(
                CashPaymentModel.account_code == account_code,
                CashPaymentModel.payment_date.between(from_date, to_date),
            ).order_by(CashPaymentModel.payment_date, CashPaymentModel.id)
        ).scalars().all()

        entries = []
        for r in receipts:
            entries.append({
                "type": "receipt",
                "date": r.receipt_date,
                "number": r.receipt_number,
                "voucher_type": "PT",
                "counter_party": r.payer_name,
                "description": r.description,
                "debit": r.amount,
                "credit": Decimal("0"),
                "account_code": r.account_code,
                "counter_account": r.counter_account,
                "status": r.status.value,
                "sort_key": (r.receipt_date.isoformat(), 0, r.id),
            })
        for p in payments:
            entries.append({
                "type": "payment",
                "date": p.payment_date,
                "number": p.payment_number,
                "voucher_type": "PC",
                "counter_party": p.receiver_name,
                "description": p.description,
                "debit": Decimal("0"),
                "credit": p.amount,
                "account_code": p.account_code,
                "counter_account": p.counter_account,
                "status": p.status.value,
                "sort_key": (p.payment_date.isoformat(), 1, p.id),
            })

        entries.sort(key=lambda e: e["sort_key"])
        return entries

    # ── GL entries for cash/bank matching ────────────────────────────

    def get_gl_entries_for_bank(
        self,
        coa_code: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        bank_account_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        stmt = select(
            JournalEntryModel.id,
            JournalEntryModel.journal_number,
            JournalEntryModel.transaction_date,
            JournalEntryModel.description,
            JournalLineModel.debit,
            JournalLineModel.credit,
            JournalLineModel.account_id,
        ).join(
            JournalLineModel, JournalEntryModel.id == JournalLineModel.journal_entry_id
        ).where(JournalEntryModel.is_posted == True)

        if coa_code:
            stmt = stmt.where(JournalLineModel.account_id == coa_code)
        if from_date:
            stmt = stmt.where(JournalEntryModel.transaction_date >= from_date)
        if to_date:
            stmt = stmt.where(JournalEntryModel.transaction_date <= to_date)

        results = self.session.execute(stmt).all()
        entries = []
        for row in results:
            debit = Decimal(str(row.debit or 0))
            credit = Decimal(str(row.credit or 0))
            amount = debit if debit > 0 else credit
            entries.append({
                "journal_id": row.id,
                "journal_number": row.journal_number,
                "date": row.transaction_date,
                "description": row.description,
                "amount": amount,
                "is_debit": debit > 0,
                "account": row.account_id,
                "reference": row.journal_number,
                "matched": False,
            })
        return entries
