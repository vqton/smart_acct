from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, or_, desc

from domain import Result, ValidationError
from domain.ap import (
    Vendor, VendorType, VendorGroup, VendorStatus,
    APInvoice, APInvoiceLine, APInvoiceType, APInvoiceStatus,
    APPayment, APPaymentStatus, APPaymentMethod, APPaymentAllocation,
    VendorPrepayment, PrepaymentStatus,
    APProvision, ProvisionStatus,
    APAgingSnapshot,
    FCTDeclaration, FCTMethod, FCTStatus,
    IntercompanyInvoice,
)
from domain.i18n import ErrorCodes
from infrastructure.models.ap_models import (
    VendorModel, VendorTypeDB, VendorGroupDB, VendorStatusDB,
    APInvoiceModel, APInvoiceTypeDB, APInvoiceStatusDB, APInvoiceLineModel,
    APPaymentModel, APPaymentStatusDB, APPaymentMethodDB,
    APPaymentAllocationModel,
    VendorPrepaymentModel, PrepaymentStatusDB,
    APProvisionModel, ProvisionStatusDB,
    APAgingSnapshotModel,
    FCTDeclarationModel, FCTMethodDB, FCTStatusDB,
    IntercompanyInvoiceModel,
)


def _vnd(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"))


class APRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Vendor mappings ──────────────────────────────────────────
    def _vendor_to_domain(self, m: VendorModel) -> Vendor:
        v = Vendor(
            vendor_code=m.vendor_code,
            vendor_name=m.vendor_name,
            legal_name=m.legal_name,
            tax_code=m.tax_code,
            vendor_type=VendorType(m.vendor_type.value),
            vendor_group=VendorGroup(m.vendor_group.value),
            status=VendorStatus(m.status.value),
            email=m.email,
            phone=m.phone,
            address=m.address,
            city=m.city,
            country=m.country,
            contact_person=m.contact_person,
            payment_terms=m.payment_terms,
            currency=m.currency,
            bank_name=m.bank_name,
            bank_account=m.bank_account,
            bank_swift=m.bank_swift,
            credit_limit=m.credit_limit,
            coa_code=m.coa_code,
            foreign_ct_type=m.foreign_ct_type,
            foreign_vat_rate=m.foreign_vat_rate,
            foreign_cit_rate=m.foreign_cit_rate,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        v.id = m.id
        return v

    def _vendor_to_model(self, d: Vendor) -> VendorModel:
        return VendorModel(
            vendor_code=d.vendor_code,
            vendor_name=d.vendor_name,
            legal_name=d.legal_name,
            tax_code=d.tax_code,
            vendor_type=VendorTypeDB(d.vendor_type.value),
            vendor_group=VendorGroupDB(d.vendor_group.value),
            status=VendorStatusDB(d.status.value),
            email=d.email,
            phone=d.phone,
            address=d.address,
            city=d.city,
            country=d.country,
            contact_person=d.contact_person,
            payment_terms=d.payment_terms,
            currency=d.currency,
            bank_name=d.bank_name,
            bank_account=d.bank_account,
            bank_swift=d.bank_swift,
            credit_limit=d.credit_limit,
            coa_code=d.coa_code,
            foreign_ct_type=d.foreign_ct_type,
            foreign_vat_rate=d.foreign_vat_rate,
            foreign_cit_rate=d.foreign_cit_rate,
            notes=d.notes,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )

    # ── Vendor CRUD ──────────────────────────────────────────────
    def create_vendor(self, vendor: Vendor) -> Result:
        existing = self.session.execute(
            select(VendorModel).where(VendorModel.vendor_code == vendor.vendor_code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="Vendor", id=vendor.vendor_code))
        model = self._vendor_to_model(vendor)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._vendor_to_domain(model))

    def get_vendor(self, vendor_id: int) -> Optional[Vendor]:
        m = self.session.get(VendorModel, vendor_id)
        return self._vendor_to_domain(m) if m else None

    def get_vendor_by_code(self, code: str) -> Optional[Vendor]:
        m = self.session.execute(
            select(VendorModel).where(VendorModel.vendor_code == code)
        ).scalar_one_or_none()
        return self._vendor_to_domain(m) if m else None

    def list_vendors(
        self,
        vendor_type: Optional[VendorType] = None,
        vendor_group: Optional[VendorGroup] = None,
        status: Optional[VendorStatus] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Vendor]:
        stmt = select(VendorModel)
        if vendor_type:
            stmt = stmt.where(VendorModel.vendor_type == VendorTypeDB(vendor_type.value))
        if vendor_group:
            stmt = stmt.where(VendorModel.vendor_group == VendorGroupDB(vendor_group.value))
        if status:
            stmt = stmt.where(VendorModel.status == VendorStatusDB(status.value))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(VendorModel.vendor_code.ilike(pattern),
                    VendorModel.vendor_name.ilike(pattern))
            )
        stmt = stmt.order_by(VendorModel.vendor_code).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._vendor_to_domain(m) for m in models]

    def update_vendor(self, vendor_id: int, **updates) -> Optional[Vendor]:
        model = self.session.get(VendorModel, vendor_id)
        if not model:
            return None
        allowed = ("vendor_name", "legal_name", "tax_code", "email", "phone", "address", "city",
                   "contact_person", "credit_limit", "coa_code", "notes", "status", "vendor_type",
                   "vendor_group", "payment_terms", "currency", "bank_name", "bank_account",
                   "bank_swift", "foreign_ct_type", "foreign_vat_rate", "foreign_cit_rate")
        for k, v in updates.items():
            if k in allowed:
                if k == "status" and isinstance(v, VendorStatus):
                    setattr(model, k, VendorStatusDB(v.value))
                elif k == "vendor_type" and isinstance(v, VendorType):
                    setattr(model, k, VendorTypeDB(v.value))
                elif k == "vendor_group" and isinstance(v, VendorGroup):
                    setattr(model, k, VendorGroupDB(v.value))
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._vendor_to_domain(model)

    def delete_vendor(self, vendor_id: int) -> bool:
        model = self.session.get(VendorModel, vendor_id)
        if not model:
            return False
        self.session.delete(model)
        return True

    # ── Line mappings ────────────────────────────────────────────
    def _line_to_domain(self, m: APInvoiceLineModel) -> APInvoiceLine:
        return APInvoiceLine(
            id=m.id,
            ap_invoice_id=m.ap_invoice_id,
            line_number=m.line_number,
            description=m.description,
            quantity=m.quantity,
            unit_price=m.unit_price,
            line_amount=m.line_amount,
            tax_rate=m.tax_rate,
            tax_amount=m.tax_amount,
            coa_code=m.coa_code,
            po_line_number=m.po_line_number,
            gr_line_number=m.gr_line_number,
        )

    def _line_to_model(self, d: APInvoiceLine, invoice_id: int) -> APInvoiceLineModel:
        return APInvoiceLineModel(
            ap_invoice_id=invoice_id,
            line_number=d.line_number,
            description=d.description,
            quantity=d.quantity,
            unit_price=d.unit_price,
            line_amount=d.line_amount,
            tax_rate=d.tax_rate,
            tax_amount=d.tax_amount,
            coa_code=d.coa_code,
            po_line_number=d.po_line_number,
            gr_line_number=d.gr_line_number,
        )

    # ── Invoice mappings ─────────────────────────────────────────
    def _invoice_to_domain(self, m: APInvoiceModel) -> APInvoice:
        inv = APInvoice(
            invoice_number=m.invoice_number,
            vendor_id=m.vendor_id,
            vendor_code=m.vendor_code,
            vendor_name=m.vendor_name,
            invoice_type=APInvoiceType(m.invoice_type.value),
            status=APInvoiceStatus(m.status.value),
            invoice_date=m.invoice_date,
            due_date=m.due_date,
            discount_date=m.discount_date,
            discount_percent=m.discount_percent,
            posted_date=m.posted_date,
            amount=m.amount,
            discount_amount=m.discount_amount,
            tax_amount=m.tax_amount,
            total_amount=m.total_amount,
            paid_amount=m.paid_amount,
            written_off_amount=m.written_off_amount,
            balance_due=m.balance_due,
            currency=m.currency,
            fx_rate=m.fx_rate,
            fx_gl_rate=m.fx_gl_rate,
            po_number=m.po_number,
            gr_number=m.gr_number,
            reference=m.reference,
            description=m.description,
            period=m.period,
            coa_code=m.coa_code,
            created_by=m.created_by,
            approved_by=m.approved_by,
            approved_at=m.approved_at,
            lines=[self._line_to_domain(l) for l in m.lines],
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        inv.id = m.id
        return inv

    def _invoice_to_model(self, d: APInvoice) -> APInvoiceModel:
        return APInvoiceModel(
            invoice_number=d.invoice_number,
            vendor_id=d.vendor_id,
            vendor_code=d.vendor_code,
            vendor_name=d.vendor_name,
            invoice_type=APInvoiceTypeDB(d.invoice_type.value),
            status=APInvoiceStatusDB(d.status.value),
            invoice_date=d.invoice_date,
            due_date=d.due_date,
            discount_date=d.discount_date,
            discount_percent=d.discount_percent,
            posted_date=d.posted_date,
            amount=d.amount,
            discount_amount=d.discount_amount,
            tax_amount=d.tax_amount,
            total_amount=d.total_amount,
            paid_amount=d.paid_amount,
            written_off_amount=d.written_off_amount,
            balance_due=d.balance_due,
            currency=d.currency,
            fx_rate=d.fx_rate,
            fx_gl_rate=d.fx_gl_rate,
            po_number=d.po_number,
            gr_number=d.gr_number,
            reference=d.reference,
            description=d.description,
            period=d.period,
            coa_code=d.coa_code,
            created_by=d.created_by,
            approved_by=d.approved_by,
            approved_at=d.approved_at,
        )

    # ── Invoice CRUD ─────────────────────────────────────────────
    def create_invoice(self, invoice: APInvoice) -> Result:
        existing = self.session.execute(
            select(APInvoiceModel).where(
                APInvoiceModel.invoice_number == invoice.invoice_number,
                APInvoiceModel.vendor_id == invoice.vendor_id,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="APInvoice",
                                                  id=f"{invoice.vendor_id}/{invoice.invoice_number}"))
        model = self._invoice_to_model(invoice)
        self.session.add(model)
        self.session.flush()
        for line in invoice.lines:
            lm = self._line_to_model(line, model.id)
            self.session.add(lm)
        self.session.flush()
        return Result.success(self._invoice_to_domain(model))

    def get_invoice(self, invoice_id: int) -> Optional[APInvoice]:
        m = self.session.get(APInvoiceModel, invoice_id)
        return self._invoice_to_domain(m) if m else None

    def get_invoice_by_number(self, number: str) -> Optional[APInvoice]:
        m = self.session.execute(
            select(APInvoiceModel).where(APInvoiceModel.invoice_number == number)
        ).scalar_one_or_none()
        return self._invoice_to_domain(m) if m else None

    def list_invoices(
        self,
        vendor_id: Optional[int] = None,
        vendor_code: Optional[str] = None,
        status: Optional[APInvoiceStatus] = None,
        period: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[APInvoice]:
        stmt = select(APInvoiceModel)
        if vendor_id is not None:
            stmt = stmt.where(APInvoiceModel.vendor_id == vendor_id)
        if vendor_code is not None:
            stmt = stmt.where(APInvoiceModel.vendor_code == vendor_code)
        if status:
            stmt = stmt.where(APInvoiceModel.status == APInvoiceStatusDB(status.value))
        if period:
            stmt = stmt.where(APInvoiceModel.period == period)
        stmt = stmt.order_by(desc(APInvoiceModel.invoice_date)).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._invoice_to_domain(m) for m in models]

    def update_invoice(self, invoice_id: int, **updates) -> Optional[APInvoice]:
        model = self.session.get(APInvoiceModel, invoice_id)
        if not model:
            return None
        allowed = ("amount", "discount_amount", "tax_amount", "total_amount",
                   "paid_amount", "written_off_amount", "balance_due",
                   "status", "reference", "description", "period", "coa_code",
                   "posted_date", "created_by", "approved_by", "approved_at",
                   "due_date", "discount_date", "discount_percent")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._invoice_to_domain(model)

    def update_invoice_status(self, invoice_id: int, new_status: APInvoiceStatus) -> Optional[APInvoice]:
        return self.update_invoice(invoice_id, status=APInvoiceStatusDB(new_status.value))

    # ── Payment mappings ─────────────────────────────────────────
    def _payment_to_domain(self, m: APPaymentModel) -> APPayment:
        p = APPayment(
            payment_number=m.payment_number,
            vendor_id=m.vendor_id,
            payment_date=m.payment_date,
            amount=m.amount,
            discount_taken=m.discount_taken,
            net_amount=m.net_amount,
            payment_method=APPaymentMethod(m.payment_method.value),
            bank_account_id=m.bank_account_id,
            reference=m.reference,
            status=APPaymentStatus(m.status.value),
            is_batch_payment=m.is_batch_payment,
            batch_id=m.batch_id,
            approval_by=m.approval_by,
            approval_at=m.approval_at,
            notes=m.notes,
            created_by=m.created_by,
            created_at=m.created_at,
        )
        p.id = m.id
        return p

    def _payment_to_model(self, d: APPayment) -> APPaymentModel:
        return APPaymentModel(
            payment_number=d.payment_number,
            vendor_id=d.vendor_id,
            payment_date=d.payment_date,
            amount=d.amount,
            discount_taken=d.discount_taken,
            net_amount=d.net_amount,
            payment_method=APPaymentMethodDB(d.payment_method.value),
            bank_account_id=d.bank_account_id,
            reference=d.reference,
            status=APPaymentStatusDB(d.status.value),
            is_batch_payment=d.is_batch_payment,
            batch_id=d.batch_id,
            approval_by=d.approval_by,
            approval_at=d.approval_at,
            notes=d.notes,
            created_by=d.created_by,
        )

    # ── Payment CRUD ─────────────────────────────────────────────
    def create_payment(self, payment: APPayment) -> Result:
        existing = self.session.execute(
            select(APPaymentModel).where(APPaymentModel.payment_number == payment.payment_number)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(ErrorCodes.ALREADY_EXISTS,
                                                  type="APPayment", id=payment.payment_number))
        model = self._payment_to_model(payment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._payment_to_domain(model))

    def get_payment(self, payment_id: int) -> Optional[APPayment]:
        m = self.session.get(APPaymentModel, payment_id)
        return self._payment_to_domain(m) if m else None

    def list_payments(
        self,
        vendor_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[APPayment]:
        stmt = select(APPaymentModel)
        if vendor_id is not None:
            stmt = stmt.where(APPaymentModel.vendor_id == vendor_id)
        if date_from:
            stmt = stmt.where(APPaymentModel.payment_date >= date_from)
        if date_to:
            stmt = stmt.where(APPaymentModel.payment_date <= date_to)
        stmt = stmt.order_by(desc(APPaymentModel.payment_date)).limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._payment_to_domain(m) for m in models]

    def get_payments_for_invoice(self, invoice_id: int) -> List[APPayment]:
        models = self.session.execute(
            select(APPaymentModel).join(
                APPaymentAllocationModel,
                APPaymentAllocationModel.ap_payment_id == APPaymentModel.id
            ).where(APPaymentAllocationModel.ap_invoice_id == invoice_id)
        ).scalars().all()
        return [self._payment_to_domain(m) for m in models]

    # ── Payment Allocation mappings ──────────────────────────────
    def _allocation_to_domain(self, m: APPaymentAllocationModel) -> APPaymentAllocation:
        return APPaymentAllocation(
            id=m.id,
            ap_payment_id=m.ap_payment_id,
            ap_invoice_id=m.ap_invoice_id,
            allocated_amount=m.allocated_amount,
            is_adjustment=m.is_adjustment,
            created_at=m.created_at,
        )

    def _allocation_to_model(self, d: APPaymentAllocation) -> APPaymentAllocationModel:
        return APPaymentAllocationModel(
            ap_payment_id=d.ap_payment_id,
            ap_invoice_id=d.ap_invoice_id,
            allocated_amount=d.allocated_amount,
            is_adjustment=d.is_adjustment,
        )

    def create_payment_allocation(self, allocation: APPaymentAllocation) -> Result:
        model = self._allocation_to_model(allocation)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._allocation_to_domain(model))

    def get_payment_allocations(self, payment_id: int) -> List[APPaymentAllocation]:
        models = self.session.execute(
            select(APPaymentAllocationModel).where(
                APPaymentAllocationModel.ap_payment_id == payment_id
            )
        ).scalars().all()
        return [self._allocation_to_domain(m) for m in models]

    # ── Prepayment mappings ──────────────────────────────────────
    def _prepayment_to_domain(self, m: VendorPrepaymentModel) -> VendorPrepayment:
        p = VendorPrepayment(
            vendor_id=m.vendor_id,
            amount=m.amount,
            unapplied_balance=m.unapplied_balance,
            payment_date=m.payment_date,
            expected_invoice_date=m.expected_invoice_date,
            reference=m.reference,
            status=PrepaymentStatus(m.status.value),
            created_by=m.created_by,
            created_at=m.created_at,
        )
        p.id = m.id
        return p

    def _prepayment_to_model(self, d: VendorPrepayment) -> VendorPrepaymentModel:
        return VendorPrepaymentModel(
            vendor_id=d.vendor_id,
            amount=d.amount,
            unapplied_balance=d.unapplied_balance,
            payment_date=d.payment_date,
            expected_invoice_date=d.expected_invoice_date,
            reference=d.reference,
            status=PrepaymentStatusDB(d.status.value),
            created_by=d.created_by,
        )

    # ── Prepayment CRUD ──────────────────────────────────────────
    def create_prepayment(self, prepayment: VendorPrepayment) -> Result:
        model = self._prepayment_to_model(prepayment)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._prepayment_to_domain(model))

    def get_prepayment(self, prepayment_id: int) -> Optional[VendorPrepayment]:
        m = self.session.get(VendorPrepaymentModel, prepayment_id)
        return self._prepayment_to_domain(m) if m else None

    def list_prepayments(
        self,
        vendor_id: Optional[int] = None,
        status: Optional[PrepaymentStatus] = None,
    ) -> List[VendorPrepayment]:
        stmt = select(VendorPrepaymentModel)
        if vendor_id is not None:
            stmt = stmt.where(VendorPrepaymentModel.vendor_id == vendor_id)
        if status:
            stmt = stmt.where(VendorPrepaymentModel.status == PrepaymentStatusDB(status.value))
        stmt = stmt.order_by(desc(VendorPrepaymentModel.payment_date))
        models = self.session.execute(stmt).scalars().all()
        return [self._prepayment_to_domain(m) for m in models]

    def update_prepayment(self, prepayment_id: int, **updates) -> Optional[VendorPrepayment]:
        model = self.session.get(VendorPrepaymentModel, prepayment_id)
        if not model:
            return None
        allowed = ("amount", "unapplied_balance", "status", "expected_invoice_date",
                   "reference")
        for k, v in updates.items():
            if k in allowed:
                if k == "status" and isinstance(v, PrepaymentStatus):
                    setattr(model, k, PrepaymentStatusDB(v.value))
                else:
                    setattr(model, k, v)
        self.session.flush()
        return self._prepayment_to_domain(model)

    def get_vendor_prepayment_balance(self, vendor_id: int) -> Decimal:
        result = self.session.execute(
            select(func.coalesce(func.sum(VendorPrepaymentModel.unapplied_balance), Decimal("0")))
            .where(VendorPrepaymentModel.vendor_id == vendor_id)
            .where(VendorPrepaymentModel.status == PrepaymentStatusDB.PENDING)
        ).scalar_one()
        return _vnd(result)

    # ── Provision mappings ───────────────────────────────────────
    def _provision_to_domain(self, m: APProvisionModel) -> APProvision:
        p = APProvision(
            vendor_id=m.vendor_id,
            period=m.period,
            provision_percent=m.provision_percent,
            overdue_days=m.overdue_days,
            invoice_total=m.invoice_total,
            provision_amount=m.provision_amount,
            status=ProvisionStatus(m.status.value),
            created_at=m.created_at,
        )
        p.id = m.id
        return p

    def _provision_to_model(self, d: APProvision) -> APProvisionModel:
        return APProvisionModel(
            vendor_id=d.vendor_id,
            period=d.period,
            provision_percent=d.provision_percent,
            overdue_days=d.overdue_days,
            invoice_total=d.invoice_total,
            provision_amount=d.provision_amount,
            status=ProvisionStatusDB(d.status.value),
        )

    # ── Provision CRUD ───────────────────────────────────────────
    def create_provision(self, provision: APProvision) -> Result:
        existing = self.session.execute(
            select(APProvisionModel).where(
                APProvisionModel.period == provision.period,
                APProvisionModel.vendor_id == provision.vendor_id,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(
                ErrorCodes.ALREADY_EXISTS,
                type="APProvision",
                id=f"{provision.period}/{provision.vendor_id}"
            ))
        model = self._provision_to_model(provision)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._provision_to_domain(model))

    def get_provision(self, provision_id: int) -> Optional[APProvision]:
        m = self.session.get(APProvisionModel, provision_id)
        return self._provision_to_domain(m) if m else None

    def get_provisions(self, period: str) -> List[APProvision]:
        models = self.session.execute(
            select(APProvisionModel).where(APProvisionModel.period == period)
            .order_by(APProvisionModel.vendor_id)
        ).scalars().all()
        return [self._provision_to_domain(m) for m in models]

    def list_provisions(
        self,
        vendor_id: Optional[int] = None,
        period: Optional[str] = None,
    ) -> List[APProvision]:
        stmt = select(APProvisionModel)
        if vendor_id is not None:
            stmt = stmt.where(APProvisionModel.vendor_id == vendor_id)
        if period:
            stmt = stmt.where(APProvisionModel.period == period)
        stmt = stmt.order_by(APProvisionModel.vendor_id)
        models = self.session.execute(stmt).scalars().all()
        return [self._provision_to_domain(m) for m in models]

    # ── Aging Snapshot mappings ──────────────────────────────────
    def _aging_snapshot_to_domain(self, m: APAgingSnapshotModel) -> APAgingSnapshot:
        return APAgingSnapshot(
            id=m.id, period=m.period, vendor_id=m.vendor_id,
            vendor_code=m.vendor_code, vendor_name=m.vendor_name,
            current_amount=m.current_amount, bucket_1_30=m.bucket_1_30,
            bucket_31_60=m.bucket_31_60, bucket_61_90=m.bucket_61_90,
            bucket_91_180=m.bucket_91_180, bucket_181_365=m.bucket_181_365,
            bucket_365_plus=m.bucket_365_plus, total_outstanding=m.total_outstanding,
            locked=m.locked, generated_at=m.generated_at,
        )

    def _aging_snapshot_to_model(self, d: APAgingSnapshot) -> APAgingSnapshotModel:
        return APAgingSnapshotModel(
            period=d.period,
            vendor_id=d.vendor_id,
            vendor_code=d.vendor_code,
            vendor_name=d.vendor_name,
            current_amount=d.current_amount,
            bucket_1_30=d.bucket_1_30,
            bucket_31_60=d.bucket_31_60,
            bucket_61_90=d.bucket_61_90,
            bucket_91_180=d.bucket_91_180,
            bucket_181_365=d.bucket_181_365,
            bucket_365_plus=d.bucket_365_plus,
            total_outstanding=d.total_outstanding,
            locked=True,
        )

    # ── Aging Snapshots ──────────────────────────────────────────
    def create_aging_snapshot(self, snapshot: APAgingSnapshot) -> Result:
        existing = self.session.execute(
            select(APAgingSnapshotModel).where(
                APAgingSnapshotModel.period == snapshot.period,
                APAgingSnapshotModel.vendor_id == snapshot.vendor_id,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(
                ErrorCodes.ALREADY_EXISTS,
                type="APAgingSnapshot",
                id=f"{snapshot.period}/{snapshot.vendor_id}"
            ))
        model = self._aging_snapshot_to_model(snapshot)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._aging_snapshot_to_domain(model))

    def get_aging_snapshots(self, period: str) -> List[APAgingSnapshot]:
        models = self.session.execute(
            select(APAgingSnapshotModel).where(APAgingSnapshotModel.period == period)
            .order_by(APAgingSnapshotModel.vendor_code)
        ).scalars().all()
        return [self._aging_snapshot_to_domain(m) for m in models]

    # ── FCT Declaration mappings ─────────────────────────────────
    def _fct_to_domain(self, m: FCTDeclarationModel) -> FCTDeclaration:
        f = FCTDeclaration(
            vendor_id=m.vendor_id,
            period=m.period,
            invoice_id=m.invoice_id,
            fct_method=FCTMethod(m.fct_method.value),
            vat_rate=m.vat_rate,
            cit_rate=m.cit_rate,
            gross_amount=m.gross_amount,
            vat_amount=m.vat_amount,
            cit_amount=m.cit_amount,
            net_amount=m.net_amount,
            status=FCTStatus(m.status.value),
            declared_at=m.declared_at,
            remitted_at=m.remitted_at,
            due_date=m.due_date,
            created_at=m.created_at,
        )
        f.id = m.id
        return f

    def _fct_to_model(self, d: FCTDeclaration) -> FCTDeclarationModel:
        return FCTDeclarationModel(
            vendor_id=d.vendor_id,
            period=d.period,
            invoice_id=d.invoice_id,
            fct_method=FCTMethodDB(d.fct_method.value),
            vat_rate=d.vat_rate,
            cit_rate=d.cit_rate,
            gross_amount=d.gross_amount,
            vat_amount=d.vat_amount,
            cit_amount=d.cit_amount,
            net_amount=d.net_amount,
            status=FCTStatusDB(d.status.value),
            declared_at=d.declared_at,
            remitted_at=d.remitted_at,
            due_date=d.due_date,
        )

    # ── FCT CRUD ─────────────────────────────────────────────────
    def create_fct_declaration(self, fct: FCTDeclaration) -> Result:
        existing = self.session.execute(
            select(FCTDeclarationModel).where(
                FCTDeclarationModel.invoice_id == fct.invoice_id,
                FCTDeclarationModel.period == fct.period,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ValidationError(
                ErrorCodes.ALREADY_EXISTS,
                type="FCTDeclaration",
                id=f"{fct.period}/{fct.invoice_id}"
            ))
        model = self._fct_to_model(fct)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._fct_to_domain(model))

    def get_fct_declarations(self, period: str) -> List[FCTDeclaration]:
        models = self.session.execute(
            select(FCTDeclarationModel).where(FCTDeclarationModel.period == period)
            .order_by(FCTDeclarationModel.vendor_id)
        ).scalars().all()
        return [self._fct_to_domain(m) for m in models]

    def update_fct_status(
        self,
        fct_id: int,
        status: FCTStatus,
        **updates,
    ) -> Optional[FCTDeclaration]:
        model = self.session.get(FCTDeclarationModel, fct_id)
        if not model:
            return None
        model.status = FCTStatusDB(status.value)
        allowed = ("declared_at", "remitted_at", "status")
        for k, v in updates.items():
            if k in allowed:
                setattr(model, k, v)
        self.session.flush()
        return self._fct_to_domain(model)

    # ── Intercompany Invoice mappings ────────────────────────────
    def _ic_invoice_to_domain(self, m: IntercompanyInvoiceModel) -> IntercompanyInvoice:
        inv = IntercompanyInvoice(
            from_entity_code=m.from_entity_code,
            to_entity_code=m.to_entity_code,
            invoice_number=m.invoice_number,
            invoice_date=m.invoice_date,
            amount=m.amount,
            currency=m.currency,
            description=m.description,
            reference=m.reference,
            created_by=m.created_by,
            created_at=m.created_at,
        )
        inv.id = m.id
        return inv

    def _ic_invoice_to_model(self, d: IntercompanyInvoice) -> IntercompanyInvoiceModel:
        return IntercompanyInvoiceModel(
            from_entity_code=d.from_entity_code,
            to_entity_code=d.to_entity_code,
            invoice_number=d.invoice_number,
            invoice_date=d.invoice_date,
            amount=d.amount,
            currency=d.currency,
            description=d.description,
            reference=d.reference,
            created_by=d.created_by,
        )

    def create_ic_invoice(self, ic_invoice: IntercompanyInvoice) -> Result:
        model = self._ic_invoice_to_model(ic_invoice)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._ic_invoice_to_domain(model))

    # ── Queries ──────────────────────────────────────────────────
    def get_overdue_invoices(self, as_of_date: date) -> List[APInvoice]:
        models = self.session.execute(
            select(APInvoiceModel).where(
                APInvoiceModel.due_date < as_of_date,
                APInvoiceModel.status.notin_([
                    APInvoiceStatusDB.PAID_FULL, APInvoiceStatusDB.CANCELLED,
                    APInvoiceStatusDB.WRITTEN_OFF, APInvoiceStatusDB.REJECTED,
                ]),
                APInvoiceModel.balance_due > 0,
            ).order_by(APInvoiceModel.due_date)
        ).scalars().all()
        return [self._invoice_to_domain(m) for m in models]

    def get_due_invoices(
        self,
        cutoff_date: date,
        vendor_ids: Optional[List[int]] = None,
    ) -> List[APInvoice]:
        stmt = select(APInvoiceModel).where(
            APInvoiceModel.due_date <= cutoff_date,
            APInvoiceModel.status.notin_([
                APInvoiceStatusDB.PAID_FULL, APInvoiceStatusDB.CANCELLED,
                APInvoiceStatusDB.WRITTEN_OFF, APInvoiceStatusDB.REJECTED,
            ]),
            APInvoiceModel.balance_due > 0,
        )
        if vendor_ids:
            stmt = stmt.where(APInvoiceModel.vendor_id.in_(vendor_ids))
        stmt = stmt.order_by(APInvoiceModel.due_date)
        models = self.session.execute(stmt).scalars().all()
        return [self._invoice_to_domain(m) for m in models]

    def get_invoices_with_balance(
        self,
        vendor_id: Optional[int] = None,
        as_of: Optional[date] = None,
    ) -> List[APInvoice]:
        stmt = select(APInvoiceModel).where(
            APInvoiceModel.status.notin_([
                APInvoiceStatusDB.PAID_FULL, APInvoiceStatusDB.CANCELLED,
                APInvoiceStatusDB.WRITTEN_OFF, APInvoiceStatusDB.REJECTED,
            ]),
            APInvoiceModel.balance_due > 0,
        )
        if vendor_id is not None:
            stmt = stmt.where(APInvoiceModel.vendor_id == vendor_id)
        if as_of is not None:
            stmt = stmt.where(APInvoiceModel.due_date <= as_of)
        stmt = stmt.order_by(APInvoiceModel.vendor_id, APInvoiceModel.due_date)
        models = self.session.execute(stmt).scalars().all()
        return [self._invoice_to_domain(m) for m in models]

    def get_vendor_outstanding(self, vendor_id: int) -> Decimal:
        result = self.session.execute(
            select(func.coalesce(func.sum(APInvoiceModel.balance_due), Decimal("0")))
            .where(APInvoiceModel.vendor_id == vendor_id)
            .where(APInvoiceModel.status.notin_([
                APInvoiceStatusDB.PAID_FULL, APInvoiceStatusDB.CANCELLED,
                APInvoiceStatusDB.WRITTEN_OFF, APInvoiceStatusDB.REJECTED,
            ]))
        ).scalar_one()
        return _vnd(result)

    def check_credit_limit(self, vendor_id: int, amount: Decimal) -> Dict[str, Any]:
        vendor = self.session.get(VendorModel, vendor_id)
        if not vendor:
            return {"approved": False, "error": "Vendor not found"}
        outstanding = self.get_vendor_outstanding(vendor_id)
        total_exposure = _vnd(outstanding + amount)
        result = {
            "approved": True,
            "vendor_code": vendor.vendor_code,
            "vendor_name": vendor.vendor_name,
            "credit_limit": vendor.credit_limit,
            "current_outstanding": outstanding,
            "new_amount": amount,
            "total_exposure": total_exposure,
            "utilization_pct": Decimal("0"),
            "warning": None,
        }
        if vendor.credit_limit > 0:
            utilization = _vnd((total_exposure / vendor.credit_limit) * Decimal("100"))
            result["utilization_pct"] = utilization
            if total_exposure > vendor.credit_limit:
                result["approved"] = False
                result["error"] = (
                    f"Credit limit exceeded: {total_exposure} > {vendor.credit_limit}"
                )
            elif utilization >= Decimal("80"):
                result["warning"] = f"Credit utilization at {utilization:.1f}%"
        return result
