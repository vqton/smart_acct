from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_, desc

from domain import (
    Customer, CustomerType, CustomerGroup, CustomerStatus,
    ARInvoice, InvoiceLine, ARPayment, ARPaymentAllocation,
    ARInvoiceType, ARInvoiceStatus, ARPaymentMethod, ARAllocationStatus,
    ARAgingSnapshot, ARDunningLog, BadDebtProvision, BadDebtWriteOffRequest,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.models.ar_models import (
    CustomerModel, ARInvoiceModel, ARInvoiceLineModel, ARPaymentModel,
    ARPaymentAllocationModel, ARAgingSnapshotModel, ARDunningLogModel,
    BadDebtProvisionModel, BadDebtWriteOffRequestModel,
    CustomerTypeDB, CustomerGroupDB, CustomerStatusDB,
    InvoiceTypeDB, InvoiceStatusDB, PaymentMethodDB,
    WriteOffRequestStatusDB,
)


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class ARRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── helpers ─────────────────────────────────────────────────────
    @staticmethod
    def _dt_to_domain_type(model, enum_cls, attr: str):
        val = getattr(model, attr)
        return enum_cls(val.value) if val else None

    # ── Customer mappings ───────────────────────────────────────────
    def _customer_to_domain(self, m: CustomerModel) -> Customer:
        c = Customer(
            customer_code=m.customer_code,
            customer_name=m.customer_name,
            legal_name=m.legal_name,
            tax_code=m.tax_code,
            customer_type=CustomerType(m.customer_type.value),
            customer_group=CustomerGroup(m.customer_group.value),
            status=CustomerStatus(m.status.value),
            email=m.email,
            phone=m.phone,
            address=m.address,
            city=m.city,
            country=m.country,
            contact_person=m.contact_person,
            credit_limit=m.credit_limit,
            credit_limit_override=m.credit_limit_override,
            credit_limit_override_expires=m.credit_limit_override_expires,
            credit_rating=m.credit_rating,
            outstanding_balance=m.outstanding_balance,
            coa_account_code=m.coa_account_code,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        c.id = m.id
        return c

    def _customer_to_model(self, d: Customer) -> CustomerModel:
        return CustomerModel(
            customer_code=d.customer_code,
            customer_name=d.customer_name,
            legal_name=d.legal_name,
            tax_code=d.tax_code,
            customer_type=CustomerTypeDB(d.customer_type.value),
            customer_group=CustomerGroupDB(d.customer_group.value),
            status=CustomerStatusDB(d.status.value),
            email=d.email,
            phone=d.phone,
            address=d.address,
            city=d.city,
            country=d.country,
            contact_person=d.contact_person,
            credit_limit=d.credit_limit,
            credit_limit_override=d.credit_limit_override,
            credit_limit_override_expires=d.credit_limit_override_expires,
            credit_rating=d.credit_rating,
            outstanding_balance=d.outstanding_balance,
            coa_account_code=d.coa_account_code,
            notes=d.notes,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )

    # ── Customer CRUD ───────────────────────────────────────────────
    def create_customer(self, customer: Customer) -> Result:
        existing = self.session.execute(
            select(CustomerModel).where(CustomerModel.customer_code == customer.customer_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="Customer", id=customer.customer_code))
        model = self._customer_to_model(customer)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._customer_to_domain(model))

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        m = self.session.get(CustomerModel, customer_id)
        return self._customer_to_domain(m) if m else None

    def get_customer_by_code(self, code: str) -> Optional[Customer]:
        m = self.session.execute(
            select(CustomerModel).where(CustomerModel.customer_code == code)
        ).scalar_one_or_none()
        return self._customer_to_domain(m) if m else None

    def list_customers(
        self,
        customer_type: Optional[CustomerType] = None,
        customer_group: Optional[CustomerGroup] = None,
        status: Optional[CustomerStatus] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Customer]:
        stmt = select(CustomerModel)
        if customer_type:
            stmt = stmt.where(CustomerModel.customer_type == CustomerTypeDB(customer_type.value))
        if customer_group:
            stmt = stmt.where(CustomerModel.customer_group == CustomerGroupDB(customer_group.value))
        if status:
            stmt = stmt.where(CustomerModel.status == CustomerStatusDB(status.value))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(CustomerModel.customer_code.ilike(pattern),
                    CustomerModel.customer_name.ilike(pattern))
            )
        stmt = stmt.order_by(CustomerModel.customer_code).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._customer_to_domain(m) for m in models]

    def update_customer(self, customer_id: int, **updates) -> Optional[Customer]:
        model = self.session.get(CustomerModel, customer_id)
        if not model:
            return None
        allowed = ("customer_name", "legal_name", "tax_code", "email", "phone", "address", "city",
                   "contact_person", "credit_limit", "outstanding_balance",
                   "coa_account_code", "notes", "status", "customer_type", "customer_group",
                   "credit_limit_override", "credit_limit_override_expires", "credit_rating")
        for k, v in updates.items():
            if k in allowed:
                if k == "status" and isinstance(v, CustomerStatus):
                    setattr(model, k, CustomerStatusDB(v.value))
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._customer_to_domain(model)

    def delete_customer(self, customer_id: int) -> bool:
        model = self.session.get(CustomerModel, customer_id)
        if not model:
            return False
        self.session.delete(model)
        return True

    # ── Invoice mappings ────────────────────────────────────────────
    def _line_to_domain(self, m: ARInvoiceLineModel) -> InvoiceLine:
        return InvoiceLine(
            id=m.id,
            line_number=m.line_number,
            description=m.description,
            quantity=m.quantity,
            unit_price=m.unit_price,
            line_amount=m.line_amount,
            tax_rate=m.tax_rate,
            tax_amount=m.tax_amount,
            coa_code=m.coa_code,
        )

    def _line_to_model(self, d: InvoiceLine, invoice_id: int) -> ARInvoiceLineModel:
        return ARInvoiceLineModel(
            invoice_id=invoice_id,
            line_number=d.line_number,
            description=d.description,
            quantity=d.quantity,
            unit_price=d.unit_price,
            line_amount=d.line_amount,
            tax_rate=d.tax_rate,
            tax_amount=d.tax_amount,
            coa_code=d.coa_code,
        )

    def _invoice_to_domain(self, m: ARInvoiceModel) -> ARInvoice:
        inv = ARInvoice(
            invoice_number=m.invoice_number,
            customer_id=m.customer_id,
            customer_code=m.customer_code,
            customer_name=m.customer_name,
            invoice_type=ARInvoiceType(m.invoice_type.value),
            status=ARInvoiceStatus(m.status.value),
            issue_date=m.issue_date,
            due_date=m.due_date,
            amount=m.amount,
            discount_amount=m.discount_amount,
            tax_amount=m.tax_amount,
            total_amount=m.total_amount,
            paid_amount=m.paid_amount,
            written_off_amount=m.written_off_amount,
            balance_due=m.balance_due,
            payment_terms_days=m.payment_terms_days,
            dunning_level=m.dunning_level,
            next_dunning_date=m.next_dunning_date,
            reference=m.reference,
            notes=m.notes,
            period=m.period,
            posted_at=m.posted_at,
            posted_by=m.posted_by,
            coa_code=m.coa_code,
            einvoice_id=m.einvoice_id,
            lines=[self._line_to_domain(l) for l in m.lines],
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        inv.id = m.id
        return inv

    def _invoice_to_model(self, d: ARInvoice) -> ARInvoiceModel:
        return ARInvoiceModel(
            invoice_number=d.invoice_number,
            customer_id=d.customer_id,
            customer_code=d.customer_code,
            customer_name=d.customer_name,
            invoice_type=InvoiceTypeDB(d.invoice_type.value),
            status=InvoiceStatusDB(d.status.value),
            issue_date=d.issue_date,
            due_date=d.due_date,
            amount=d.amount,
            discount_amount=d.discount_amount,
            tax_amount=d.tax_amount,
            total_amount=d.total_amount,
            paid_amount=d.paid_amount,
            written_off_amount=d.written_off_amount,
            balance_due=d.balance_due,
            payment_terms_days=d.payment_terms_days,
            dunning_level=d.dunning_level,
            next_dunning_date=d.next_dunning_date,
            reference=d.reference,
            notes=d.notes,
            period=d.period,
            posted_at=d.posted_at,
            posted_by=d.posted_by,
            coa_code=d.coa_code,
            einvoice_id=d.einvoice_id,
        )

    # ── Invoice CRUD ────────────────────────────────────────────────
    def create_invoice(self, invoice: ARInvoice) -> Result:
        existing = self.session.execute(
            select(ARInvoiceModel).where(ARInvoiceModel.invoice_number == invoice.invoice_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="Invoice", id=invoice.invoice_number))
        model = self._invoice_to_model(invoice)
        self.session.add(model)
        self.session.flush()
        for line in invoice.lines:
            lm = self._line_to_model(line, model.id)
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._invoice_to_domain(model))

    def get_invoice(self, invoice_id: int) -> Optional[ARInvoice]:
        m = self.session.get(ARInvoiceModel, invoice_id)
        return self._invoice_to_domain(m) if m else None

    def get_invoice_by_number(self, number: str) -> Optional[ARInvoice]:
        m = self.session.execute(
            select(ARInvoiceModel).where(ARInvoiceModel.invoice_number == number)
        ).scalar_one_or_none()
        return self._invoice_to_domain(m) if m else None

    def list_invoices(
        self,
        customer_id: Optional[int] = None,
        customer_code: Optional[str] = None,
        status: Optional[ARInvoiceStatus] = None,
        period: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ARInvoice]:
        stmt = select(ARInvoiceModel)
        if customer_id is not None:
            stmt = stmt.where(ARInvoiceModel.customer_id == customer_id)
        if customer_code:
            stmt = stmt.where(ARInvoiceModel.customer_code == customer_code)
        if status:
            stmt = stmt.where(ARInvoiceModel.status == InvoiceStatusDB(status.value))
        if period:
            stmt = stmt.where(ARInvoiceModel.period == period)
        stmt = stmt.order_by(desc(ARInvoiceModel.issue_date)).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._invoice_to_domain(m) for m in models]

    def update_invoice(self, invoice_id: int, **updates) -> Optional[ARInvoice]:
        model = self.session.get(ARInvoiceModel, invoice_id)
        if not model:
            return None
        allowed = ("amount", "discount_amount", "tax_amount", "total_amount",
                   "paid_amount", "written_off_amount", "balance_due",
                   "status", "reference", "notes", "period", "posted_at",
                   "posted_by", "coa_code", "einvoice_id", "dunning_level",
                   "next_dunning_date")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._invoice_to_domain(model)

    def update_invoice_status(self, invoice_id: int, new_status: ARInvoiceStatus) -> Optional[ARInvoice]:
        return self.update_invoice(invoice_id, status=new_status)

    def add_payment_to_invoice(self, invoice_id: int, payment_amount: Decimal) -> Optional[ARInvoice]:
        model = self.session.get(ARInvoiceModel, invoice_id)
        if not model:
            return None
        model.paid_amount = _vnd(model.paid_amount + payment_amount)
        model.balance_due = _vnd(model.balance_due - payment_amount)
        if model.balance_due <= Decimal("0"):
            model.status = InvoiceStatusDB.PAID
        elif model.paid_amount > Decimal("0"):
            model.status = InvoiceStatusDB.PARTIALLY_PAID
        self.session.flush()
        return self._invoice_to_domain(model)

    def get_customer_outstanding(self, customer_id: int) -> Decimal:
        result = self.session.execute(
            select(func.coalesce(func.sum(ARInvoiceModel.balance_due), Decimal("0")))
            .where(ARInvoiceModel.customer_id == customer_id)
            .where(ARInvoiceModel.status.notin_([
                InvoiceStatusDB.CANCELLED, InvoiceStatusDB.WRITTEN_OFF
            ]))
        ).scalar_one()
        return _vnd(result)

    def get_invoices_with_balance(
        self, customer_id: int, as_of: Optional[date] = None
    ) -> List[ARInvoiceModel]:
        stmt = select(ARInvoiceModel).where(
            ARInvoiceModel.customer_id == customer_id,
            ARInvoiceModel.balance_due > 0,
            ARInvoiceModel.status.notin_([
                InvoiceStatusDB.CANCELLED, InvoiceStatusDB.WRITTEN_OFF
            ])
        ).order_by(ARInvoiceModel.due_date)
        return self.session.execute(stmt).scalars().all()

    def check_credit_limit(self, customer_id: int, new_invoice_total: Decimal) -> Dict[str, Any]:
        customer = self.session.get(CustomerModel, customer_id)
        if not customer:
            return {"approved": False, "error": "Customer not found"}
        outstanding = self.get_customer_outstanding(customer_id)
        total_exposure = outstanding + new_invoice_total
        result = {
            "approved": True,
            "customer_code": customer.customer_code,
            "customer_name": customer.customer_name,
            "credit_limit": customer.credit_limit,
            "current_outstanding": outstanding,
            "new_invoice_total": new_invoice_total,
            "total_exposure": total_exposure,
            "utilization_pct": Decimal("0"),
            "warning": None,
        }
        if customer.credit_limit > 0:
            utilization = (total_exposure / customer.credit_limit) * Decimal("100")
            result["utilization_pct"] = utilization
            if total_exposure > customer.credit_limit:
                if customer.credit_limit_override and customer.credit_limit_override_expires:
                    if customer.credit_limit_override_expires >= date.today():
                        result["warning"] = f"Credit limit exceeded but override active until {customer.credit_limit_override_expires}"
                    else:
                        result["approved"] = False
                        result["error"] = "Credit limit override expired"
                else:
                    result["approved"] = False
                    result["error"] = f"Credit limit exceeded: {total_exposure} > {customer.credit_limit}"
            elif utilization >= Decimal("80"):
                result["warning"] = f"Credit utilization at {utilization:.1f}%"
        return result

    # ── Payment CRUD ────────────────────────────────────────────────
    def _payment_to_domain(self, m: ARPaymentModel) -> ARPayment:
        p = ARPayment(
            payment_number=m.payment_number,
            customer_id=m.customer_id,
            invoice_id=m.invoice_id,
            payment_date=m.payment_date,
            amount=m.amount,
            payment_method=ARPaymentMethod(m.payment_method.value),
            reference=m.reference,
            notes=m.notes,
            received_by=m.received_by,
            bank_account_id=m.bank_account_id,
            coa_code=m.coa_code,
            amount_applied=m.amount_applied,
            amount_unapplied=m.amount_unapplied,
            created_at=m.created_at,
        )
        p.id = m.id
        return p

    def _payment_to_model(self, d: ARPayment) -> ARPaymentModel:
        return ARPaymentModel(
            payment_number=d.payment_number,
            customer_id=d.customer_id,
            invoice_id=d.invoice_id,
            payment_date=d.payment_date,
            amount=d.amount,
            payment_method=PaymentMethodDB(d.payment_method.value),
            reference=d.reference,
            notes=d.notes,
            received_by=d.received_by,
            bank_account_id=d.bank_account_id,
            coa_code=d.coa_code,
            amount_applied=d.amount_applied,
            amount_unapplied=d.amount_unapplied,
        )

    def create_payment(self, payment: ARPayment) -> Result:
        existing = self.session.execute(
            select(ARPaymentModel).where(ARPaymentModel.payment_number == payment.payment_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="Payment", id=payment.payment_number))

        model = self._payment_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._payment_to_domain(model))

    def allocate_payment_fifo(self, payment_id: int, customer_id: int) -> Result:
        payment_model = self.session.get(ARPaymentModel, payment_id)
        if not payment_model:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Payment", id=str(payment_id)))

        invoices = self.get_invoices_with_balance(customer_id)
        if not invoices:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id="no_open_invoices"))

        remaining = payment_model.amount
        allocations = []

        for inv in invoices:
            if remaining <= Decimal("0"):
                break
            alloc_amount = min(inv.balance_due, remaining)
            remaining -= alloc_amount

            inv.paid_amount = _vnd(inv.paid_amount + alloc_amount)
            inv.balance_due = _vnd(inv.balance_due - alloc_amount)
            if inv.balance_due <= Decimal("0"):
                inv.status = InvoiceStatusDB.PAID
            else:
                inv.status = InvoiceStatusDB.PARTIALLY_PAID

            alloc = ARPaymentAllocationModel(
                ar_payment_id=payment_id,
                ar_invoice_id=inv.id,
                allocated_amount=alloc_amount,
            )
            self.session.add(alloc)
            allocations.append({"invoice_id": inv.id, "amount": alloc_amount})

        payment_model.amount_applied = _vnd(payment_model.amount - remaining)
        payment_model.amount_unapplied = _vnd(remaining)
        self.session.flush()
        return Result.success({
            "payment_id": payment_id,
            "amount": payment_model.amount,
            "amount_applied": payment_model.amount_applied,
            "amount_unapplied": payment_model.amount_unapplied,
            "allocations": allocations,
        })

    def get_payment(self, payment_id: int) -> Optional[ARPayment]:
        m = self.session.get(ARPaymentModel, payment_id)
        return self._payment_to_domain(m) if m else None

    def get_payments_for_invoice(self, invoice_id: int) -> List[ARPayment]:
        models = self.session.execute(
            select(ARPaymentModel).where(ARPaymentModel.invoice_id == invoice_id)
            .order_by(ARPaymentModel.payment_date)
        ).scalars().all()
        return [self._payment_to_domain(m) for m in models]

    def list_payments(
        self,
        customer_code: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ARPayment]:
        stmt = select(ARPaymentModel)
        if customer_code:
            stmt = stmt.join(ARInvoiceModel).where(ARInvoiceModel.customer_code == customer_code)
        if date_from:
            stmt = stmt.where(ARPaymentModel.payment_date >= date_from)
        if date_to:
            stmt = stmt.where(ARPaymentModel.payment_date <= date_to)
        stmt = stmt.order_by(desc(ARPaymentModel.payment_date)).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._payment_to_domain(m) for m in models]

    # ── Payment Allocations ──────────────────────────────────────────
    def get_allocations_for_payment(self, payment_id: int) -> List[ARPaymentAllocation]:
        allocs = self.session.execute(
            select(ARPaymentAllocationModel).where(
                ARPaymentAllocationModel.ar_payment_id == payment_id
            )
        ).scalars().all()
        result = []
        for a in allocs:
            result.append(ARPaymentAllocation(
                id=a.id,
                ar_payment_id=a.ar_payment_id,
                ar_invoice_id=a.ar_invoice_id,
                allocated_amount=a.allocated_amount,
                is_adjustment=a.is_adjustment,
                created_at=a.created_at,
            ))
        return result

    # ── Aging Snapshots ──────────────────────────────────────────────
    def create_aging_snapshot(self, snapshot: ARAgingSnapshot) -> Result:
        existing = self.session.execute(
            select(ARAgingSnapshotModel).where(
                ARAgingSnapshotModel.period == snapshot.period,
                ARAgingSnapshotModel.customer_id == snapshot.customer_id,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(
                ErrorCodes.ALREADY_EXISTS,
                type="AgingSnapshot",
                id=f"{snapshot.period}/{snapshot.customer_id}"
            ))
        model = ARAgingSnapshotModel(
            period=snapshot.period,
            customer_id=snapshot.customer_id,
            customer_code=snapshot.customer_code,
            customer_name=snapshot.customer_name,
            current_amount=snapshot.current_amount,
            bucket_1_30=snapshot.bucket_1_30,
            bucket_31_60=snapshot.bucket_31_60,
            bucket_61_90=snapshot.bucket_61_90,
            bucket_91_180=snapshot.bucket_91_180,
            bucket_181_365=snapshot.bucket_181_365,
            bucket_365_plus=snapshot.bucket_365_plus,
            total_outstanding=snapshot.total_outstanding,
            locked=True,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(snapshot)

    def get_aging_snapshots(self, period: str) -> List[ARAgingSnapshot]:
        models = self.session.execute(
            select(ARAgingSnapshotModel).where(ARAgingSnapshotModel.period == period)
            .order_by(ARAgingSnapshotModel.customer_code)
        ).scalars().all()
        result = []
        for m in models:
            result.append(ARAgingSnapshot(
                id=m.id, period=m.period, customer_id=m.customer_id,
                customer_code=m.customer_code, customer_name=m.customer_name,
                current_amount=m.current_amount, bucket_1_30=m.bucket_1_30,
                bucket_31_60=m.bucket_31_60, bucket_61_90=m.bucket_61_90,
                bucket_91_180=m.bucket_91_180, bucket_181_365=m.bucket_181_365,
                bucket_365_plus=m.bucket_365_plus, total_outstanding=m.total_outstanding,
                locked=m.locked, generated_at=m.generated_at,
            ))
        return result

    # ── Dunning ──────────────────────────────────────────────────────
    def log_dunning(self, log: ARDunningLog) -> Result:
        model = ARDunningLogModel(
            ar_invoice_id=log.ar_invoice_id,
            dunning_level=log.dunning_level,
            dunning_date=log.dunning_date,
            dunning_method=log.dunning_method,
            notes=log.notes,
            performed_by=log.performed_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(log)

    def get_dunning_logs(self, invoice_id: int) -> List[ARDunningLog]:
        models = self.session.execute(
            select(ARDunningLogModel).where(ARDunningLogModel.ar_invoice_id == invoice_id)
            .order_by(desc(ARDunningLogModel.dunning_date))
        ).scalars().all()
        result = []
        for m in models:
            result.append(ARDunningLog(
                id=m.id, ar_invoice_id=m.ar_invoice_id,
                dunning_level=m.dunning_level, dunning_date=m.dunning_date,
                dunning_method=m.dunning_method, notes=m.notes,
                performed_by=m.performed_by, created_at=m.created_at,
            ))
        return result

    def get_overdue_invoices_for_dunning(self, as_of: date) -> List[ARInvoiceModel]:
        stmt = select(ARInvoiceModel).where(
            ARInvoiceModel.status.in_([
                InvoiceStatusDB.ISSUED, InvoiceStatusDB.PARTIALLY_PAID, InvoiceStatusDB.OVERDUE
            ]),
            ARInvoiceModel.due_date < as_of,
            ARInvoiceModel.dunning_level < 5,
            ARInvoiceModel.balance_due > 0,
        ).order_by(ARInvoiceModel.due_date)
        return self.session.execute(stmt).scalars().all()

    # ── Bad Debt Provisions ──────────────────────────────────────────
    def create_provision(self, provision: BadDebtProvision) -> Result:
        existing = self.session.execute(
            select(BadDebtProvisionModel).where(
                BadDebtProvisionModel.period == provision.period,
                BadDebtProvisionModel.ar_invoice_id == provision.ar_invoice_id,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(
                ErrorCodes.ALREADY_EXISTS,
                type="BadDebtProvision",
                id=f"{provision.period}/{provision.ar_invoice_id}"
            ))
        model = BadDebtProvisionModel(
            customer_id=provision.customer_id,
            ar_invoice_id=provision.ar_invoice_id,
            period=provision.period,
            provision_percent=provision.provision_percent,
            invoice_amount=provision.invoice_amount,
            provision_amount=provision.provision_amount,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(provision)

    def get_provisions_for_period(self, period: str) -> List[BadDebtProvision]:
        models = self.session.execute(
            select(BadDebtProvisionModel).where(BadDebtProvisionModel.period == period)
        ).scalars().all()
        result = []
        for m in models:
            result.append(BadDebtProvision(
                id=m.id, customer_id=m.customer_id, ar_invoice_id=m.ar_invoice_id,
                period=m.period, provision_percent=m.provision_percent,
                invoice_amount=m.invoice_amount, provision_amount=m.provision_amount,
                is_written_off=m.is_written_off, created_at=m.created_at,
            ))
        return result

    def get_overdue_invoices_for_provision(self, period: str, min_days: int = 180) -> List[ARInvoiceModel]:
        cutoff = date.today()
        stmt = select(ARInvoiceModel).where(
            ARInvoiceModel.status.notin_([
                InvoiceStatusDB.PAID, InvoiceStatusDB.CANCELLED, InvoiceStatusDB.WRITTEN_OFF
            ]),
            ARInvoiceModel.balance_due > 0,
            ARInvoiceModel.dunning_level >= 5,
        )
        return self.session.execute(stmt).scalars().all()

    def mark_provision_written_off(self, provision_id: int) -> bool:
        model = self.session.get(BadDebtProvisionModel, provision_id)
        if not model:
            return False
        model.is_written_off = True
        self.session.flush()
        return True

    # ── Write-Off Requests ───────────────────────────────────────────
    def create_write_off_request(self, req: BadDebtWriteOffRequest) -> Result:
        model = BadDebtWriteOffRequestModel(
            ar_invoice_id=req.ar_invoice_id,
            customer_id=req.customer_id,
            reason=req.reason,
            supporting_docs=req.supporting_docs,
            status=WriteOffRequestStatusDB(req.status.value),
            created_by=req.created_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(req)

    def get_write_off_request(self, request_id: int) -> Optional[BadDebtWriteOffRequest]:
        m = self.session.get(BadDebtWriteOffRequestModel, request_id)
        if not m:
            return None
        return BadDebtWriteOffRequest(
            id=m.id, ar_invoice_id=m.ar_invoice_id, customer_id=m.customer_id,
            reason=m.reason, supporting_docs=m.supporting_docs,
            status=m.status.value,  # simplified
            approval_by=m.approval_by, approval_notes=m.approval_notes,
            created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
        )

    def list_write_off_requests(self, status: Optional[str] = None) -> List[BadDebtWriteOffRequest]:
        stmt = select(BadDebtWriteOffRequestModel).order_by(desc(BadDebtWriteOffRequestModel.created_at))
        if status:
            stmt = stmt.where(BadDebtWriteOffRequestModel.status == WriteOffRequestStatusDB(status))
        models = self.session.execute(stmt).scalars().all()
        result = []
        for m in models:
            result.append(BadDebtWriteOffRequest(
                id=m.id, ar_invoice_id=m.ar_invoice_id, customer_id=m.customer_id,
                reason=m.reason, supporting_docs=m.supporting_docs,
                status=m.status.value,
                approval_by=m.approval_by, approval_notes=m.approval_notes,
                created_by=m.created_by, created_at=m.created_at, updated_at=m.updated_at,
            ))
        return result

    def approve_write_off(self, request_id: int, approval_by: str, approval_notes: Optional[str] = None) -> Result:
        model = self.session.get(BadDebtWriteOffRequestModel, request_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="WriteOffRequest", id=str(request_id)))
        model.status = WriteOffRequestStatusDB.APPROVED
        model.approval_by = approval_by
        model.approval_notes = approval_notes
        self.session.flush()

        invoice = self.session.get(ARInvoiceModel, model.ar_invoice_id)
        if invoice:
            invoice.status = InvoiceStatusDB.WRITTEN_OFF
            invoice.written_off_amount = invoice.balance_due
            invoice.balance_due = Decimal("0")
            self.session.flush()
        return Result.success(None)

    def reject_write_off(self, request_id: int, approval_by: str, reason: Optional[str] = None) -> Result:
        model = self.session.get(BadDebtWriteOffRequestModel, request_id)
        if not model:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="WriteOffRequest", id=str(request_id)))
        model.status = WriteOffRequestStatusDB.REJECTED
        model.approval_by = approval_by
        model.approval_notes = reason
        self.session.flush()
        return Result.success(None)
