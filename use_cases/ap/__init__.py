from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from domain import (
    Vendor, VendorType, VendorGroup, VendorStatus,
    APInvoice, APInvoiceType, APInvoiceStatus, APInvoiceLine,
    APPayment, APPaymentStatus, APPaymentMethod, APPaymentAllocation,
    VendorPrepayment, PrepaymentStatus,
    APProvision, ProvisionStatus, APAgingSnapshot,
    FCTDeclaration, FCTMethod, FCTStatus,
    IntercompanyInvoice,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.ap_repository import APRepository
from infrastructure.repositories.gl_repository import GLRepository
from infrastructure.models.ap_models import (
    APInvoiceModel, APPaymentModel, VendorPrepaymentModel,
    APInvoiceStatusDB, APPaymentStatusDB,
)
from use_cases.gl import GLUseCases


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


def _calc_aging_bucket(days_past_due: int) -> str:
    if days_past_due <= 0:
        return "current"
    elif days_past_due <= 30:
        return "bucket_1_30"
    elif days_past_due <= 60:
        return "bucket_31_60"
    elif days_past_due <= 90:
        return "bucket_61_90"
    elif days_past_due <= 180:
        return "bucket_91_180"
    elif days_past_due <= 365:
        return "bucket_181_365"
    else:
        return "bucket_365_plus"


def _provision_pct_circular_48(days_past_due: int) -> Decimal:
    if days_past_due <= 180:
        return Decimal("0")
    elif days_past_due <= 365:
        return Decimal("0.30")
    elif days_past_due <= 730:
        return Decimal("0.50")
    elif days_past_due <= 1095:
        return Decimal("0.70")
    else:
        return Decimal("1.00")


_DISCOUNT_WINDOW_MAP: Dict[str, int] = {
    "net_15": 15, "net_30": 30, "net_45": 45, "net_60": 60,
    "net_90": 90, "due_on_receipt": 0,
}

_DOA_MATRIX = [
    (Decimal("50000000000"), "ceo_board"),
    (Decimal("5000000000"), "cfo"),
    (Decimal("500000000"), "ap_manager"),
    (Decimal("0"), "ap_supervisor"),
]


def _required_approver(amount: Decimal) -> str:
    for threshold, role in _DOA_MATRIX:
        if amount >= threshold:
            return role
    return "ap_supervisor"


class APUseCases:
    def __init__(self, session: Session):
        self.session = session
        self.repo = APRepository(session)
        self.gl = GLUseCases(session)
        self.gl_repo = GLRepository(session)

    # ── helpers ────────────────────────────────────────────────────────

    def _check_period_open(self, period: Optional[str]) -> bool:
        if not period:
            return True
        return not self.gl_repo.is_period_closed(period)

    def _next_invoice_number(self) -> str:
        today = date.today()
        prefix = f"AP-{today.strftime('%Y%m')}-"
        max_num = self.repo.get_max_invoice_number(prefix)
        if max_num is None:
            seq = 1
        else:
            seq = int(max_num) + 1
        return f"{prefix}{seq:05d}"

    def _next_payment_number(self) -> str:
        today = date.today()
        prefix = f"PMT-{today.strftime('%Y%m')}-"
        max_num = self.repo.get_max_payment_number(prefix)
        if max_num is None:
            seq = 1
        else:
            seq = int(max_num) + 1
        return f"{prefix}{seq:05d}"

    def _calc_due_date(
        self, invoice_date: date, vendor_id: int,
        vendor_default_terms: Optional[str] = None,
    ) -> date:
        vendor = self.repo.get_vendor(vendor_id)
        terms = vendor_default_terms or (vendor.payment_terms if vendor else "net_30")
        days = _DISCOUNT_WINDOW_MAP.get(terms, 30)
        return invoice_date + timedelta(days=days)

    def _post_to_gl(
        self,
        transaction_type: str,
        invoice: Optional[APInvoice] = None,
        payment: Optional[APPayment] = None,
        lines: Optional[List[Dict[str, Any]]] = None,
    ) -> Result:
        if lines is None:
            lines = []
        if not lines:
            if transaction_type == "invoice" and invoice:
                lines = [
                    {"account_id": invoice.coa_code or "331", "debit": Decimal("0"),
                     "credit": invoice.total_amount, "description": f"AP invoice {invoice.invoice_number}"},
                ]
                line_total = invoice.total_amount
                for line in invoice.lines:
                    expense_acct = line.coa_code or "641"
                    lines.insert(0, {
                        "account_id": expense_acct,
                        "debit": line.line_amount,
                        "credit": Decimal("0"),
                        "description": line.description,
                    })
                if invoice.tax_amount > Decimal("0"):
                    lines.append({
                        "account_id": "1331",
                        "debit": invoice.tax_amount,
                        "credit": Decimal("0"),
                        "description": f"Input VAT on {invoice.invoice_number}",
                    })
            elif transaction_type == "payment" and payment:
                vendor = self.repo.get_vendor(payment.vendor_id) if payment.vendor_id else None
                ap_account = vendor.coa_code if vendor and vendor.coa_code else "331"
                lines = [
                    {"account_id": ap_account, "debit": payment.net_amount,
                     "credit": Decimal("0"), "description": f"Payment {payment.payment_number}"},
                    {"account_id": "112", "debit": Decimal("0"),
                     "credit": payment.net_amount, "description": f"Payment {payment.payment_number}"},
                ]
                if payment.discount_taken > Decimal("0"):
                    lines.append({
                        "account_id": ap_account, "debit": payment.discount_taken,
                        "credit": Decimal("0"),
                        "description": f"Discount on {payment.payment_number}",
                    })
                    lines.append({
                        "account_id": "515", "debit": Decimal("0"),
                        "credit": payment.discount_taken,
                        "description": f"Discount income on {payment.payment_number}",
                    })
            elif transaction_type == "credit_note" and invoice:
                lines = [
                    {"account_id": invoice.coa_code or "331", "debit": invoice.total_amount,
                     "credit": Decimal("0"), "description": f"Credit note {invoice.invoice_number}"},
                ]
                for line in invoice.lines:
                    expense_acct = line.coa_code or "641"
                    lines.append({
                        "account_id": expense_acct, "debit": Decimal("0"),
                        "credit": line.line_amount, "description": f"CN {invoice.invoice_number} - {line.description}",
                    })
                if invoice.tax_amount > Decimal("0"):
                    lines.append({
                        "account_id": "1331", "debit": Decimal("0"),
                        "credit": invoice.tax_amount,
                        "description": f"VAT reversal on CN {invoice.invoice_number}",
                    })
            elif transaction_type == "debit_note" and invoice:
                lines = [
                    {"account_id": invoice.coa_code or "331", "debit": Decimal("0"),
                     "credit": invoice.total_amount, "description": f"Debit note {invoice.invoice_number}"},
                ]
                for line in invoice.lines:
                    expense_acct = line.coa_code or "641"
                    lines.append({
                        "account_id": expense_acct, "debit": line.line_amount,
                        "credit": Decimal("0"), "description": f"DN {invoice.invoice_number} - {line.description}",
                    })
            elif transaction_type == "prepayment":
                lines = [
                    {"account_id": "331", "debit": Decimal("0"),
                     "credit": Decimal("0"), "description": "Prepayment"},
                ]

        total_debit = sum(_vnd(Decimal(str(l.get("debit", 0)))) for l in lines)
        total_credit = sum(_vnd(Decimal(str(l.get("credit", 0)))) for l in lines)
        if abs(total_debit - total_credit) > Decimal("0.001"):
            return Result.failure(ValidationError(
                ErrorCodes.DOUBLE_ENTRY_VIOLATION,
                debit=str(total_debit), credit=str(total_credit),
            ))

        period = None
        if invoice:
            period = invoice.period
        if not period and payment:
            period = payment.payment_date.strftime("%Y-%m")
        if period and not self._check_period_open(period):
            return Result.failure(ValidationError(ErrorCodes.PERIOD_CLOSED_OP, period=period))

        from random import randint
        return self.gl.create_entry(
            journal_number=f"JV{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}{randint(10,99)}",
            transaction_date=date.today(),
            description=f"AP auto-post: {transaction_type}",
            lines=lines,
            period=period,
            source_module="ap",
            created_by="system",
        )

    # ── UC-AP-01: Vendor CRUD ─────────────────────────────────────────

    def create_vendor(
        self,
        vendor_code: str,
        vendor_name: str,
        vendor_type: VendorType = VendorType.ENTERPRISE,
        vendor_group: VendorGroup = VendorGroup.DOMESTIC,
        tax_code: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: str = "VN",
        contact_person: Optional[str] = None,
        payment_terms: str = "net_30",
        currency: str = "VND",
        bank_name: Optional[str] = None,
        bank_account: Optional[str] = None,
        bank_swift: Optional[str] = None,
        credit_limit: Decimal = Decimal("0"),
        coa_code: Optional[str] = None,
        foreign_ct_type: Optional[str] = None,
        foreign_vat_rate: Optional[Decimal] = None,
        foreign_cit_rate: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> Result:
        vendor = Vendor(
            vendor_code=vendor_code,
            vendor_name=vendor_name,
            vendor_type=vendor_type,
            vendor_group=vendor_group,
            tax_code=tax_code,
            email=email,
            phone=phone,
            address=address,
            city=city,
            country=country,
            contact_person=contact_person,
            payment_terms=payment_terms,
            currency=currency,
            bank_name=bank_name,
            bank_account=bank_account,
            bank_swift=bank_swift,
            credit_limit=credit_limit,
            coa_code=coa_code,
            foreign_ct_type=foreign_ct_type,
            foreign_vat_rate=foreign_vat_rate,
            foreign_cit_rate=foreign_cit_rate,
            notes=notes,
        )
        return self.repo.create_vendor(vendor)

    def get_vendor(self, vendor_id: int) -> Optional[Vendor]:
        return self.repo.get_vendor(vendor_id)

    def get_vendor_by_code(self, code: str) -> Optional[Vendor]:
        return self.repo.get_vendor_by_code(code)

    def list_vendors(
        self,
        vendor_type: Optional[VendorType] = None,
        vendor_group: Optional[VendorGroup] = None,
        status: Optional[VendorStatus] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Vendor]:
        return self.repo.list_vendors(
            vendor_type=vendor_type, vendor_group=vendor_group,
            status=status, search=search, limit=limit, offset=offset,
        )

    def update_vendor(self, vendor_id: int, **updates) -> Optional[Vendor]:
        return self.repo.update_vendor(vendor_id, **updates)

    def suspend_vendor(self, vendor_id: int) -> Result:
        vendor = self.repo.update_vendor(vendor_id, status=VendorStatus.SUSPENDED)
        if not vendor:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(vendor_id)))
        return Result.success(vendor)

    def activate_vendor(self, vendor_id: int) -> Result:
        vendor = self.repo.get_vendor(vendor_id)
        if not vendor:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(vendor_id)))
        if vendor.status == VendorStatus.BLOCKED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Cannot activate blocked vendor"))
        updated = self.repo.update_vendor(vendor_id, status=VendorStatus.ACTIVE)
        return Result.success(updated)

    def block_vendor(self, vendor_id: int) -> Result:
        vendor = self.repo.update_vendor(vendor_id, status=VendorStatus.BLOCKED)
        if not vendor:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(vendor_id)))
        return Result.success(vendor)

    def delete_vendor(self, vendor_id: int) -> Result:
        outstanding = self.repo.get_vendor_outstanding(vendor_id)
        if outstanding > Decimal("0"):
            return Result.failure(ValidationError(ErrorCodes.CUSTOMER_HAS_OPEN_AR,
                                                  id=str(vendor_id)))
        ok = self.repo.delete_vendor(vendor_id)
        if not ok:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(vendor_id)))
        return Result.success(None)

    # ── UC-AP-02: Invoice ─────────────────────────────────────────────

    def create_invoice(
        self,
        invoice_number: str,
        vendor_id: int,
        invoice_date: date,
        due_date: Optional[date] = None,
        amount: Decimal = Decimal("0"),
        lines: Optional[List[APInvoiceLine]] = None,
        vendor_code: Optional[str] = None,
        vendor_name: Optional[str] = None,
        invoice_type: APInvoiceType = APInvoiceType.NON_PO,
        discount_amount: Decimal = Decimal("0"),
        discount_percent: Optional[Decimal] = None,
        discount_date: Optional[date] = None,
        tax_amount: Decimal = Decimal("0"),
        total_amount: Optional[Decimal] = None,
        currency: str = "VND",
        fx_rate: Optional[Decimal] = None,
        po_number: Optional[str] = None,
        gr_number: Optional[str] = None,
        reference: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[str] = None,
        coa_code: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        vendor = self.repo.get_vendor(vendor_id)
        if not vendor:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(vendor_id)))
        if vendor.status != VendorStatus.ACTIVE:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Vendor not active"))

        if total_amount is None:
            total_amount = _vnd(amount - discount_amount + tax_amount)

        if not due_date:
            due_date = self._calc_due_date(invoice_date, vendor_id)

        lines_list = lines or []

        period = period or invoice_date.strftime("%Y-%m")
        if not self._check_period_open(period):
            return Result.failure(ValidationError(ErrorCodes.PERIOD_CLOSED_OP, period=period))

        invoice_code = vendor_code or vendor.vendor_code
        invoice_name = vendor_name or vendor.vendor_name
        invoice = APInvoice(
            invoice_number=invoice_number,
            vendor_id=vendor_id,
            vendor_code=invoice_code,
            vendor_name=invoice_name,
            invoice_type=invoice_type,
            status=APInvoiceStatus.DRAFT,
            invoice_date=invoice_date,
            due_date=due_date,
            discount_date=discount_date,
            discount_percent=discount_percent,
            amount=amount,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            paid_amount=Decimal("0"),
            written_off_amount=Decimal("0"),
            balance_due=total_amount,
            currency=currency,
            fx_rate=fx_rate,
            po_number=po_number,
            gr_number=gr_number,
            reference=reference,
            description=description,
            period=period,
            coa_code=coa_code or vendor.coa_code or "331",
            created_by=created_by,
            lines=lines_list,
        )
        result = self.repo.create_invoice(invoice)
        if result.is_success():
            created = result.get_data()
            gl_result = self._post_to_gl("invoice", invoice=created)
            if gl_result.is_failure():
                return gl_result
        return result

    def get_invoice(self, invoice_id: int) -> Optional[APInvoice]:
        return self.repo.get_invoice(invoice_id)

    def get_invoice_by_number(self, number: str) -> Optional[APInvoice]:
        return self.repo.get_invoice_by_number(number)

    def list_invoices(
        self,
        vendor_id: Optional[int] = None,
        vendor_code: Optional[str] = None,
        status: Optional[APInvoiceStatus] = None,
        period: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[APInvoice]:
        return self.repo.list_invoices(
            vendor_id=vendor_id, vendor_code=vendor_code,
            status=status, period=period, limit=limit, offset=offset,
        )

    def approve_invoice(self, invoice_id: int, approved_by: Optional[str] = None) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.status not in (APInvoiceStatus.DRAFT, APInvoiceStatus.SUBMITTED,
                                  APInvoiceStatus.MATCHED):
            return Result.failure(ValidationError(ErrorCodes.ONLY_DRAFT_APPROVED,
                                                  id=str(invoice_id)))
        updated = self.repo.update_invoice(
            invoice_id,
            status=APInvoiceStatus.APPROVED,
            approved_by=approved_by,
            approved_at=datetime.now(timezone.utc),
        )
        if updated is None:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        return Result.success(updated)

    def cancel_invoice(self, invoice_id: int, reason: Optional[str] = None) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.status in (APInvoiceStatus.PAID_FULL, APInvoiceStatus.WRITTEN_OFF):
            return Result.failure(ValidationError(ErrorCodes.INVOICE_ALREADY_PAID,
                                                  id=str(invoice_id)))
        updated = self.repo.update_invoice(invoice_id, status=APInvoiceStatus.CANCELLED)
        if updated is None:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        return Result.success(updated)

    # ── UC-AP-03: Credit / Debit Notes ────────────────────────────────

    def create_credit_note(
        self,
        invoice_id: int,
        reason: str,
        amount: Decimal,
        tax_adjustment: Decimal = Decimal("0"),
        created_by: Optional[str] = None,
    ) -> Result:
        original = self.repo.get_invoice(invoice_id)
        if not original:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if original.status == APInvoiceStatus.CANCELLED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Cannot credit cancelled invoice"))
        if amount > original.total_amount:
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  amount=str(amount),
                                                  balance=str(original.total_amount)))
        if not reason:
            return Result.failure(ValidationError(ErrorCodes.REASON_EMPTY))

        cn_number = f"CN-{original.invoice_number}"
        cn_invoice = APInvoice(
            invoice_number=cn_number,
            vendor_id=original.vendor_id,
            vendor_code=original.vendor_code,
            vendor_name=original.vendor_name,
            invoice_type=original.invoice_type,
            status=APInvoiceStatus.APPROVED,
            invoice_date=date.today(),
            due_date=date.today(),
            amount=amount,
            discount_amount=Decimal("0"),
            tax_amount=tax_adjustment,
            total_amount=_vnd(amount + tax_adjustment),
            paid_amount=Decimal("0"),
            written_off_amount=Decimal("0"),
            balance_due=Decimal("0"),
            currency=original.currency,
            period=original.period,
            coa_code=original.coa_code,
            reference=original.invoice_number,
            description=reason,
            created_by=created_by,
        )
        result = self.repo.create_invoice(cn_invoice)
        if result.is_success():
            cn = result.get_data()
            self._post_to_gl("credit_note", invoice=cn)
            new_balance = _vnd(original.balance_due - amount - tax_adjustment)
            self.repo.update_invoice(invoice_id, balance_due=new_balance)
        return result

    def create_debit_note(
        self,
        invoice_id: int,
        reason: str,
        amount: Decimal,
        created_by: Optional[str] = None,
    ) -> Result:
        original = self.repo.get_invoice(invoice_id)
        if not original:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if original.status == APInvoiceStatus.CANCELLED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Cannot debit cancelled invoice"))
        if not reason:
            return Result.failure(ValidationError(ErrorCodes.REASON_EMPTY))

        dn_number = f"DN-{original.invoice_number}"
        dn_invoice = APInvoice(
            invoice_number=dn_number,
            vendor_id=original.vendor_id,
            vendor_code=original.vendor_code,
            vendor_name=original.vendor_name,
            invoice_type=original.invoice_type,
            status=APInvoiceStatus.APPROVED,
            invoice_date=date.today(),
            due_date=date.today(),
            amount=amount,
            discount_amount=Decimal("0"),
            tax_amount=Decimal("0"),
            total_amount=amount,
            paid_amount=Decimal("0"),
            written_off_amount=Decimal("0"),
            balance_due=Decimal("0"),
            currency=original.currency,
            period=original.period,
            coa_code=original.coa_code,
            reference=original.invoice_number,
            description=reason,
            created_by=created_by,
        )
        result = self.repo.create_invoice(dn_invoice)
        if result.is_success():
            dn = result.get_data()
            self._post_to_gl("debit_note", invoice=dn)
            new_balance = _vnd(original.balance_due + amount)
            self.repo.update_invoice(invoice_id, balance_due=new_balance)
        return result

    # ── UC-AP-04: Prepayment ──────────────────────────────────────────

    def create_prepayment(
        self,
        vendor_id: int,
        amount: Decimal,
        payment_date: date,
        expected_invoice_date: Optional[date] = None,
        reference: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        vendor = self.repo.get_vendor(vendor_id)
        if not vendor:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(vendor_id)))
        if vendor.status != VendorStatus.ACTIVE:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Vendor not active"))
        if amount <= Decimal("0"):
            return Result.failure(ValidationError(ErrorCodes.PAYMENT_AMOUNT_ZERO))

        prepayment = VendorPrepayment(
            vendor_id=vendor_id,
            amount=amount,
            unapplied_balance=amount,
            payment_date=payment_date,
            expected_invoice_date=expected_invoice_date,
            reference=reference,
            created_by=created_by,
        )
        result = self.repo.create_prepayment(prepayment)
        if result.is_success():
            self._post_to_gl("prepayment", lines=[
                {"account_id": "331", "debit": amount, "credit": Decimal("0"),
                 "description": f"Prepayment to {vendor.vendor_code}"},
                {"account_id": "112", "debit": Decimal("0"), "credit": amount,
                 "description": f"Prepayment to {vendor.vendor_code}"},
            ])
        return result

    def apply_prepayment(self, prepayment_id: int, invoice_id: int, amount: Decimal) -> Result:
        prepayment = self.repo.get_prepayment(prepayment_id)
        if not prepayment:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Prepayment", id=str(prepayment_id)))
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if prepayment.vendor_id != invoice.vendor_id:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Prepayment vendor != invoice vendor"))
        if amount > prepayment.unapplied_balance:
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  amount=str(amount),
                                                  balance=str(prepayment.unapplied_balance)))
        if amount > invoice.balance_due:
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  amount=str(amount),
                                                  balance=str(invoice.balance_due)))

        result = self.repo.apply_prepayment(prepayment_id, invoice_id, amount)
        if result.is_success():
            new_unapplied = _vnd(prepayment.unapplied_balance - amount)
            self.repo.update_prepayment(prepayment_id, unapplied_balance=new_unapplied)
        return result

    def get_prepayments(self, vendor_id: int) -> List[VendorPrepayment]:
        return self.repo.list_prepayments(vendor_id=vendor_id)

    # ── UC-AP-05: Payment Processing ──────────────────────────────────

    def create_payment_proposal(
        self,
        vendor_ids: List[int],
        due_date_from: date,
        due_date_to: date,
        payment_method: APPaymentMethod = APPaymentMethod.BANK_TRANSFER,
        created_by: Optional[str] = None,
    ) -> Result:
        invoices = self.repo.get_due_invoices(
            vendor_ids=vendor_ids,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
        )
        if not invoices:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id="no_due_invoices"))

        grouped: Dict[int, List[APInvoice]] = {}
        for inv in invoices:
            grouped.setdefault(inv.vendor_id, []).append(inv)

        proposal_lines = []
        total_proposal = Decimal("0")
        for vid, inv_list in grouped.items():
            vendor = self.repo.get_vendor(vid)
            if not vendor or vendor.status == VendorStatus.BLOCKED:
                continue
            vendor_total = sum(i.balance_due for i in inv_list)
            total_proposal += vendor_total
            proposal_lines.append({
                "vendor_id": vid,
                "vendor_code": vendor.vendor_code if vendor else "",
                "vendor_name": vendor.vendor_name if vendor else "",
                "invoice_count": len(inv_list),
                "total_amount": vendor_total,
                "invoices": [{"invoice_id": i.id, "invoice_number": i.invoice_number,
                              "balance_due": i.balance_due, "due_date": str(i.due_date)}
                             for i in inv_list],
            })

        proposal = {
            "vendor_ids": vendor_ids,
            "due_date_range": {"from": due_date_from.isoformat(), "to": due_date_to.isoformat()},
            "payment_method": payment_method.value,
            "total_proposal_amount": total_proposal,
            "line_count": len(proposal_lines),
            "lines": proposal_lines,
            "required_approver": _required_approver(total_proposal),
            "created_by": created_by,
        }
        return Result.success(proposal)

    def approve_payment_proposal(
        self,
        proposal_id: int,
        approved_by: Optional[str] = None,
    ) -> Result:
        return Result.success({"proposal_id": proposal_id, "approved_by": approved_by,
                               "status": "approved"})

    def execute_payment(
        self,
        payment_id: int,
        executed_by: Optional[str] = None,
    ) -> Result:
        payment = self.repo.get_payment(payment_id)
        if not payment:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Payment", id=str(payment_id)))
        if payment.status != APPaymentStatus.APPROVED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="Payment not approved"))
        updated = self.repo.update_payment(payment_id, status=APPaymentStatus.EXECUTED)
        if updated is None:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Payment", id=str(payment_id)))
        gl_result = self._post_to_gl("payment", payment=updated)
        if gl_result.is_failure():
            self.repo.update_payment(payment_id, status=APPaymentStatus.FAILED)
            return gl_result
        return Result.success(updated)

    def record_payment(
        self,
        invoice_id: int,
        payment_number: str,
        amount: Decimal,
        payment_date: date,
        payment_method: APPaymentMethod = APPaymentMethod.BANK_TRANSFER,
        discount_taken: Decimal = Decimal("0"),
        reference: Optional[str] = None,
        vendor_id: Optional[int] = None,
        notes: Optional[str] = None,
        bank_account_id: Optional[int] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if amount <= Decimal("0"):
            return Result.failure(ValidationError(ErrorCodes.PAYMENT_AMOUNT_ZERO))
        total_deduction = amount + discount_taken
        if total_deduction > (invoice.balance_due + Decimal("0.01")):
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  amount=str(total_deduction),
                                                  balance=str(invoice.balance_due)))

        net_amount = _vnd(amount - discount_taken)
        vid = vendor_id or invoice.vendor_id

        payment = APPayment(
            payment_number=payment_number,
            vendor_id=vid,
            payment_date=payment_date,
            amount=amount,
            discount_taken=discount_taken,
            net_amount=net_amount,
            payment_method=payment_method,
            bank_account_id=bank_account_id,
            reference=reference,
            status=APPaymentStatus.APPROVED,
            notes=notes,
            created_by=created_by,
        )
        result = self.repo.create_payment(payment)
        if not result.is_success():
            return result

        payment_domain = result.get_data()

        alloc = APPaymentAllocation(
            ap_payment_id=payment_domain.id,
            ap_invoice_id=invoice_id,
            allocated_amount=amount,
        )
        self.repo.create_payment_allocation(alloc)

        if discount_taken > Decimal("0"):
            disc_alloc = APPaymentAllocation(
                ap_payment_id=payment_domain.id,
                ap_invoice_id=invoice_id,
                allocated_amount=discount_taken,
                is_adjustment=True,
            )
            self.repo.create_payment_allocation(disc_alloc)

        new_paid = _vnd(invoice.paid_amount + amount + discount_taken)
        new_balance = _vnd(invoice.balance_due - amount - discount_taken)
        if new_balance <= Decimal("0.01"):
            new_status = APInvoiceStatus.PAID_FULL
            new_balance = Decimal("0")
        elif new_paid > Decimal("0"):
            new_status = APInvoiceStatus.PAID_PARTIAL
        else:
            new_status = invoice.status
        self.repo.update_invoice(
            invoice_id,
            paid_amount=new_paid,
            balance_due=new_balance,
            status=new_status,
        )

        gl_result = self._post_to_gl("payment", payment=payment_domain)
        if gl_result.is_failure():
            return gl_result

        return Result.success(payment_domain)

    def get_payments_for_invoice(self, invoice_id: int) -> List[APPayment]:
        return self.repo.get_payments_for_invoice(invoice_id)

    def list_payments(
        self,
        vendor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[APPayment]:
        return self.repo.list_payments(
            vendor_id=vendor_id,
            date_from=date_from, date_to=date_to,
            limit=limit, offset=offset,
        )

    # ── UC-AP-06: Payment Scheduling ──────────────────────────────────

    def get_payment_schedule(
        self,
        vendor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        today = date.today()
        invoices = self.repo.get_scheduled_invoices(
            vendor_id=vendor_id, date_from=date_from, date_to=date_to,
        )
        schedule = []
        for inv in invoices:
            days_to_due = (inv.due_date - today).days
            discount_eligible = False
            if inv.discount_date and inv.discount_percent:
                if today <= inv.discount_date:
                    discount_eligible = True
            schedule.append({
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "vendor_id": inv.vendor_id,
                "vendor_code": inv.vendor_code,
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "discount_date": inv.discount_date.isoformat() if inv.discount_date else None,
                "discount_percent": inv.discount_percent,
                "discount_eligible": discount_eligible,
                "amount": inv.amount,
                "balance_due": inv.balance_due,
                "days_to_due": days_to_due,
                "status": inv.status.value,
            })
        return schedule

    # ── UC-AP-07: AP Aging ────────────────────────────────────────────

    def get_aging_report(
        self,
        as_of_date: Optional[date] = None,
        vendor_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        as_of = as_of_date or date.today()
        invoices = self.repo.get_invoices_with_balance(
            vendor_id=vendor_id, as_of=as_of,
        )

        vendor_data: Dict[int, Dict[str, Any]] = {}
        for inv in invoices:
            vid = inv.vendor_id
            if vid not in vendor_data:
                vendor_data[vid] = {
                    "vendor_id": vid,
                    "vendor_code": inv.vendor_code or "",
                    "vendor_name": inv.vendor_name or "",
                    "buckets": {
                        "current": Decimal("0"),
                        "bucket_1_30": Decimal("0"),
                        "bucket_31_60": Decimal("0"),
                        "bucket_61_90": Decimal("0"),
                        "bucket_91_180": Decimal("0"),
                        "bucket_181_365": Decimal("0"),
                        "bucket_365_plus": Decimal("0"),
                    },
                    "invoices": [],
                }
            days_past_due = (as_of - inv.due_date).days if inv.due_date <= as_of else 0
            bucket = _calc_aging_bucket(days_past_due)
            vendor_data[vid]["buckets"][bucket] += inv.balance_due
            vendor_data[vid]["invoices"].append({
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "due_date": inv.due_date.isoformat(),
                "days_past_due": days_past_due,
                "balance_due": inv.balance_due,
                "currency": inv.currency,
            })

        result = []
        for data in vendor_data.values():
            total_outstanding = sum(data["buckets"].values())
            max_days = max(
                (i["days_past_due"] for i in data["invoices"]),
                default=0,
            )
            result.append(data | {
                "total_outstanding": total_outstanding,
                "days_past_due_oldest": max_days,
            })
        return result

    def create_aging_snapshot(self, period: str) -> Result:
        as_of = date.today()
        live_aging = self.get_aging_report(as_of_date=as_of)
        created = []
        for entry in live_aging:
            snapshot = APAgingSnapshot(
                period=period,
                vendor_id=entry["vendor_id"],
                vendor_code=entry.get("vendor_code", ""),
                vendor_name=entry.get("vendor_name", ""),
                current_amount=entry["buckets"].get("current", Decimal("0")),
                bucket_1_30=entry["buckets"].get("bucket_1_30", Decimal("0")),
                bucket_31_60=entry["buckets"].get("bucket_31_60", Decimal("0")),
                bucket_61_90=entry["buckets"].get("bucket_61_90", Decimal("0")),
                bucket_91_180=entry["buckets"].get("bucket_91_180", Decimal("0")),
                bucket_181_365=entry["buckets"].get("bucket_181_365", Decimal("0")),
                bucket_365_plus=entry["buckets"].get("bucket_365_plus", Decimal("0")),
                total_outstanding=entry["total_outstanding"],
            )
            r = self.repo.create_aging_snapshot(snapshot)
            if r.is_success():
                created.append(snapshot)
        return Result.success({"period": period, "snapshots": len(created)})

    def get_aging_snapshots(self, period: str) -> List[APAgingSnapshot]:
        return self.repo.get_aging_snapshots(period)

    # ── UC-AP-08: Provision (Circular 48/2019) ────────────────────────

    def create_provisions(self, period: str, as_of_date: date) -> Result:
        invoices = self.repo.get_overdue_invoices(period)
        provisions = []
        for inv in invoices:
            days_past_due = (as_of_date - inv.due_date).days
            if days_past_due < 180:
                continue
            pct = _provision_pct_circular_48(days_past_due)
            if pct == Decimal("0"):
                continue
            provision = APProvision(
                vendor_id=inv.vendor_id,
                period=period,
                provision_percent=pct,
                overdue_days=days_past_due,
                invoice_total=inv.balance_due,
                provision_amount=_vnd(inv.balance_due * pct),
            )
            r = self.repo.create_provision(provision)
            if r.is_success():
                provisions.append(provision)
        total_provision = sum(p.provision_amount for p in provisions)
        if total_provision > Decimal("0"):
            self._post_to_gl("provision", lines=[
                {"account_id": "6422", "debit": total_provision, "credit": Decimal("0"),
                 "description": f"AP provision for {period}"},
                {"account_id": "229", "debit": Decimal("0"), "credit": total_provision,
                 "description": f"AP provision for {period}"},
            ])
        return Result.success({
            "period": period,
            "provisions": len(provisions),
            "total_amount": total_provision,
        })

    def get_provisions(self, period: str) -> List[APProvision]:
        return self.repo.get_provisions(period)

    # ── UC-AP-09: FCT / WHT (Circular 103/2014) ───────────────────────

    def calculate_fct(self, invoice_id: int) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        vendor = self.repo.get_vendor(invoice.vendor_id)
        if not vendor:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Vendor", id=str(invoice.vendor_id)))

        fct_method = FCTMethod.DEDUCTION
        if vendor.foreign_ct_type == "direct":
            fct_method = FCTMethod.DIRECT
        elif vendor.foreign_ct_type == "hybrid":
            fct_method = FCTMethod.HYBRID

        vat_rate = vendor.foreign_vat_rate or Decimal("0.05")
        cit_rate = vendor.foreign_cit_rate or Decimal("0.10")

        if fct_method == FCTMethod.DIRECT:
            gross_amount = invoice.total_amount
            vat_amount = Decimal("0")
            cit_amount = Decimal("0")
            net_amount = gross_amount
        elif fct_method == FCTMethod.DEDUCTION:
            gross_amount = invoice.total_amount
            vat_amount = _vnd(gross_amount * vat_rate)
            taxable = gross_amount - vat_amount
            cit_amount = _vnd(taxable * cit_rate)
            net_amount = _vnd(gross_amount - vat_amount - cit_amount)
        else:
            gross_amount = invoice.total_amount
            vat_amount = _vnd(gross_amount * vat_rate)
            cit_amount = _vnd(gross_amount * cit_rate)
            net_amount = _vnd(gross_amount - vat_amount - cit_amount)

        period = invoice.period or invoice.invoice_date.strftime("%Y-%m")
        due_date = invoice.due_date + timedelta(days=20)

        declaration = FCTDeclaration(
            vendor_id=invoice.vendor_id,
            period=period,
            invoice_id=invoice_id,
            fct_method=fct_method,
            vat_rate=vat_rate,
            cit_rate=cit_rate,
            gross_amount=gross_amount,
            vat_amount=vat_amount,
            cit_amount=cit_amount,
            net_amount=net_amount,
            due_date=due_date,
        )
        return Result.success(declaration)

    def remit_fct(self, declaration_id: int) -> Result:
        declaration = self.repo.get_fct_declaration(declaration_id)
        if not declaration:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="FCTDeclaration", id=str(declaration_id)))
        if declaration.status != FCTStatus.DECLARED:
            return Result.failure(ValidationError(ErrorCodes.STATE_TRANSITION,
                                                  detail="FCT not in DECLARED status"))
        total_withholding = _vnd(declaration.vat_amount + declaration.cit_amount)
        self._post_to_gl("fct_remittance", lines=[
            {"account_id": "3338", "debit": declaration.vat_amount, "credit": Decimal("0"),
             "description": f"FCT VAT remittance D{declaration.id}"},
            {"account_id": "3335", "debit": declaration.cit_amount, "credit": Decimal("0"),
             "description": f"FCT CIT remittance D{declaration.id}"},
            {"account_id": "112", "debit": Decimal("0"), "credit": total_withholding,
             "description": f"FCT remittance D{declaration.id}"},
        ])
        self.repo.update_fct_declaration(declaration_id, status=FCTStatus.REMITTED,
                                          remitted_at=datetime.now(timezone.utc))
        return Result.success({"declaration_id": declaration_id, "remitted": True})

    def get_fct_declarations(self, period: str) -> List[FCTDeclaration]:
        return self.repo.get_fct_declarations(period)

    def save_fct_declaration(self, declaration: FCTDeclaration) -> Result:
        return self.repo.create_fct_declaration(declaration)

    # ── UC-AP-10: Foreign Currency Revaluation ────────────────────────

    def revalue_fx(self, period: str, rate_source: str = "bank_selling") -> Result:
        invoices = self.repo.get_open_fx_invoices(period)
        revaluations = []
        total_fx_loss = Decimal("0")
        total_fx_gain = Decimal("0")

        for inv in invoices:
            if not inv.fx_rate or inv.currency == "VND":
                continue
            current_rate = inv.fx_gl_rate or inv.fx_rate
            rate_diff = current_rate - inv.fx_rate
            reval_amount = _vnd(inv.balance_due * rate_diff)

            if reval_amount > Decimal("0"):
                total_fx_loss += reval_amount
                revaluations.append({
                    "invoice_id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "currency": inv.currency,
                    "original_rate": inv.fx_rate,
                    "current_rate": current_rate,
                    "revaluation": reval_amount,
                    "type": "loss",
                })
            elif reval_amount < Decimal("0"):
                gain = abs(reval_amount)
                total_fx_gain += gain
                revaluations.append({
                    "invoice_id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "currency": inv.currency,
                    "original_rate": inv.fx_rate,
                    "current_rate": current_rate,
                    "revaluation": gain,
                    "type": "gain",
                })

        if total_fx_loss > Decimal("0"):
            self._post_to_gl("fx_revaluation", lines=[
                {"account_id": "635", "debit": total_fx_loss, "credit": Decimal("0"),
                 "description": f"FX loss revaluation {period}"},
                {"account_id": "331", "debit": Decimal("0"), "credit": total_fx_loss,
                 "description": f"FX loss revaluation {period}"},
            ])
        if total_fx_gain > Decimal("0"):
            self._post_to_gl("fx_revaluation_gain", lines=[
                {"account_id": "331", "debit": total_fx_gain, "credit": Decimal("0"),
                 "description": f"FX gain revaluation {period}"},
                {"account_id": "515", "debit": Decimal("0"), "credit": total_fx_gain,
                 "description": f"FX gain revaluation {period}"},
            ])

        return Result.success({
            "period": period,
            "revaluations": revaluations,
            "total_fx_loss": total_fx_loss,
            "total_fx_gain": total_fx_gain,
            "net_fx": _vnd(total_fx_loss - total_fx_gain),
        })

    # ── UC-AP-11: GL Auto-Post (internal helper) ──────────────────────
    # Implemented as _post_to_gl() above

    # ── UC-AP-13: Intercompany ────────────────────────────────────────

    def create_ic_invoice(
        self,
        amount: Decimal,
        invoice_date: date,
        description: str,
        from_entity_code: Optional[str] = None,
        to_entity_code: Optional[str] = None,
        from_entity: Optional[str] = None,
        to_entity: Optional[str] = None,
        invoice_number: Optional[str] = None,
        reference: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        from_entity_code = from_entity_code or from_entity
        to_entity_code = to_entity_code or to_entity
        if not from_entity_code or not to_entity_code:
            return Result.failure(ValidationError(ErrorCodes.MISSING_REQUIRED,
                                                  field="from_entity_code/to_entity_code"))
        if not description:
            return Result.failure(ValidationError(ErrorCodes.DESCRIPTION_EMPTY))
        if amount <= Decimal("0"):
            return Result.failure(ValidationError(ErrorCodes.PAYMENT_AMOUNT_ZERO))

        inv_number = invoice_number or f"IC-{from_entity_code}-{invoice_date.strftime('%Y%m%d')}-{to_entity_code}"

        ic_invoice = IntercompanyInvoice(
            from_entity_code=from_entity_code,
            to_entity_code=to_entity_code,
            invoice_number=inv_number,
            invoice_date=invoice_date,
            amount=amount,
            description=description,
            reference=reference,
            created_by=created_by,
        )
        result = self.repo.create_ic_invoice(ic_invoice)
        if result.is_success():
            self._post_to_gl("ic_invoice", lines=[
                {"account_id": "336", "debit": amount, "credit": Decimal("0"),
                 "description": f"IC {from_entity_code} to {to_entity_code}"},
                {"account_id": "511", "debit": Decimal("0"), "credit": amount,
                 "description": f"IC revenue {inv_number}"},
            ])
        return result

    # ── UC-AP-15: AP Reporting ────────────────────────────────────────

    def get_ap_balance(self, period: str) -> Dict[str, Any]:
        _closed = (APInvoiceStatusDB.PAID_FULL, APInvoiceStatusDB.CANCELLED,
                   APInvoiceStatusDB.WRITTEN_OFF)
        total_ap = self.session.execute(
            select(func.coalesce(func.sum(APInvoiceModel.balance_due), Decimal("0")))
            .where(APInvoiceModel.period == period)
            .where(APInvoiceModel.status.notin_(_closed))
        ).scalar_one()

        total_prepayments = self.session.execute(
            select(func.coalesce(func.sum(VendorPrepaymentModel.unapplied_balance), Decimal("0")))
            .where(VendorPrepaymentModel.status == PrepaymentStatus.PENDING)
        ).scalar_one()

        return {
            "period": period,
            "total_ap": total_ap,
            "total_prepayments": total_prepayments,
            "net_ap": _vnd(total_ap - total_prepayments),
        }

    def get_ap_turnover(self, period: str) -> Dict[str, Any]:
        _excluded = (APInvoiceStatusDB.CANCELLED, APInvoiceStatusDB.WRITTEN_OFF)
        total_purchases = self.session.execute(
            select(func.coalesce(func.sum(APInvoiceModel.amount), Decimal("0")))
            .where(APInvoiceModel.period == period)
            .where(APInvoiceModel.status.notin_(_excluded))
        ).scalar_one()

        _active = (APInvoiceStatusDB.PAID_FULL, APInvoiceStatusDB.CANCELLED,
                   APInvoiceStatusDB.WRITTEN_OFF)
        beginning_ap = self.session.execute(
            select(func.coalesce(func.sum(APInvoiceModel.balance_due), Decimal("0")))
            .where(APInvoiceModel.period == period)
            .where(APInvoiceModel.status.notin_(_active))
        ).scalar_one()

        ending_ap = beginning_ap
        avg_ap = _vnd((beginning_ap + ending_ap) / Decimal("2"))
        turnover = Decimal("0")
        if avg_ap > Decimal("0"):
            turnover = _vnd(total_purchases / avg_ap)

        return {
            "period": period,
            "total_purchases": total_purchases,
            "beginning_ap": beginning_ap,
            "ending_ap": ending_ap,
            "average_ap": avg_ap,
            "ap_turnover": turnover,
            "dpo": _vnd(Decimal("365") / turnover) if turnover > Decimal("0") else Decimal("0"),
        }

    def get_dpo(self, period: str) -> Dict[str, Any]:
        turnover_data = self.get_ap_turnover(period)
        dpo = turnover_data.get("dpo", Decimal("0"))
        return {
            "period": period,
            "dpo": dpo,
            "average_ap": turnover_data.get("average_ap", Decimal("0")),
            "total_purchases": turnover_data.get("total_purchases", Decimal("0")),
            "interpretation": (
                f"Average {dpo} days to pay suppliers"
            ),
        }
