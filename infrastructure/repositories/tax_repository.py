from typing import Optional, List, Any
from datetime import datetime, timezone, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_

from domain import (
    TaxType, VATCalculationMethod, DeclarationType, DeclarationStatus,
    TaxPaymentStatus, InvoiceStatus, TaxAdjustmentStatus,
    TaxDeclaration, TaxLine, TaxPayment, TaxAdjustment, TaxIncentive,
    EInvoice, EInvoiceLine, TaxSchedule,
    Result, ValidationError,
)
from infrastructure.models.tax_models import (
    TaxDeclarationModel, TaxLineModel, TaxPaymentModel, TaxAdjustmentModel,
    TaxIncentiveModel, EInvoiceModel, TaxScheduleModel,
    TaxTypeDB, DeclarationStatusDB, TaxPaymentStatusDB, InvoiceStatusDB,
)


class TaxRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Domain mapping helpers ──────────────────────────────────────────

    def _declaration_to_domain(self, model: TaxDeclarationModel) -> TaxDeclaration:
        return TaxDeclaration(
            id=model.id,
            tax_type=TaxType(model.tax_type.value),
            declaration_type=DeclarationType(model.declaration_type),
            form_code=model.form_code,
            period_year=model.period_year,
            period_month=model.period_month,
            period_quarter=model.period_quarter,
            status=DeclarationStatus(model.status.value),
            total_revenue=model.total_revenue or 0,
            total_tax=model.total_tax or 0,
            total_deduction=model.total_deduction or 0,
            total_exemption=model.total_exemption or 0,
            total_payable=model.total_payable or 0,
            previous_adjustment=model.previous_adjustment or 0,
            late_interest=model.late_interest or 0,
            penalty=model.penalty or 0,
            net_payable=model.net_payable or 0,
            submission_deadline=model.submission_deadline,
            submitted_date=model.submitted_date,
            accepted_date=model.accepted_date,
            gdt_reference=model.gdt_reference,
            gdt_error_code=model.gdt_error_code,
            etax_submission_id=model.etax_submission_id,
            submission_method=model.submission_method,
            notes=model.notes,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _payment_to_domain(self, model: TaxPaymentModel) -> TaxPayment:
        return TaxPayment(
            id=model.id,
            declaration_id=model.declaration_id,
            tax_type=TaxType(model.tax_type.value),
            amount=model.amount,
            payment_date=model.payment_date,
            due_date=model.due_date,
            budget_account=model.budget_account,
            payment_method=model.payment_method,
            payment_status=TaxPaymentStatus(model.payment_status.value),
            gdt_payment_code=model.gdt_payment_code,
            bank_reference=model.bank_reference,
            penalty_interest=model.penalty_interest or 0,
            notes=model.notes,
            created_at=model.created_at,
        )

    def _adjustment_to_domain(self, model: TaxAdjustmentModel) -> TaxAdjustment:
        return TaxAdjustment(
            id=model.id,
            declaration_id=model.original_declaration_id,
            adjustment_type=self._str_to_adjustment_type(model.adjustment_type),
            supplemental_declaration_id=model.supplemental_declaration_id,
            reason=model.reason,
            original_amount=model.original_amount or 0,
            adjusted_amount=model.adjusted_amount or 0,
            difference_amount=model.difference or 0,
            penalty_interest=model.late_interest or 0,
            penalty=model.penalty or 0,
            status=self._str_to_adjustment_status(model.approval_status),
            review_notes=None,
            reviewed_by=model.approved_by,
            reviewed_at=model.approval_date,
            created_by=model.created_by,
            created_at=model.created_at,
        )

    def _schedule_to_domain(self, model: TaxScheduleModel) -> TaxSchedule:
        from domain import ScheduleStatus
        return TaxSchedule(
            id=model.id,
            tax_type=TaxType(model.tax_type.value),
            period_year=model.period_year,
            period_month=model.period_month,
            period_quarter=model.period_quarter,
            due_date=model.due_date,
            reminder_days_before=model.reminder_days_before,
            status=ScheduleStatus(model.status) if model.status in [s.value for s in ScheduleStatus] else ScheduleStatus.PENDING,
            assigned_to=model.assigned_to,
            notes=model.notes,
            created_at=model.created_at,
        )

    def _invoice_to_domain(self, model: EInvoiceModel) -> EInvoice:
        from domain import InvoiceType, EInvoiceAdjustmentType
        inv_type = InvoiceType.SALES
        for t in InvoiceType:
            if t.value == model.invoice_type:
                inv_type = t
                break
        adj_type = None
        if model.adjustment_type:
            for t in EInvoiceAdjustmentType:
                if t.value == model.adjustment_type:
                    adj_type = t
                    break
        return EInvoice(
            id=model.id,
            invoice_number=model.invoice_number,
            invoice_series=model.invoice_series,
            invoice_date=model.invoice_date,
            invoice_type=inv_type,
            seller_tax_code=model.seller_tax_code,
            seller_name=model.seller_name,
            seller_address=model.seller_address,
            buyer_tax_code=model.buyer_tax_code,
            buyer_name=model.buyer_name,
            buyer_address=model.buyer_address,
            buyer_id=model.buyer_id,
            subtotal=model.subtotal or 0,
            discount_amount=model.discount_amount or 0,
            vat_rate=model.vat_rate or 0,
            vat_amount=model.vat_amount or 0,
            grand_total=model.grand_total or 0,
            currency=model.currency,
            exchange_rate=model.exchange_rate or 1,
            payment_method=model.payment_method,
            status=InvoiceStatus(model.status.value),
            verification_code=model.verification_code,
            gdt_transaction_id=model.gdt_transaction_id,
            signed_file_url=model.signed_file_url,
            digital_signature=model.digital_signature,
            adjustment_ref_id=model.adjustment_ref_id,
            adjustment_type=adj_type,
            adjustment_reason=model.adjustment_reason,
            original_invoice_ref=model.original_invoice_ref,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _str_to_adjustment_type(v: str):
        from domain import TaxAdjustmentType
        for t in TaxAdjustmentType:
            if t.value == v:
                return t
        return TaxAdjustmentType.CORRECTION

    @staticmethod
    def _str_to_adjustment_status(v: str):
        for s in TaxAdjustmentStatus:
            if s.value == v:
                return s
        return TaxAdjustmentStatus.PENDING

    # ── TaxDeclaration CRUD ─────────────────────────────────────────────

    def create_declaration(self, declaration: TaxDeclaration) -> Result:
        model = TaxDeclarationModel(
            tax_type=TaxTypeDB(declaration.tax_type.value),
            declaration_type=declaration.declaration_type.value,
            form_code=declaration.form_code,
            period_year=declaration.period_year,
            period_month=declaration.period_month,
            period_quarter=declaration.period_quarter,
            status=DeclarationStatusDB(declaration.status.value),
            total_revenue=declaration.total_revenue,
            total_tax=declaration.total_tax,
            total_deduction=declaration.total_deduction,
            total_exemption=declaration.total_exemption,
            total_payable=declaration.total_payable,
            previous_adjustment=declaration.previous_adjustment,
            late_interest=declaration.late_interest,
            penalty=declaration.penalty,
            net_payable=declaration.net_payable,
            submission_deadline=declaration.submission_deadline,
            submitted_date=declaration.submitted_date,
            accepted_date=declaration.accepted_date,
            gdt_reference=declaration.gdt_reference,
            gdt_error_code=declaration.gdt_error_code,
            etax_submission_id=declaration.etax_submission_id,
            submission_method=declaration.submission_method,
            notes=declaration.notes,
            created_by=declaration.created_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._declaration_to_domain(model))

    def get_declaration(self, decl_id: int) -> Optional[TaxDeclaration]:
        model = self.session.get(TaxDeclarationModel, decl_id)
        return self._declaration_to_domain(model) if model else None

    def list_declarations(
        self,
        tax_type: Optional[TaxType] = None,
        period_year: Optional[int] = None,
        status: Optional[DeclarationStatus] = None,
        declaration_type: Optional[DeclarationType] = None,
    ) -> List[TaxDeclaration]:
        stmt = select(TaxDeclarationModel)
        if tax_type:
            stmt = stmt.where(TaxDeclarationModel.tax_type == TaxTypeDB(tax_type.value))
        if period_year:
            stmt = stmt.where(TaxDeclarationModel.period_year == period_year)
        if status:
            stmt = stmt.where(TaxDeclarationModel.status == DeclarationStatusDB(status.value))
        if declaration_type:
            stmt = stmt.where(TaxDeclarationModel.declaration_type == declaration_type.value)
        stmt = stmt.order_by(TaxDeclarationModel.period_year.desc(), TaxDeclarationModel.id.desc())
        models = self.session.execute(stmt).scalars().all()
        return [self._declaration_to_domain(m) for m in models]

    def update_declaration(self, decl_id: int, **kwargs) -> Result:
        model = self.session.get(TaxDeclarationModel, decl_id)
        if not model:
            return Result.failure(ValidationError(f"Declaration {decl_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                if key == "status" and isinstance(value, DeclarationStatus):
                    setattr(model, key, DeclarationStatusDB(value.value))
                else:
                    setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._declaration_to_domain(model))

    def delete_declaration(self, decl_id: int) -> Result:
        model = self.session.get(TaxDeclarationModel, decl_id)
        if not model:
            return Result.failure(ValidationError(f"Declaration {decl_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── TaxLine CRUD ────────────────────────────────────────────────────

    def create_line(self, line: TaxLine) -> Result:
        model = TaxLineModel(
            declaration_id=line.declaration_id,
            line_code=line.line_code,
            label=line.label,
            amount=line.amount,
            is_calculated=line.is_calculated,
            parent_line_code=str(line.parent_line_id) if line.parent_line_id else None,
            sort_order=line.sort_order,
            notes=line.notes,
        )
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._line_to_domain(model))

    def _line_to_domain(self, model: TaxLineModel) -> TaxLine:
        return TaxLine(
            id=model.id,
            declaration_id=model.declaration_id,
            line_code=model.line_code,
            label=model.label,
            amount=model.amount or 0,
            is_calculated=model.is_calculated,
            parent_line_id=int(model.parent_line_code) if model.parent_line_code and model.parent_line_code.isdigit() else None,
            sort_order=model.sort_order,
            notes=model.notes,
        )

    def get_line(self, line_id: int) -> Optional[TaxLine]:
        model = self.session.get(TaxLineModel, line_id)
        return self._line_to_domain(model) if model else None

    def list_lines(self, declaration_id: int) -> List[TaxLine]:
        stmt = select(TaxLineModel).where(
            TaxLineModel.declaration_id == declaration_id
        ).order_by(TaxLineModel.sort_order)
        models = self.session.execute(stmt).scalars().all()
        return [self._line_to_domain(m) for m in models]

    def update_line(self, line_id: int, **kwargs) -> Result:
        model = self.session.get(TaxLineModel, line_id)
        if not model:
            return Result.failure(ValidationError(f"TaxLine {line_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._line_to_domain(model))

    def delete_line(self, line_id: int) -> Result:
        model = self.session.get(TaxLineModel, line_id)
        if not model:
            return Result.failure(ValidationError(f"TaxLine {line_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── TaxPayment CRUD ─────────────────────────────────────────────────

    def create_payment(self, payment: TaxPayment) -> Result:
        model = TaxPaymentModel(
            declaration_id=payment.declaration_id,
            tax_type=TaxTypeDB(payment.tax_type.value),
            amount=payment.amount,
            payment_date=payment.payment_date,
            due_date=payment.due_date,
            budget_account=payment.budget_account,
            payment_method=payment.payment_method,
            payment_status=TaxPaymentStatusDB(payment.payment_status.value),
            gdt_payment_code=payment.gdt_payment_code,
            bank_reference=payment.bank_reference,
            penalty_interest=payment.penalty_interest,
            notes=payment.notes,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._payment_to_domain(model))

    def get_payment(self, payment_id: int) -> Optional[TaxPayment]:
        model = self.session.get(TaxPaymentModel, payment_id)
        return self._payment_to_domain(model) if model else None

    def list_payments(self, declaration_id: Optional[int] = None) -> List[TaxPayment]:
        stmt = select(TaxPaymentModel)
        if declaration_id:
            stmt = stmt.where(TaxPaymentModel.declaration_id == declaration_id)
        stmt = stmt.order_by(TaxPaymentModel.payment_date.desc())
        models = self.session.execute(stmt).scalars().all()
        return [self._payment_to_domain(m) for m in models]

    def update_payment(self, payment_id: int, **kwargs) -> Result:
        model = self.session.get(TaxPaymentModel, payment_id)
        if not model:
            return Result.failure(ValidationError(f"TaxPayment {payment_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                if key == "payment_status" and isinstance(value, TaxPaymentStatus):
                    setattr(model, key, TaxPaymentStatusDB(value.value))
                else:
                    setattr(model, key, value)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._payment_to_domain(model))

    def delete_payment(self, payment_id: int) -> Result:
        model = self.session.get(TaxPaymentModel, payment_id)
        if not model:
            return Result.failure(ValidationError(f"TaxPayment {payment_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── TaxAdjustment CRUD ──────────────────────────────────────────────

    def create_adjustment(self, adjustment: TaxAdjustment) -> Result:
        model = TaxAdjustmentModel(
            original_declaration_id=adjustment.declaration_id,
            supplemental_declaration_id=adjustment.supplemental_declaration_id,
            adjustment_type=adjustment.adjustment_type.value,
            reason=adjustment.reason,
            original_amount=adjustment.original_amount,
            adjusted_amount=adjustment.adjusted_amount,
            difference=adjustment.difference_amount,
            late_interest=adjustment.penalty_interest,
            penalty=adjustment.penalty,
            approval_status=adjustment.status.value,
            approved_by=adjustment.reviewed_by,
            approval_date=adjustment.reviewed_at,
            created_by=adjustment.created_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._adjustment_to_domain(model))

    def get_adjustment(self, adj_id: int) -> Optional[TaxAdjustment]:
        model = self.session.get(TaxAdjustmentModel, adj_id)
        return self._adjustment_to_domain(model) if model else None

    def list_adjustments(self, declaration_id: Optional[int] = None) -> List[TaxAdjustment]:
        stmt = select(TaxAdjustmentModel)
        if declaration_id:
            stmt = stmt.where(TaxAdjustmentModel.original_declaration_id == declaration_id)
        stmt = stmt.order_by(TaxAdjustmentModel.created_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [self._adjustment_to_domain(m) for m in models]

    def update_adjustment(self, adj_id: int, **kwargs) -> Result:
        model = self.session.get(TaxAdjustmentModel, adj_id)
        if not model:
            return Result.failure(ValidationError(f"TaxAdjustment {adj_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._adjustment_to_domain(model))

    def delete_adjustment(self, adj_id: int) -> Result:
        model = self.session.get(TaxAdjustmentModel, adj_id)
        if not model:
            return Result.failure(ValidationError(f"TaxAdjustment {adj_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── TaxIncentive CRUD ───────────────────────────────────────────────

    def create_incentive(self, incentive: TaxIncentive) -> Result:
        model = TaxIncentiveModel(
            tax_type=TaxTypeDB(incentive.tax_type.value),
            incentive_type=incentive.incentive_type.value,
            code=incentive.code,
            name=incentive.name,
            legal_basis=incentive.legal_basis,
            rate_value=incentive.rate_value,
            is_percentage=incentive.is_percentage,
            valid_from=incentive.valid_from,
            valid_to=incentive.valid_to,
            max_duration_months=incentive.max_duration_months,
            eligibility_condition=incentive.eligibility_condition,
            requires_approval=incentive.requires_approval,
            status=incentive.status.value,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._incentive_to_domain(model))

    def _incentive_to_domain(self, model: TaxIncentiveModel) -> TaxIncentive:
        from domain import IncentiveStatus
        status = IncentiveStatus.ACTIVE
        for s in IncentiveStatus:
            if s.value == model.status:
                status = s
                break
        return TaxIncentive(
            id=model.id,
            tax_type=TaxType(model.tax_type.value),
            incentive_type=self._str_to_incentive_type(model.incentive_type),
            code=model.code,
            name=model.name,
            legal_basis=model.legal_basis,
            rate_value=model.rate_value or 0,
            is_percentage=model.is_percentage,
            valid_from=model.valid_from,
            valid_to=model.valid_to,
            max_duration_months=model.max_duration_months,
            eligibility_condition=model.eligibility_condition,
            requires_approval=model.requires_approval,
            status=status,
        )

    def _str_to_incentive_type(self, v: str):
        from domain import TaxIncentiveType
        for t in TaxIncentiveType:
            if t.value == v:
                return t
        return TaxIncentiveType.EXEMPTION

    def get_incentive(self, incentive_id: int) -> Optional[TaxIncentive]:
        model = self.session.get(TaxIncentiveModel, incentive_id)
        return self._incentive_to_domain(model) if model else None

    def list_incentives(self, tax_type: Optional[TaxType] = None) -> List[TaxIncentive]:
        stmt = select(TaxIncentiveModel)
        if tax_type:
            stmt = stmt.where(TaxIncentiveModel.tax_type == TaxTypeDB(tax_type.value))
        stmt = stmt.order_by(TaxIncentiveModel.code)
        models = self.session.execute(stmt).scalars().all()
        return [self._incentive_to_domain(m) for m in models]

    def update_incentive(self, incentive_id: int, **kwargs) -> Result:
        model = self.session.get(TaxIncentiveModel, incentive_id)
        if not model:
            return Result.failure(ValidationError(f"TaxIncentive {incentive_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._incentive_to_domain(model))

    def delete_incentive(self, incentive_id: int) -> Result:
        model = self.session.get(TaxIncentiveModel, incentive_id)
        if not model:
            return Result.failure(ValidationError(f"TaxIncentive {incentive_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── EInvoice CRUD ───────────────────────────────────────────────────

    def create_invoice(self, invoice: EInvoice) -> Result:
        model = EInvoiceModel(
            invoice_number=invoice.invoice_number,
            invoice_series=invoice.invoice_series,
            invoice_date=invoice.invoice_date,
            invoice_type=invoice.invoice_type.value,
            seller_tax_code=invoice.seller_tax_code,
            seller_name=invoice.seller_name,
            seller_address=invoice.seller_address,
            buyer_tax_code=invoice.buyer_tax_code,
            buyer_name=invoice.buyer_name,
            buyer_address=invoice.buyer_address,
            buyer_id=invoice.buyer_id,
            subtotal=invoice.subtotal,
            discount_amount=invoice.discount_amount,
            vat_rate=invoice.vat_rate,
            vat_amount=invoice.vat_amount,
            grand_total=invoice.grand_total,
            currency=invoice.currency,
            exchange_rate=invoice.exchange_rate,
            payment_method=invoice.payment_method,
            status=InvoiceStatusDB(invoice.status.value),
            verification_code=invoice.verification_code,
            gdt_transaction_id=invoice.gdt_transaction_id,
            signed_file_url=invoice.signed_file_url,
            digital_signature=invoice.digital_signature,
            adjustment_ref_id=invoice.adjustment_ref_id,
            adjustment_type=invoice.adjustment_type.value if invoice.adjustment_type else None,
            adjustment_reason=invoice.adjustment_reason,
            original_invoice_ref=invoice.original_invoice_ref,
            created_by=invoice.created_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._invoice_to_domain(model))

    def get_invoice(self, invoice_id: int) -> Optional[EInvoice]:
        model = self.session.get(EInvoiceModel, invoice_id)
        return self._invoice_to_domain(model) if model else None

    def list_invoices(self, status: Optional[InvoiceStatus] = None) -> List[EInvoice]:
        stmt = select(EInvoiceModel)
        if status:
            stmt = stmt.where(EInvoiceModel.status == InvoiceStatusDB(status.value))
        stmt = stmt.order_by(EInvoiceModel.invoice_date.desc())
        models = self.session.execute(stmt).scalars().all()
        return [self._invoice_to_domain(m) for m in models]

    def update_invoice(self, invoice_id: int, **kwargs) -> Result:
        model = self.session.get(EInvoiceModel, invoice_id)
        if not model:
            return Result.failure(ValidationError(f"Invoice {invoice_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                if key == "status" and isinstance(value, InvoiceStatus):
                    setattr(model, key, InvoiceStatusDB(value.value))
                else:
                    setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._invoice_to_domain(model))

    def delete_invoice(self, invoice_id: int) -> Result:
        model = self.session.get(EInvoiceModel, invoice_id)
        if not model:
            return Result.failure(ValidationError(f"Invoice {invoice_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    # ── TaxSchedule CRUD ────────────────────────────────────────────────

    def create_schedule(self, schedule: TaxSchedule) -> Result:
        model = TaxScheduleModel(
            tax_type=TaxTypeDB(schedule.tax_type.value),
            period_year=schedule.period_year,
            period_month=schedule.period_month,
            period_quarter=schedule.period_quarter,
            due_date=schedule.due_date,
            reminder_days_before=schedule.reminder_days_before,
            status=schedule.status.value,
            assigned_to=schedule.assigned_to,
            notes=schedule.notes,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._schedule_to_domain(model))

    def get_schedule(self, schedule_id: int) -> Optional[TaxSchedule]:
        model = self.session.get(TaxScheduleModel, schedule_id)
        return self._schedule_to_domain(model) if model else None

    def list_schedule(self, year: int, tax_type: Optional[TaxType] = None) -> List[TaxSchedule]:
        stmt = select(TaxScheduleModel).where(TaxScheduleModel.period_year == year)
        if tax_type:
            stmt = stmt.where(TaxScheduleModel.tax_type == TaxTypeDB(tax_type.value))
        stmt = stmt.order_by(TaxScheduleModel.due_date)
        models = self.session.execute(stmt).scalars().all()
        return [self._schedule_to_domain(m) for m in models]

    def get_upcoming_schedule(self, days_ahead: int = 7) -> List[TaxSchedule]:
        today = date.today()
        future = today + timedelta(days=days_ahead)
        stmt = select(TaxScheduleModel).where(
            and_(
                TaxScheduleModel.due_date >= today,
                TaxScheduleModel.due_date <= future,
                TaxScheduleModel.status == "pending",
            )
        ).order_by(TaxScheduleModel.due_date)
        models = self.session.execute(stmt).scalars().all()
        return [self._schedule_to_domain(m) for m in models]

    def update_schedule(self, schedule_id: int, **kwargs) -> Result:
        model = self.session.get(TaxScheduleModel, schedule_id)
        if not model:
            return Result.failure(ValidationError(f"TaxSchedule {schedule_id} not found"))
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._schedule_to_domain(model))

    def delete_schedule(self, schedule_id: int) -> Result:
        model = self.session.get(TaxScheduleModel, schedule_id)
        if not model:
            return Result.failure(ValidationError(f"TaxSchedule {schedule_id} not found"))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)
