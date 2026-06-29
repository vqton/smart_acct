from typing import Optional, List
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from domain import (
    CashReceipt, CashPayment, BankAccount, BankStatement, BankTransaction,
    ReconciliationDiscrepancy, BankReconciliation, PettyCashFund,
    PettyCashTransaction, CashTransfer, ChequeBook, Cheque,
    DailyCashCount, Advance, CashForecast, CashForecastLine,
    CashReceiptType, CashPaymentType, CashVoucherStatus, BankAccountStatus,
    ChequeStatus, CashTransferStatus, PettyCashFundStatus,
    ReconciliationDiscrepancyType,
    Result, ValidationError, AccountError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.cash_repository import CashRepository
from infrastructure.repositories.gl_repository import GLRepository


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class CashUseCases:
    def __init__(self, session: Session):
        self.repo = CashRepository(session)
        self.gl_repo = GLRepository(session)

    # ── Cash Receipts (UC-CASH-01) ────────────────────────────────────

    def create_receipt(
        self,
        receipt_date: date,
        receipt_type: CashReceiptType,
        payer_name: str,
        amount: Decimal,
        amount_in_words: str,
        account_code: str,
        counter_account: str,
        description: str,
        created_by: str,
        currency: str = "VND",
        fx_rate: Optional[Decimal] = None,
        reference_number: Optional[str] = None,
    ) -> Result:
        receipt_number = self._next_receipt_number(receipt_date)
        try:
            receipt = CashReceipt(
                receipt_number=receipt_number,
                receipt_date=receipt_date,
                receipt_type=receipt_type,
                payer_name=payer_name,
                amount=amount,
                amount_in_words=amount_in_words,
                currency=currency,
                fx_rate=fx_rate,
                account_code=account_code,
                counter_account=counter_account,
                reference_number=reference_number,
                description=description,
                status=CashVoucherStatus.DRAFT,
                created_by=created_by,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)

        return self.repo.create_receipt(receipt)

    def get_receipt(self, receipt_id: int) -> Result:
        receipt = self.repo.get_receipt(receipt_id)
        if not receipt:
            return Result.failure(AccountError(ErrorCodes.RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        return Result.success(receipt)

    def list_receipts(self, status: Optional[str] = None) -> List[CashReceipt]:
        return self.repo.list_receipts(status=status)

    def approve_receipt(self, receipt_id: int, approved_by: str) -> Result:
        receipt = self.repo.get_receipt(receipt_id)
        if not receipt:
            return Result.failure(AccountError(ErrorCodes.RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        if receipt.status != CashVoucherStatus.DRAFT:
            return Result.failure(ValidationError(ErrorCodes.ONLY_DRAFT_APPROVED))
        return self.repo.update_receipt_status(receipt_id, CashVoucherStatus.APPROVED, approved_by)

    def cancel_receipt(self, receipt_id: int) -> Result:
        receipt = self.repo.get_receipt(receipt_id)
        if not receipt:
            return Result.failure(AccountError(ErrorCodes.RECEIPT_NOT_FOUND, receipt_id=receipt_id))
        if receipt.status == CashVoucherStatus.CANCELLED:
            return Result.failure(ValidationError(ErrorCodes.RECEIPT_CANCELLED))
        return self.repo.update_receipt_status(receipt_id, CashVoucherStatus.CANCELLED)

    # ── Cash Payments (UC-CASH-02) ────────────────────────────────────

    def create_payment(
        self,
        payment_date: date,
        payment_type: CashPaymentType,
        receiver_name: str,
        amount: Decimal,
        amount_in_words: str,
        account_code: str,
        counter_account: str,
        description: str,
        created_by: str,
        currency: str = "VND",
        fx_rate: Optional[Decimal] = None,
        reference_number: Optional[str] = None,
        supporting_doc_ref: Optional[str] = None,
    ) -> Result:
        payment_number = self._next_payment_number(payment_date)
        try:
            payment = CashPayment(
                payment_number=payment_number,
                payment_date=payment_date,
                payment_type=payment_type,
                receiver_name=receiver_name,
                amount=amount,
                amount_in_words=amount_in_words,
                currency=currency,
                fx_rate=fx_rate,
                account_code=account_code,
                counter_account=counter_account,
                reference_number=reference_number,
                supporting_doc_ref=supporting_doc_ref,
                description=description,
                status=CashVoucherStatus.DRAFT,
                created_by=created_by,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_payment(payment)

    def get_payment(self, payment_id: int) -> Result:
        payment = self.repo.get_payment(payment_id)
        if not payment:
            return Result.failure(AccountError(ErrorCodes.PAYMENT_NOT_FOUND, payment_id=payment_id))
        return Result.success(payment)

    def list_payments(self, status: Optional[str] = None) -> List[CashPayment]:
        return self.repo.list_payments(status=status)

    def approve_payment(self, payment_id: int, approved_by: str) -> Result:
        payment = self.repo.get_payment(payment_id)
        if not payment:
            return Result.failure(AccountError(ErrorCodes.PAYMENT_NOT_FOUND, payment_id=payment_id))
        if payment.status != CashVoucherStatus.DRAFT:
            return Result.failure(ValidationError(ErrorCodes.ONLY_DRAFT_PAYMENT_APPROVED))
        return self.repo.update_payment_status(payment_id, CashVoucherStatus.APPROVED, approved_by)

    def cancel_payment(self, payment_id: int) -> Result:
        payment = self.repo.get_payment(payment_id)
        if not payment:
            return Result.failure(AccountError(ErrorCodes.PAYMENT_NOT_FOUND, payment_id=payment_id))
        if payment.status == CashVoucherStatus.CANCELLED:
            return Result.failure(ValidationError(ErrorCodes.PAYMENT_CANCELLED))
        return self.repo.update_payment_status(payment_id, CashVoucherStatus.CANCELLED)

    # ── Bank Accounts (UC-CASH-04) ────────────────────────────────────

    def create_bank_account(
        self,
        bank_name: str,
        branch: str,
        account_number: str,
        account_holder: str,
        coa_code: str,
        currency: str = "VND",
        swift_code: Optional[str] = None,
        iban: Optional[str] = None,
        opening_balance: Decimal = Decimal("0"),
        signatories: Optional[List[str]] = None,
        authorization_limit: Decimal = Decimal("0"),
    ) -> Result:
        try:
            ba = BankAccount(
                bank_name=bank_name,
                branch=branch,
                account_number=account_number,
                account_holder=account_holder,
                currency=currency,
                coa_code=coa_code,
                swift_code=swift_code,
                iban=iban,
                opening_balance=opening_balance,
                signatories=signatories or [],
                authorization_limit=authorization_limit,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_bank_account(ba)

    def get_bank_account(self, ba_id: int) -> Result:
        ba = self.repo.get_bank_account(ba_id)
        if not ba:
            return Result.failure(AccountError(ErrorCodes.BANK_ACCOUNT_NOT_FOUND, ba_id=ba_id))
        return Result.success(ba)

    def list_bank_accounts(self, status: Optional[str] = None) -> Result:
        return Result.success(self.repo.list_bank_accounts(status=status))

    def get_bank_balance(self, ba_id: int, as_of: Optional[date] = None) -> Result:
        ba = self.repo.get_bank_account(ba_id)
        if not ba:
            return Result.failure(AccountError(ErrorCodes.BANK_ACCOUNT_NOT_FOUND, ba_id=ba_id))
        balance = self.repo.calculate_bank_balance(ba_id, as_of=as_of)
        return Result.success({
            "bank_account_id": ba_id,
            "account_number": ba.account_number,
            "bank_name": ba.bank_name,
            "currency": ba.currency,
            "opening_balance": str(ba.opening_balance),
            "current_balance": str(balance),
            "as_of": (as_of or date.today()).isoformat(),
        })

    # ── Cash Balance ──────────────────────────────────────────────────

    def get_cash_balance(self, account_code: str = "1111") -> Result:
        balance = self.repo.get_cash_balance(account_code)
        return Result.success({
            "account_code": account_code,
            "balance": str(balance),
            "currency": "VND",
            "as_of": date.today().isoformat(),
        })

    # ── Cash Book Report (So quy tien mat — UC-CASH-11) ──────────────

    def generate_cash_book_report(
        self,
        account_code: str = "1111",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Result:
        to_date = to_date or date.today()
        from_date = from_date or to_date.replace(day=1)

        entries = self.repo.get_cash_book_entries(account_code, from_date, to_date)

        opening = self.gl_repo.get_account_balance(account_code)
        running = opening.get("opening_balance", opening.get("balance", Decimal("0")))
        rows = []
        for e in entries:
            running += e["debit"] - e["credit"]
            rows.append({
                "date": e["date"].isoformat(),
                "number": e["number"],
                "type": e["voucher_type"],
                "counter_party": e["counter_party"],
                "description": e["description"],
                "debit": str(e["debit"]),
                "credit": str(e["credit"]),
                "balance": str(running),
                "counter_account": e["counter_account"],
            })

        return Result.success({
            "account_code": account_code,
            "period": f"{from_date.isoformat()} to {to_date.isoformat()}",
            "opening_balance": str(running - sum(e["debit"] - e["credit"] for e in entries)),
            "closing_balance": str(running),
            "rows": rows,
        })

    # ── Cash Count Report (Bien ban kiem ke quy) ─────────────────────

    def generate_cash_count_report(self, count_id: int) -> Result:
        counts = self.repo.list_daily_cash_counts()
        count = None
        for c in counts:
            if c.id == count_id:
                count = c
                break
        if not count:
            return Result.failure(AccountError(ErrorCodes.DAILY_COUNT_NOT_FOUND, count_id=count_id))

        diff_type = "Phu hop" if count.difference == 0 else "Thua quy" if count.difference > 0 else "Thieu quy"
        diff_entries = []
        if count.difference > 0:
            diff_entries.append({
                "description": "Tai san thua cho giai quyet (3381)",
                "debit": str(count.difference),
                "credit": "0",
            })
        elif count.difference < 0:
            diff_entries.append({
                "description": "Tai san thieu cho xu ly (1381)",
                "debit": "0",
                "credit": str(abs(count.difference)),
            })

        return Result.success({
            "count": {
                "id": count.id,
                "count_date": count.count_date.isoformat(),
                "account_code": count.account_code,
                "expected_balance": str(count.expected_balance),
                "actual_balance": str(count.actual_balance),
                "difference": str(count.difference),
                "difference_type": diff_type,
                "denomination_breakdown": count.denomination_breakdown,
                "notes": count.notes,
                "counted_by": count.counted_by,
                "witnessed_by": count.witnessed_by,
            },
        })

    # ── Bank Statement Import (UC-CASH-05) ────────────────────────────

    def import_bank_statement(
        self,
        bank_account_id: int,
        statement_date: date,
        opening_balance: Decimal,
        closing_balance: Decimal,
        transactions: List[dict],
        source: str = "csv",
    ) -> Result:
        try:
            bank_txns = []
            for tx in transactions:
                bank_txns.append(BankTransaction(
                    bank_account_id=bank_account_id,
                    transaction_date=date.fromisoformat(tx["transaction_date"]),
                    value_date=date.fromisoformat(tx["value_date"]) if tx.get("value_date") else None,
                    amount=_vnd(Decimal(str(tx["amount"]))),
                    is_debit=tx.get("is_debit", False),
                    reference=tx.get("reference", ""),
                    description=tx.get("description", ""),
                    matched_entry_id=tx.get("matched_entry_id"),
                ))
            stmt = BankStatement(
                bank_account_id=bank_account_id,
                statement_date=statement_date,
                opening_balance=_vnd(opening_balance),
                closing_balance=_vnd(closing_balance),
                transactions=bank_txns,
                source=source,
            )
        except (ValidationError, ValueError, KeyError) as e:
            return Result.failure(ValidationError(ErrorCodes.INVALID_STATEMENT_DATA, error=str(e)))

        existing = self.repo.list_statements(bank_account_id=bank_account_id)
        for e in existing:
            if e.statement_date == statement_date and e.closing_balance == stmt.closing_balance:
                return Result.failure(ValidationError(ErrorCodes.DUPLICATE_STATEMENT, account_id=bank_account_id, date=statement_date))

        net_change = sum((-t.amount if t.is_debit else t.amount) for t in bank_txns)
        running_check = opening_balance + net_change
        if abs(running_check - closing_balance) > Decimal("0.01"):
            return Result.failure(ValidationError(ErrorCodes.RUNNING_BALANCE_MISMATCH, expected=running_check, actual=closing_balance))

        return self.repo.create_statement(stmt)

    def parse_csv_statement(
        self,
        bank_account_id: int,
        csv_lines: List[str],
        fmt: str = "vietcombank",
    ) -> Result:
        try:
            import csv
            from io import StringIO
            reader = csv.DictReader(StringIO("\n".join(csv_lines)))

            txns = []
            for row in reader:
                if fmt == "vietcombank":
                    txn = {
                        "transaction_date": row.get("Ngay giao dich", row.get("Date", "")),
                        "value_date": row.get("Ngay hieu luc", row.get("Value Date", "")),
                        "amount": row.get("So tien", row.get("Amount", "0")),
                        "is_debit": row.get("Loai", row.get("Type", "")).strip().upper() in ("OUT", "DEBIT", "CHI", "-"),
                        "reference": row.get("Ma giao dich", row.get("Reference", "")),
                        "description": row.get("Dien giai", row.get("Description", "")),
                        "_opening_balance": row.get("_opening_balance", ""),
                        "_closing_balance": row.get("_closing_balance", ""),
                    }
                else:
                    txn = {
                        "transaction_date": row.get("Date", row.get("date", "")),
                        "value_date": row.get("Value Date", row.get("value_date", "")),
                        "amount": row.get("Amount", row.get("amount", "0")),
                        "is_debit": row.get("Type", row.get("type", "")).strip().upper() in ("DEBIT", "OUT", "WITHDRAWAL"),
                        "reference": row.get("Reference", row.get("reference", "")),
                        "description": row.get("Description", row.get("description", "")),
                        "_opening_balance": row.get("_opening_balance", ""),
                        "_closing_balance": row.get("_closing_balance", ""),
                    }
                txns.append(txn)

            if not txns:
                return Result.failure(ValidationError(ErrorCodes.NO_TRANSACTIONS_CSV))

            first = txns[0]
            opening = Decimal(str(first.get("_opening_balance", "0"))) if "_opening_balance" in first else Decimal("0")
            last = txns[-1]
            closing = Decimal(str(last.get("_closing_balance", "0"))) if "_closing_balance" in last else Decimal("0")

            return self.import_bank_statement(
                bank_account_id=bank_account_id,
                statement_date=date.today(),
                opening_balance=opening,
                closing_balance=closing,
                transactions=txns,
                source="csv",
            )
        except Exception as e:
            return Result.failure(ValidationError(ErrorCodes.CSV_PARSE_ERROR, error=str(e)))

    # ── Auto-Match for Reconciliation ─────────────────────────────────

    def suggest_matches(
        self,
        bank_account_id: int,
        period: str,
    ) -> Result:
        stmt = self.repo.list_statements(bank_account_id=bank_account_id)
        period_start = f"{period}-01"
        gl_entries = self.repo.get_gl_entries_for_bank(
            coa_code=None,
            from_date=date.fromisoformat(period_start) if period else None,
            bank_account_id=bank_account_id,
        )
        unmatched_bank = []
        unmatched_gl = []
        suggestions = []

        all_txns = []
        for s in stmt:
            for t in s.transactions:
                if t.matched_entry_id:
                    continue
                all_txns.append(t)

        for txn in all_txns:
            matched = False
            for gl in gl_entries:
                if gl.get("matched", False):
                    continue
                ref_match = txn.reference and txn.reference == gl.get("reference", "")
                amount_match = abs(txn.amount - gl.get("amount", Decimal("0"))) <= Decimal("0.01")
                date_diff = abs((txn.transaction_date - gl.get("date", txn.transaction_date)).days)
                if ref_match or (amount_match and date_diff <= 3):
                    suggestions.append({
                        "bank_transaction_id": txn.id,
                        "bank_reference": txn.reference,
                        "bank_amount": str(txn.amount),
                        "bank_date": txn.transaction_date.isoformat(),
                        "gl_description": gl.get("description", ""),
                        "gl_amount": str(gl.get("amount", Decimal("0"))),
                        "gl_date": gl.get("date", txn.transaction_date).isoformat(),
                        "confidence": "high" if ref_match else "medium",
                        "match_type": "reference" if ref_match else "amount+date",
                    })
                    matched = True
                    gl["matched"] = True
                    break
            if not matched:
                unmatched_bank.append({
                    "id": txn.id,
                    "reference": txn.reference,
                    "amount": str(txn.amount),
                    "date": txn.transaction_date.isoformat(),
                    "description": txn.description,
                })

        for gl in gl_entries:
            if not gl.get("matched", False):
                unmatched_gl.append({
                    "journal_id": gl.get("journal_id"),
                    "description": gl.get("description", ""),
                    "amount": str(gl.get("amount", Decimal("0"))),
                    "date": gl.get("date").isoformat(),
                    "account": gl.get("account", ""),
                })

        return Result.success({
            "suggestions": suggestions,
            "unmatched_bank_transactions": unmatched_bank,
            "unmatched_gl_entries": unmatched_gl,
            "total_suggestions": len(suggestions),
            "total_unmatched_bank": len(unmatched_bank),
            "total_unmatched_gl": len(unmatched_gl),
        })

    # ── Bank Reconciliation (UC-CASH-06) ──────────────────────────────

    def create_reconciliation(
        self,
        bank_account_id: int,
        period: str,
        book_balance: Decimal,
        bank_balance: Decimal,
        deposits_in_transit: Decimal = Decimal("0"),
        outstanding_checks: Decimal = Decimal("0"),
        unrecorded_credits: Decimal = Decimal("0"),
        unrecorded_debits: Decimal = Decimal("0"),
        discrepancies: Optional[List[dict]] = None,
        reconciled_by: Optional[str] = None,
    ) -> Result:
        disc_entities = []
        for d in (discrepancies or []):
            disc_entities.append(ReconciliationDiscrepancy(
                reconciliation_id=0,
                discrepancy_type=ReconciliationDiscrepancyType(d["discrepancy_type"]),
                amount=_vnd(Decimal(str(d["amount"]))),
                entry_side=d["entry_side"],
                reference=d.get("reference"),
                description=d.get("description"),
                status=d.get("status", "unresolved"),
            ))
        try:
            recon = BankReconciliation(
                bank_account_id=bank_account_id,
                period=period,
                book_balance=book_balance,
                bank_balance=bank_balance,
                deposits_in_transit=deposits_in_transit,
                outstanding_checks=outstanding_checks,
                unrecorded_credits=unrecorded_credits,
                unrecorded_debits=unrecorded_debits,
                discrepancies=disc_entities,
                reconciled_by=reconciled_by,
                reconciled_at=datetime.now(timezone.utc) if reconciled_by else None,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_reconciliation(recon)

    def get_reconciliation(self, recon_id: int) -> Result:
        recon = self.repo.get_reconciliation(recon_id)
        if not recon:
            return Result.failure(AccountError(ErrorCodes.RECONCILIATION_NOT_FOUND, recon_id=recon_id))
        return Result.success(recon)

    # ── Petty Cash (UC-CASH-03b) ──────────────────────────────────────

    def create_petty_cash_fund(
        self,
        fund_code: str,
        custodian: str,
        limit_amount: Decimal,
        currency: str = "VND",
    ) -> Result:
        try:
            fund = PettyCashFund(
                fund_code=fund_code,
                custodian=custodian,
                limit_amount=limit_amount,
                currency=currency,
                established_date=date.today(),
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_petty_cash_fund(fund)

    def get_petty_cash_fund(self, fund_id: int) -> Result:
        fund = self.repo.get_petty_cash_fund(fund_id)
        if not fund:
            return Result.failure(AccountError(ErrorCodes.PETTY_CASH_FUND_NOT_FOUND, fund_id=fund_id))
        return Result.success(fund)

    def list_petty_cash_funds(self) -> Result:
        return Result.success(self.repo.list_petty_cash_funds())

    # ── Advances / Tam ung (UC-CASH-03a) ──────────────────────────────

    def create_advance(
        self,
        employee_name: str,
        employee_id: str,
        amount: Decimal,
        purpose: str,
        settlement_deadline: Optional[date] = None,
    ) -> Result:
        try:
            advance = Advance(
                employee_name=employee_name,
                employee_id=employee_id,
                amount=amount,
                advance_date=date.today(),
                purpose=purpose,
                settlement_deadline=settlement_deadline or date.today().replace(day=1, month=date.today().month % 12 + 1) if date.today().month == 12 else date.today().replace(month=date.today().month + 1),
                status="outstanding",
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_advance(advance)

    def get_advance(self, advance_id: int) -> Result:
        advance = self.repo.get_advance(advance_id)
        if not advance:
            return Result.failure(AccountError(ErrorCodes.ADVANCE_NOT_FOUND, advance_id=advance_id))
        return Result.success(advance)

    def settle_advance(self, advance_id: int, settlement_amount: Decimal) -> Result:
        advance = self.repo.get_advance(advance_id)
        if not advance:
            return Result.failure(AccountError(ErrorCodes.ADVANCE_NOT_FOUND, advance_id=advance_id))
        if advance.status == "settled":
            return Result.failure(ValidationError(ErrorCodes.ADVANCE_ALREADY_SETTLED))
        return self.repo.update_advance_settlement(advance_id, settlement_amount)

    # ── Cash Transfers (UC-CASH-07) ───────────────────────────────────

    def create_transfer(
        self,
        source_account: str,
        destination_account: str,
        amount: Decimal,
        reference: str,
        fx_rate: Optional[Decimal] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        try:
            transfer = CashTransfer(
                source_account=source_account,
                destination_account=destination_account,
                amount=_vnd(amount),
                transfer_date=date.today(),
                fx_rate=fx_rate,
                reference=reference,
                created_by=created_by,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_transfer(transfer)

    def get_transfer(self, transfer_id: int) -> Result:
        transfer = self.repo.get_transfer(transfer_id)
        if not transfer:
            return Result.failure(AccountError(ErrorCodes.CASH_TRANSFER_NOT_FOUND, transfer_id=transfer_id))
        return Result.success(transfer)

    # ── Daily Cash Count (UC-CASH-08) ─────────────────────────────────

    def create_daily_cash_count(
        self,
        account_code: str,
        expected_balance: Decimal,
        actual_balance: Decimal,
        counted_by: str,
        denomination_breakdown: Optional[dict] = None,
        notes: Optional[str] = None,
        witnessed_by: Optional[str] = None,
    ) -> Result:
        try:
            count = DailyCashCount(
                count_date=date.today(),
                account_code=account_code,
                expected_balance=_vnd(expected_balance),
                actual_balance=_vnd(actual_balance),
                denomination_breakdown=denomination_breakdown or {},
                notes=notes,
                counted_by=counted_by,
                witnessed_by=witnessed_by,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_daily_cash_count(count)

    def list_daily_cash_counts(self, account_code: Optional[str] = None) -> Result:
        return Result.success(self.repo.list_daily_cash_counts(account_code=account_code))

    # ── Cheques (UC-CASH-10) ──────────────────────────────────────────

    def create_cheque(
        self,
        cheque_number: str,
        cheque_book_id: int,
        payee: str,
        amount: Decimal,
        bank_account_id: int,
    ) -> Result:
        try:
            cheque = Cheque(
                cheque_number=cheque_number,
                cheque_book_id=cheque_book_id,
                payee=payee,
                amount=_vnd(amount),
                issue_date=date.today(),
                bank_account_id=bank_account_id,
            )
        except (ValidationError, ValueError) as e:
            return Result.failure(e)
        return self.repo.create_cheque(cheque)

    def get_cheque(self, cheque_id: int) -> Result:
        cheque = self.repo.get_cheque(cheque_id)
        if not cheque:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        return Result.success(cheque)

    # ── Bank Book Report (So tien gui NH — UC-CASH-11) ────────────────

    def generate_bank_book_report(
        self,
        bank_account_id: int,
        from_date: date,
        to_date: date,
        format: str = "json",
    ) -> Result:
        ba = self.repo.get_bank_account(bank_account_id)
        if not ba:
            return Result.failure(AccountError(ErrorCodes.BANK_ACCOUNT_NOT_FOUND, bank_account_id=bank_account_id))
        entries = self.repo.get_gl_entries_for_bank(
            coa_code=ba.coa_code,
            from_date=from_date,
            to_date=to_date,
            bank_account_id=bank_account_id,
        )
        rows = []
        running = ba.opening_balance
        for e in entries:
            amount = e.get("amount", Decimal("0"))
            is_debit = e.get("is_debit", True)
            if is_debit:
                running += amount
            else:
                running -= amount
            rows.append({
                "date": e.get("date").isoformat(),
                "reference": e.get("reference", e.get("journal_number", "")),
                "bank_code": e.get("account", ""),
                "description": e.get("description", ""),
                "debit": str(amount) if is_debit else "0",
                "credit": str(amount) if not is_debit else "0",
                "balance": str(running),
            })

        return Result.success({
            "bank_account_id": bank_account_id,
            "bank_name": ba.bank_name,
            "account_number": ba.account_number,
            "currency": ba.currency,
            "period": f"{from_date.isoformat()} to {to_date.isoformat()}",
            "opening_balance": str(ba.opening_balance),
            "closing_balance": str(running),
            "rows": rows,
        })

    # ── Bank Reconciliation Report ────────────────────────────────────

    def generate_reconciliation_report(self, recon_id: int) -> Result:
        recon = self.repo.get_reconciliation(recon_id)
        if not recon:
            return Result.failure(AccountError(ErrorCodes.RECONCILIATION_NOT_FOUND, recon_id=recon_id))
        ba = self.repo.get_bank_account(recon.bank_account_id)
        summary = {
            "reconciliation_id": recon.id,
            "bank_account_id": recon.bank_account_id,
            "bank_name": ba.bank_name if ba else "N/A",
            "account_number": ba.account_number if ba else "N/A",
            "period": recon.period,
            "book_balance": str(recon.book_balance),
            "bank_balance": str(recon.bank_balance),
            "adjustments": {
                "deposits_in_transit": str(recon.deposits_in_transit),
                "outstanding_checks": str(recon.outstanding_checks),
                "unrecorded_credits": str(recon.unrecorded_credits),
                "unrecorded_debits": str(recon.unrecorded_debits),
            },
            "adjusted_book_balance": str(recon.adjusted_book_balance),
            "adjusted_bank_balance": str(recon.adjusted_bank_balance),
            "is_balanced": recon.is_balanced,
            "reconciled_by": recon.reconciled_by,
            "reconciled_at": recon.reconciled_at.isoformat() if recon.reconciled_at else None,
            "discrepancies": [
                {
                    "type": d.discrepancy_type.value,
                    "amount": str(d.amount),
                    "side": d.entry_side,
                    "reference": d.reference,
                    "description": d.description,
                    "status": d.status,
                }
                for d in recon.discrepancies
            ],
        }
        return Result.success({"data": summary})

    def _render_reconciliation_html(self, summary: dict) -> str:
        disc_rows = ""
        for d in summary.get("discrepancies", []):
            disc_rows += f"""<tr>
                <td>{d['type']}</td>
                <td>{d['side']}</td>
                <td>{d['amount']}</td>
                <td>{d.get('reference', '')}</td>
                <td>{d.get('description', '')}</td>
                <td>{d['status']}</td>
            </tr>\n"""
        adj = summary["adjustments"]
        balanced = "CO" if summary["is_balanced"] else "KHONG"
        return f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="utf-8"><title>BANG DOI CHIEU TIEN GUI NGAN HANG</title>
<style>
    body {{ font-family: 'Times New Roman', serif; font-size: 13px; }}
    h1 {{ text-align: center; font-size: 16px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid #000; padding: 4px 8px; text-align: left; }}
    .right {{ text-align: right; }}
    .center {{ text-align: center; }}
</style></head>
<body>
<h1>BANG DOI CHIEU TIEN GUI NGAN HANG</h1>
<p><strong>Don vi:</strong> {summary['bank_name']} - {summary['account_number']}</p>
<p><strong>Ky:</strong> {summary['period']}</p>

<h2>1. So du ke toan (Book Balance)</h2>
<table><tr><td>So du tren so ke toan</td><td class='right'>{summary['book_balance']}</td></tr>
<tr><td>+/- Khoan dieu chinh:</td></tr>
<tr><td>&nbsp;&nbsp;+ Khoan thu chua ghi so (Deposits in transit)</td><td class='right'>{adj['deposits_in_transit']}</td></tr>
<tr><td>&nbsp;&nbsp;- Khoan chi chua ghi so (Unrecorded debits)</td><td class='right'>{adj['unrecorded_debits']}</td></tr>
<tr><td>&nbsp;&nbsp;+ Khoan thu khac (Unrecorded credits)</td><td class='right'>{adj['unrecorded_credits']}</td></tr>
<tr><td><strong>So du dieu chinh (Adjusted Book Balance)</strong></td><td class='right'><strong>{summary['adjusted_book_balance']}</strong></td></tr></table>

<h2>2. So du ngan hang (Bank Balance)</h2>
<table><tr><td>So du tren sao ke ngan hang</td><td class='right'>{summary['bank_balance']}</td></tr>
<tr><td>+/- Khoan dieu chinh:</td></tr>
<tr><td>&nbsp;&nbsp;- Sec phat hanh chua thanh toan (Outstanding checks)</td><td class='right'>{adj['outstanding_checks']}</td></tr>
<tr><td><strong>So du dieu chinh (Adjusted Bank Balance)</strong></td><td class='right'><strong>{summary['adjusted_bank_balance']}</strong></td></tr></table>

<h3>Ket qua: {'DA CAN DOI' if summary['is_balanced'] else 'CHUA CAN DOI'}</h3>

<h2>3. Chenh lech (Discrepancies)</h2>
<table><thead><tr><th>Loai</th><th>Ben</th><th>So tien</th><th>Tham chieu</th><th>Dien giai</th><th>Trang thai</th></tr></thead>
<tbody>{disc_rows}</tbody></table>
<p><em>Ngay lap: {summary.get('reconciled_at', '')[:10] if summary.get('reconciled_at') else ''}</em></p>
<p><em>Nguoi lap: {summary.get('reconciled_by', '')}</em></p>
</body>
</html>"""

    # ── Cheque Lifecycle ──────────────────────────────────────────────

    def issue_cheque(
        self,
        cheque_id: int,
        payee: str,
        amount: Decimal,
        bank_account_id: int,
    ) -> Result:
        cheque = self.repo.get_cheque(cheque_id)
        if not cheque:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        if cheque.status != ChequeStatus.NEW:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION, action="issue", subject="cheque", state=cheque.status.value))
        return self.repo.update_cheque_status(
            cheque_id, ChequeStatus.ISSUED,
            payee=payee,
            amount=_vnd(amount),
            bank_account_id=bank_account_id,
        )

    def clear_cheque(self, cheque_id: int, cleared_date: date) -> Result:
        cheque = self.repo.get_cheque(cheque_id)
        if not cheque:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        if cheque.status != ChequeStatus.ISSUED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION, action="clear", subject="cheque", state=cheque.status.value))
        return self.repo.update_cheque_status(cheque_id, ChequeStatus.CLEARED, cleared_date=cleared_date)

    def cancel_cheque(self, cheque_id: int, reason: str) -> Result:
        cheque = self.repo.get_cheque(cheque_id)
        if not cheque:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        if cheque.status in (ChequeStatus.CLEARED, ChequeStatus.CANCELLED):
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION, action="cancel", subject="cheque", state=cheque.status.value))
        return self.repo.update_cheque_status(cheque_id, ChequeStatus.CANCELLED, cancel_reason=reason)

    def stop_cheque(self, cheque_id: int, reason: str) -> Result:
        cheque = self.repo.get_cheque(cheque_id)
        if not cheque:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        if cheque.status != ChequeStatus.ISSUED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION, action="stop", subject="cheque", state=cheque.status.value))
        return self.repo.update_cheque_status(cheque_id, ChequeStatus.STOPPED, cancel_reason=reason)

    def bounce_cheque(self, cheque_id: int, reason: str) -> Result:
        cheque = self.repo.get_cheque(cheque_id)
        if not cheque:
            return Result.failure(AccountError(ErrorCodes.CHEQUE_NOT_FOUND, cheque_id=cheque_id))
        if cheque.status != ChequeStatus.ISSUED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION, action="bounce", subject="cheque", state=cheque.status.value))
        return self.repo.update_cheque_status(cheque_id, ChequeStatus.BOUNCED, cancel_reason=reason)

    def get_stale_cheques(self, days: int = 180) -> Result:
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        cheques = self.repo.list_cheques()
        stale = [c for c in cheques if c.status == ChequeStatus.ISSUED and c.issue_date < cutoff]
        return Result.success({
            "stale_cheques": [
                {
                    "id": c.id,
                    "cheque_number": c.cheque_number,
                    "payee": c.payee,
                    "amount": str(c.amount),
                    "issue_date": c.issue_date.isoformat(),
                    "days_outstanding": (date.today() - c.issue_date).days,
                }
                for c in stale
            ],
            "total": len(stale),
        })

    # ── Helpers ───────────────────────────────────────────────────────

    def _next_receipt_number(self, dt: date) -> str:
        prefix = f"PT-{dt.year}{dt.month:02d}-"
        existing = self.repo.list_receipts()
        max_seq = 0
        for r in existing:
            if r.receipt_number.startswith(prefix):
                try:
                    seq = int(r.receipt_number.split("-")[-1])
                    if seq > max_seq:
                        max_seq = seq
                except (IndexError, ValueError):
                    pass
        return f"{prefix}{max_seq + 1:05d}"

    def _next_payment_number(self, dt: date) -> str:
        prefix = f"PC-{dt.year}{dt.month:02d}-"
        existing = self.repo.list_payments()
        max_seq = 0
        for p in existing:
            if p.payment_number.startswith(prefix):
                try:
                    seq = int(p.payment_number.split("-")[-1])
                    if seq > max_seq:
                        max_seq = seq
                except (IndexError, ValueError):
                    pass
        return f"{prefix}{max_seq + 1:05d}"
