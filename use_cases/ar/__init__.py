from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select

from domain import (
    Customer, CustomerType, CustomerGroup, CustomerStatus,
    ARInvoice, ARInvoiceType, ARInvoiceStatus, InvoiceLine, ARPayment, ARPaymentMethod,
    Result, ValidationError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.ar_repository import ARRepository
from infrastructure.models.ar_models import (
    ARInvoiceModel,
    InvoiceStatusDB as _InvoiceStatusDB,
)


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class ARUseCases:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ARRepository(session)

    # ── UC-AR-01..04 Customer CRUD ──────────────────────────────────
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

    # ── UC-AR-05..08 Invoice CRUD ───────────────────────────────────
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
        return self.repo.create_invoice(invoice)

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
        invoice = self.repo.update_invoice_status(invoice_id, ARInvoiceStatus.ISSUED)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        return Result.success(invoice)

    def cancel_invoice(self, invoice_id: int, reason: Optional[str] = None) -> Result:
        invoice = self.repo.update_invoice_status(invoice_id, ARInvoiceStatus.CANCELLED)
        if not invoice:
            return Result.failure(ValidationError(ErrorCodes.NOT_FOUND,
                                                  type="Invoice", id=str(invoice_id)))
        return Result.success(invoice)

    # ── UC-AR-09..11 Payments ───────────────────────────────────────
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
    ) -> Result:
        payment = ARPayment(
            payment_number=payment_number,
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
        return self.repo.create_payment(payment)

    def get_payments_for_invoice(self, invoice_id: int) -> List[ARPayment]:
        return self.repo.get_payments_for_invoice(invoice_id)

    # ── UC-AR-12 Aging ──────────────────────────────────────────────
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
            )
            .where(ARInvoiceModel.balance_due > 0)
            .where(ARInvoiceModel.due_date < as_of)
            .where(ARInvoiceModel.status.notin_([
                _InvoiceStatusDB.CANCELLED, _InvoiceStatusDB.WRITTEN_OFF,
            ]))
        )
        if customer_id is not None:
            stmt = stmt.where(ARInvoiceModel.customer_id == customer_id)
        stmt = stmt.group_by(
            ARInvoiceModel.customer_id,
            ARInvoiceModel.customer_code,
            ARInvoiceModel.customer_name,
        )
        rows = self.session.execute(stmt).all()
        result = []
        for row in rows:
            outstanding = self.repo.get_customer_outstanding(row.customer_id)
            result.append({
                "customer_id": row.customer_id,
                "customer_code": row.customer_code,
                "customer_name": row.customer_name,
                "balance_due": outstanding,
            })
        return result

    # ── UC-AR-13..15 stubs (Phase 2+) ──────────────────────────────
    def get_ar_balance_sheet(self, period: str) -> Dict[str, Any]:
        return {"period": period, "receivables": Decimal("0"), "provision": Decimal("0")}
