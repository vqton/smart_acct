from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_, desc

from domain import (
    Customer, CustomerType, CustomerGroup, CustomerStatus,
    ARInvoice, InvoiceLine, ARPayment, ARInvoiceType, ARInvoiceStatus, ARPaymentMethod,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.models.ar_models import (
    CustomerModel, ARInvoiceModel, ARInvoiceLineModel, ARPaymentModel,
    CustomerTypeDB, CustomerGroupDB, CustomerStatusDB,
    InvoiceTypeDB, InvoiceStatusDB, PaymentMethodDB,
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
        allowed = ("legal_name", "tax_code", "email", "phone", "address", "city",
                   "contact_person", "credit_limit", "outstanding_balance",
                   "coa_account_code", "notes", "status")
        for k, v in updates.items():
            if k in allowed:
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
            invoice_type=InvoiceType(m.invoice_type.value),
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
                   "posted_by", "coa_code", "einvoice_id")
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

    # ── Payment CRUD ────────────────────────────────────────────────
    def _payment_to_domain(self, m: ARPaymentModel) -> ARPayment:
        p = ARPayment(
            payment_number=m.payment_number,
            invoice_id=m.invoice_id,
            payment_date=m.payment_date,
            amount=m.amount,
            payment_method=PaymentMethod(m.payment_method.value),
            reference=m.reference,
            notes=m.notes,
            received_by=m.received_by,
            bank_account_id=m.bank_account_id,
            coa_code=m.coa_code,
            created_at=m.created_at,
        )
        p.id = m.id
        return p

    def _payment_to_model(self, d: ARPayment) -> ARPaymentModel:
        return ARPaymentModel(
            payment_number=d.payment_number,
            invoice_id=d.invoice_id,
            payment_date=d.payment_date,
            amount=d.amount,
            payment_method=PaymentMethodDB(d.payment_method.value),
            reference=d.reference,
            notes=d.notes,
            received_by=d.received_by,
            bank_account_id=d.bank_account_id,
            coa_code=d.coa_code,
        )

    def _payment_to_model(self, d: ARPayment) -> ARPaymentModel:
        return ARPaymentModel(
            payment_number=d.payment_number,
            invoice_id=d.invoice_id,
            payment_date=d.payment_date,
            amount=d.amount,
            payment_method=PaymentMethodDB(d.payment_method.value),
            reference=d.reference,
            notes=d.notes,
            received_by=d.received_by,
            bank_account_id=d.bank_account_id,
            coa_code=d.coa_code,
        )

    def create_payment(self, payment: ARPayment) -> Result:
        existing = self.session.execute(
            select(ARPaymentModel).where(ARPaymentModel.payment_number == payment.payment_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="Payment", id=payment.payment_number))
        invoice = self.session.get(ARInvoiceModel, payment.invoice_id)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(payment.invoice_id)))
        if payment.amount > (invoice.balance_due + Decimal("0.01")):
            return Result.failure(ValidationError(ErrorCodes.OVERPAYMENT_NOT_ALLOWED,
                                                  amount=str(payment.amount),
                                                  balance=str(invoice.balance_due)))
        model = self._payment_to_model(payment)
        self.session.add(model)
        self.session.flush()
        self.add_payment_to_invoice(payment.invoice_id, payment.amount)
        return Result.success(self._payment_to_domain(model))

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
