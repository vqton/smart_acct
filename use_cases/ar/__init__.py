from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from domain import (
    Customer, CustomerType, CustomerGroup, CustomerStatus,
    ARInvoice, ARInvoiceType, ARInvoiceStatus, InvoiceLine, ARPayment, ARPaymentMethod,
    ARPaymentAllocation, ARAgingSnapshot, ARDunningLog, BadDebtProvision,
    BadDebtWriteOffRequest, WriteOffRequestStatus, CEIReport,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.ar_repository import ARRepository
from infrastructure.models.ar_models import (
    ARInvoiceModel, ARPaymentModel,
    InvoiceStatusDB as _InvoiceStatusDB,
)
from services.gdt_client import GDTClient
from services.signing_service import SigningService
from domain.tax import EInvoice


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


def _provision_pct(days_past_due: int) -> Decimal:
    if days_past_due <= 180:
        return Decimal("0")
    elif days_past_due <= 365:
        return Decimal("0.20")
    else:
        return Decimal("0.50")


class ARUseCases:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ARRepository(session)
        self.gdt_client = GDTClient()
        self.signing_service = SigningService()

    # ── UC-AR-01: Customer CRUD ────────────────────────────────────
    def create_customer(
        self,
        customer_code: str,
        customer_name: str,
        customer_type: CustomerType = CustomerType.ENTERPRISE,
        customer_group: CustomerGroup = CustomerGroup.DOMESTIC,
        tax_code: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        contact_person: Optional[str] = None,
        credit_limit: Decimal = Decimal("0"),
        credit_limit_override: bool = False,
        credit_limit_override_expires: Optional[date] = None,
        coa_account_code: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        customer = Customer(
            customer_code=customer_code,
            customer_name=customer_name,
            customer_type=customer_type,
            customer_group=customer_group,
            tax_code=tax_code,
            email=email,
            phone=phone,
            address=address,
            city=city,
            contact_person=contact_person,
            credit_limit=credit_limit,
            credit_limit_override=credit_limit_override,
            credit_limit_override_expires=credit_limit_override_expires,
            coa_account_code=coa_account_code,
            notes=notes,
        )
        return self.repo.create_customer(customer)

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.repo.get_customer(customer_id)

    def get_customer_by_code(self, code: str) -> Optional[Customer]:
        return self.repo.get_customer_by_code(code)

    def list_customers(
        self,
        customer_type: Optional[CustomerType] = None,
        customer_group: Optional[CustomerGroup] = None,
        status: Optional[CustomerStatus] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Customer]:
        return self.repo.list_customers(
            customer_type=customer_type, customer_group=customer_group,
            status=status, search=search, limit=limit, offset=offset,
        )

    def update_customer(self, customer_id: int, **updates) -> Optional[Customer]:
        return self.repo.update_customer(customer_id, **updates)

    def suspend_customer(self, customer_id: int) -> Result:
        customer = self.repo.update_customer(customer_id, status=CustomerStatus.SUSPENDED)
        if not customer:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Customer", id=str(customer_id)))
        return Result.success(customer)

    def delete_customer(self, customer_id: int) -> Result:
        """Delete customer if no open invoices."""
        outstanding = self.repo.get_customer_outstanding(customer_id)
        if outstanding > Decimal("0"):
            return Result.failure(ValidationError(ErrorCodes.CUSTOMER_HAS_OPEN_AR,
                                                  id=str(customer_id)))
        ok = self.repo.delete_customer(customer_id)
        if not ok:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Customer", id=str(customer_id)))
        return Result.success(None)

    # ── UC-AR-02: Create AR Invoice ─────────────────────────────────
    def create_invoice(
        self,
        invoice_number: str,
        customer_id: int,
        customer_code: str,
        customer_name: str,
        issue_date: date,
        due_date: date,
        amount: Decimal,
        lines: List[InvoiceLine],
        invoice_type: ARInvoiceType = ARInvoiceType.SALES,
        discount_amount: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        total_amount: Optional[Decimal] = None,
        payment_terms_days: int = 30,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        period: Optional[str] = None,
        coa_code: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        if total_amount is None:
            total_amount = _vnd(amount - discount_amount + tax_amount)

        # UC-AR-08: Credit limit check
        credit_check = self.repo.check_credit_limit(customer_id, total_amount)
        if not credit_check["approved"]:
            return Result.failure(ValidationError(ErrorCodes.CREDIT_LIMIT_EXCEEDED,
                                                  detail=credit_check.get("error", "")))

        invoice = ARInvoice(
            invoice_number=invoice_number,
            customer_id=customer_id,
            customer_code=customer_code,
            customer_name=customer_name,
            invoice_type=invoice_type,
            status=ARInvoiceStatus.DRAFT,
            issue_date=issue_date,
            due_date=due_date,
            amount=amount,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            balance_due=total_amount,
            payment_terms_days=payment_terms_days,
            reference=reference,
            notes=notes,
            period=period,
            coa_code=coa_code,
            lines=lines,
        )
        result = self.repo.create_invoice(invoice)
        if result.is_success():
            if credit_check.get("warning"):
                result.add_warning(credit_check["warning"])
        return result

    def get_invoice(self, invoice_id: int) -> Optional[ARInvoice]:
        return self.repo.get_invoice(invoice_id)

    def get_invoice_by_number(self, number: str) -> Optional[ARInvoice]:
        return self.repo.get_invoice_by_number(number)

    def list_invoices(
        self,
        customer_id: Optional[int] = None,
        customer_code: Optional[str] = None,
        status: Optional[ARInvoiceStatus] = None,
        period: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ARInvoice]:
        return self.repo.list_invoices(
            customer_id=customer_id, customer_code=customer_code,
            status=status, period=period, limit=limit, offset=offset,
        )

    def issue_invoice(self, invoice_id: int, issued_by: Optional[str] = None) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.status != ARInvoiceStatus.DRAFT:
            return Result.failure(ValidationError(ErrorCodes.INVOICE_ALREADY_PAID,
                                                  id=str(invoice_id)))
        updated = self.repo.update_invoice_status(invoice_id, ARInvoiceStatus.ISSUED)
        if updated is None:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        # UC-AR-09: Auto-post GL entries (simplified: update coa)
        self.repo.update_invoice(invoice_id, posted_by=issued_by or "system",
                                 posted_at=datetime.now(timezone.utc))
        return Result.success(updated)

    def cancel_invoice(self, invoice_id: int, reason: Optional[str] = None) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.status in (ARInvoiceStatus.PAID, ARInvoiceStatus.WRITTEN_OFF):
            return Result.failure(ValidationError(ErrorCodes.INVOICE_ALREADY_PAID,
                                                  id=str(invoice_id)))
        updated = self.repo.update_invoice_status(invoice_id, ARInvoiceStatus.CANCELLED)
        if updated is None:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        return Result.success(updated)

    # ── UC-AR-06: Payment Allocation (FIFO) ─────────────────────────
    def record_payment(
        self,
        invoice_id: int,
        payment_number: str,
        amount: Decimal,
        payment_date: date,
        payment_method: ARPaymentMethod = ARPaymentMethod.CASH,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        received_by: Optional[str] = None,
        bank_account_id: Optional[int] = None,
        coa_code: Optional[str] = None,
        auto_allocate: bool = True,
    ) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if amount <= Decimal("0"):
            return Result.failure(ValidationError(ErrorCodes.PAYMENT_AMOUNT_ZERO))
        if auto_allocate:
            total_outstanding = self.repo.get_customer_outstanding(invoice.customer_id)
            if amount > (total_outstanding + Decimal("0.01")):
                return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                      amount=str(amount),
                                                      balance=str(total_outstanding)))
        elif amount > (invoice.balance_due + Decimal("0.01")):
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  amount=str(amount),
                                                  balance=str(invoice.balance_due)))

        payment = ARPayment(
            payment_number=payment_number,
            customer_id=invoice.customer_id,
            invoice_id=invoice_id,
            payment_date=payment_date,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            received_by=received_by,
            bank_account_id=bank_account_id,
            coa_code=coa_code,
        )
        result = self.repo.create_payment(payment)
        if not result.is_success():
            return result

        payment_domain = result.get_data()

        if auto_allocate:
            alloc_result = self.repo.allocate_payment_fifo(payment_domain.id, invoice.customer_id)
            if alloc_result.is_success():
                pass  # allocation succeeded, continue
        
        return Result.success(payment_domain)

    def get_payments_for_invoice(self, invoice_id: int) -> List[ARPayment]:
        return self.repo.get_payments_for_invoice(invoice_id)

    def list_payments(
        self,
        customer_code: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ARPayment]:
        return self.repo.list_payments(
            customer_code=customer_code,
            date_from=date_from, date_to=date_to,
            limit=limit, offset=offset,
        )

    # ── UC-AR-03: AR Aging Report (Live) ────────────────────────────
    def get_aging_report(
        self,
        customer_id: Optional[int] = None,
        as_of_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        as_of = as_of_date or date.today()

        stmt = (
            select(
                ARInvoiceModel.customer_id,
                ARInvoiceModel.customer_code,
                ARInvoiceModel.customer_name,
                ARInvoiceModel.due_date,
                ARInvoiceModel.balance_due,
            )
            .where(ARInvoiceModel.balance_due > 0)
            .where(ARInvoiceModel.status.notin_([
                _InvoiceStatusDB.CANCELLED, _InvoiceStatusDB.WRITTEN_OFF,
            ]))
        )
        if customer_id is not None:
            stmt = stmt.where(ARInvoiceModel.customer_id == customer_id)

        invoices = self.session.execute(stmt).all()

        customer_data = {}
        for inv in invoices:
            cid = inv.customer_id
            if cid not in customer_data:
                customer_data[cid] = {
                    "customer_id": cid,
                    "customer_code": inv.customer_code,
                    "customer_name": inv.customer_name,
                    "buckets": {
                        "current": Decimal("0"),
                        "bucket_1_30": Decimal("0"),
                        "bucket_31_60": Decimal("0"),
                        "bucket_61_90": Decimal("0"),
                        "bucket_91_180": Decimal("0"),
                        "bucket_181_365": Decimal("0"),
                        "bucket_365_plus": Decimal("0"),
                    }
                }

            days_past_due = (as_of - inv.due_date).days if inv.due_date <= as_of else 0
            bucket = _calc_aging_bucket(days_past_due)
            customer_data[cid]["buckets"][bucket] += inv.balance_due

        result = []
        for data in customer_data.values():
            total_outstanding = sum(data["buckets"].values())
            max_days = 0
            for inv in invoices:
                if inv.customer_id == data["customer_id"] and inv.balance_due > 0:
                    if inv.due_date <= as_of:
                        d = (as_of - inv.due_date).days
                        if d > max_days:
                            max_days = d
            result.append(data | {
                "total_outstanding": total_outstanding,
                "days_past_due_oldest": max_days,
            })

        return result

    # ── UC-AR-04: Aging Snapshot (Period-Locked) ────────────────────
    def create_aging_snapshot(self, period: str) -> Result:
        as_of = date.today()
        live_aging = self.get_aging_report(as_of_date=as_of)
        created = []
        for entry in live_aging:
            snapshot = ARAgingSnapshot(
                period=period,
                customer_id=entry["customer_id"],
                customer_code=entry["customer_code"],
                customer_name=entry["customer_name"],
                current_amount=entry.get("current", Decimal("0")),
                bucket_1_30=entry.get("bucket_1_30", Decimal("0")),
                bucket_31_60=entry.get("bucket_31_60", Decimal("0")),
                bucket_61_90=entry.get("bucket_61_90", Decimal("0")),
                bucket_91_180=entry.get("bucket_91_180", Decimal("0")),
                bucket_181_365=entry.get("bucket_181_365", Decimal("0")),
                bucket_365_plus=entry.get("bucket_365_plus", Decimal("0")),
                total_outstanding=entry["total_outstanding"],
            )
            r = self.repo.create_aging_snapshot(snapshot)
            if r.is_success():
                created.append(snapshot)
        return Result.success({"period": period, "snapshots": len(created)})

    def get_aging_snapshots(self, period: str) -> List[ARAgingSnapshot]:
        return self.repo.get_aging_snapshots(period)

    # ── UC-AR-05: Dunning Workflow ──────────────────────────────────
    def advance_dunning(self, as_of_date: Optional[date] = None) -> Result:
        as_of = as_of_date or date.today()
        invoices = self.repo.get_overdue_invoices_for_dunning(as_of)
        processed = []
        for inv in invoices:
            days_past_due = (as_of - inv.due_date).days
            if days_past_due <= 0:
                continue

            # Calculate new dunning level
            if days_past_due <= 7:
                new_level = 1
            elif days_past_due <= 30:
                new_level = 2
            elif days_past_due <= 60:
                new_level = 3
            elif days_past_due <= 90:
                new_level = 4
            else:
                new_level = 5

            if new_level > inv.dunning_level:
                log = ARDunningLog(
                    ar_invoice_id=inv.id,
                    dunning_level=new_level,
                    dunning_date=as_of,
                    dunning_method="email",
                    performed_by="system",
                )
                self.repo.log_dunning(log)

                # Compute cooldown period
                cooldown = {1: 7, 2: 7, 3: 3, 4: 3, 5: 1}.get(new_level, 7)
                from datetime import timedelta
                next_dunning = as_of + timedelta(days=cooldown)

                self.repo.update_invoice(inv.id, dunning_level=new_level,
                                         next_dunning_date=next_dunning)
                processed.append({
                    "invoice_id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "dunning_level": new_level,
                    "days_past_due": days_past_due,
                })
        return Result.success({"processed": processed, "count": len(processed)})

    def manual_dunning(self, invoice_id: int, dunning_method: str = "email",
                       notes: Optional[str] = None, performed_by: Optional[str] = None) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.dunning_level >= 5:
            return Result.failure(ValidationError(ErrorCodes.DUNNING_MAX_LEVEL_REACHED,
                                                  id=str(invoice_id)))

        new_level = invoice.dunning_level + 1
        log = ARDunningLog(
            ar_invoice_id=invoice_id,
            dunning_level=new_level,
            dunning_date=date.today(),
            dunning_method=dunning_method,
            notes=notes,
            performed_by=performed_by,
        )
        self.repo.log_dunning(log)
        self.repo.update_invoice(invoice_id, dunning_level=new_level)
        return Result.success({"invoice_id": invoice_id, "dunning_level": new_level})

    def get_dunning_logs(self, invoice_id: int) -> List[ARDunningLog]:
        return self.repo.get_dunning_logs(invoice_id)

    # ── UC-AR-07: Bad Debt Provision ────────────────────────────────
    def create_bad_debt_provision(self, period: str) -> Result:
        invoices = self.repo.get_overdue_invoices_for_provision(period)
        provisions = []
        for inv in invoices:
            days_past_due = (date.today() - inv.due_date).days
            if days_past_due < 180:
                continue
            pct = _provision_pct(days_past_due)
            if pct == Decimal("0"):
                continue
            provision = BadDebtProvision(
                customer_id=inv.customer_id,
                ar_invoice_id=inv.id,
                period=period,
                provision_percent=pct,
                invoice_amount=inv.balance_due,
                provision_amount=_vnd(inv.balance_due * pct),
            )
            r = self.repo.create_provision(provision)
            if r.is_success():
                provisions.append(provision)
        return Result.success({"period": period, "provisions": len(provisions),
                               "total_amount": sum(p.provision_amount for p in provisions)})

    def get_provisions(self, period: str) -> List[BadDebtProvision]:
        return self.repo.get_provisions_for_period(period)

    # ── UC-AR-08: Credit Limit Check ────────────────────────────────
    def check_credit_limit(self, customer_id: int, amount: Decimal) -> Dict[str, Any]:
        return self.repo.check_credit_limit(customer_id, amount)

    # ── UC-AR-10: E-Invoice Auto-Submission ─────────────────────────
    def submit_einvoice(self, invoice_id: int) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.status != ARInvoiceStatus.ISSUED:
            return Result.failure(ValidationError(ErrorCodes.INVOICE_ALREADY_PAID,
                                                  id=str(invoice_id)))

        customer = self.repo.get_customer(invoice.customer_id)
        if not customer:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Customer", id=str(invoice.customer_id)))

        einvoice = EInvoice(
            invoice_number=invoice.invoice_number,
            invoice_series=f"AR/{invoice.issue_date.year}",
            invoice_date=invoice.issue_date,
            seller_tax_code=customer.tax_code or "0000000000",
            seller_name=customer.customer_name,
            seller_address=customer.address,
            buyer_tax_code=customer.tax_code,
            buyer_name=customer.customer_name,
            buyer_address=customer.address,
            subtotal=invoice.amount,
            discount_amount=invoice.discount_amount,
            vat_rate=Decimal("0.1"),
            vat_amount=invoice.tax_amount,
            grand_total=invoice.total_amount,
            currency="VND",
            lines=[
                {"line_number": l.line_number, "description": l.description,
                 "quantity": str(l.quantity), "unit_price": str(l.unit_price),
                 "amount": str(l.line_amount)}
                for l in invoice.lines
            ],
        )

        sign_result = self.signing_service.sign_invoice(einvoice)
        if not sign_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.GDT_SUBMISSION_FAILED,
                                                  detail="Signing failed"))

        gdt_result = self.gdt_client.submit_invoice(einvoice)
        if not gdt_result.is_success():
            return Result.failure(ValidationError(ErrorCodes.GDT_SUBMISSION_FAILED,
                                                  detail="GDT submission failed"))

        gdt_data = gdt_result.get_data()
        self.repo.update_invoice(invoice_id, einvoice_id=1,
                                 reference=gdt_data.get("transaction_id"))
        return Result.success(gdt_data)

    # ── UC-AR-11: Write-Off Approval Workflow ───────────────────────
    def create_write_off_request(self, invoice_id: int, reason: str,
                                 created_by: Optional[str] = None,
                                 supporting_docs: Optional[str] = None) -> Result:
        invoice = self.repo.get_invoice(invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        if invoice.status == ARInvoiceStatus.PAID:
            return Result.failure(ValidationError(ErrorCodes.INVOICE_ALREADY_PAID,
                                                  id=str(invoice_id)))

        req = BadDebtWriteOffRequest(
            ar_invoice_id=invoice_id,
            customer_id=invoice.customer_id,
            reason=reason,
            supporting_docs=supporting_docs,
            created_by=created_by,
        )
        return self.repo.create_write_off_request(req)

    def get_write_off_requests(self, status: Optional[str] = None) -> List[BadDebtWriteOffRequest]:
        return self.repo.list_write_off_requests(status)

    def approve_write_off(self, request_id: int, approval_by: str,
                          approval_notes: Optional[str] = None) -> Result:
        return self.repo.approve_write_off(request_id, approval_by, approval_notes)

    def reject_write_off(self, request_id: int, approval_by: str,
                         reason: Optional[str] = None) -> Result:
        return self.repo.reject_write_off(request_id, approval_by, reason)

    # ── UC-AR-12: CEI + DSO Reporting ───────────────────────────────
    def get_cei_report(self, periods: List[str]) -> List[Dict[str, Any]]:
        reports = []
        for i, period in enumerate(periods):
            invoices_stmt = select(
                func.coalesce(func.sum(ARInvoiceModel.total_amount), Decimal("0"))
            ).where(ARInvoiceModel.period == period)

            total_sales = self.session.execute(invoices_stmt).scalar_one()

            ending_ar = self.session.execute(
                select(func.coalesce(func.sum(ARInvoiceModel.balance_due), Decimal("0")))
                .where(ARInvoiceModel.period == period)
                .where(ARInvoiceModel.status.notin_([
                    _InvoiceStatusDB.CANCELLED, _InvoiceStatusDB.WRITTEN_OFF
                ]))
            ).scalar_one()

            beginning_ar = Decimal("0")
            if i > 0:
                prev_period = periods[i - 1]
                beginning_ar = self.session.execute(
                    select(func.coalesce(func.sum(ARInvoiceModel.balance_due), Decimal("0")))
                    .where(ARInvoiceModel.period == prev_period)
                    .where(ARInvoiceModel.status.notin_([
                        _InvoiceStatusDB.CANCELLED, _InvoiceStatusDB.WRITTEN_OFF
                    ]))
                ).scalar_one()

            bad_debt = Decimal("0")

            numerator = beginning_ar + total_sales - ending_ar - bad_debt
            denominator = beginning_ar + total_sales
            cei = Decimal("100") if denominator == Decimal("0") else _vnd((numerator / denominator) * Decimal("100"))

            avg_ar = (beginning_ar + ending_ar) / Decimal("2")
            dso = Decimal("0") if total_sales == Decimal("0") else _vnd((avg_ar / total_sales) * Decimal("30"))

            reports.append({
                "period": period,
                "beginning_ar": beginning_ar,
                "credit_sales": total_sales,
                "ending_ar": ending_ar,
                "bad_debt": bad_debt,
                "cei": cei,
                "dso": dso,
            })
        return reports

    # ── UC-AR-13: IFRS 9 ECL (simplified) ───────────────────────────
    def calculate_ecl(self, customer_id: int, reporting_date: Optional[date] = None) -> Dict[str, Any]:
        as_of = reporting_date or date.today()
        aging = self.get_aging_report(customer_id=customer_id, as_of_date=as_of)
        if not aging:
            return {"customer_id": customer_id, "stage": "stage_1", "ecl": Decimal("0")}

        entry = aging[0]
        buckets = entry.get("buckets", {})
        total_current = buckets.get("current", Decimal("0"))
        total_1_30 = buckets.get("bucket_1_30", Decimal("0"))
        total_31_60 = buckets.get("bucket_31_60", Decimal("0"))
        total_61_90 = buckets.get("bucket_61_90", Decimal("0"))
        total_91_180 = buckets.get("bucket_91_180", Decimal("0"))
        total_181_365 = buckets.get("bucket_181_365", Decimal("0"))
        total_365 = buckets.get("bucket_365_plus", Decimal("0"))

        lgd = Decimal("0.5")
        ecl = (
            total_current * Decimal("0.01") * lgd
            + total_1_30 * Decimal("0.02") * lgd
            + total_31_60 * Decimal("0.05") * lgd
            + total_61_90 * Decimal("0.10") * lgd
            + total_91_180 * Decimal("0.20") * lgd
            + total_181_365 * Decimal("0.50") * lgd
            + total_365 * Decimal("0.80") * lgd
        )

        if total_91_180 > Decimal("0") or total_181_365 > Decimal("0"):
            stage = "stage_2"
        elif total_365 > Decimal("0"):
            stage = "stage_3"
        else:
            stage = "stage_1"

        return {
            "customer_id": customer_id,
            "stage": stage,
            "ecl": _vnd(ecl),
            "reporting_date": as_of.isoformat(),
        }

    # ── AR Balance Sheet (stub, legacy) ──────────────────────────────
    def get_ar_balance_sheet(self, period: str) -> Dict[str, Any]:
        total = self.session.execute(
            select(func.coalesce(func.sum(ARInvoiceModel.balance_due), Decimal("0")))
            .where(ARInvoiceModel.period == period)
            .where(ARInvoiceModel.status.notin_([
                _InvoiceStatusDB.CANCELLED, _InvoiceStatusDB.WRITTEN_OFF,
            ]))
        ).scalar_one()
        return {"period": period, "receivables": total, "provision": Decimal("0")}
