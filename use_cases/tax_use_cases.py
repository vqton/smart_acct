from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from domain import (
    TaxType, VATCalculationMethod, DeclarationType, DeclarationStatus,
    TaxPaymentStatus, InvoiceStatus, TaxAdjustmentType, TaxIncentiveType,
    TaxDeclaration, TaxLine, TaxPayment, TaxAdjustment, TaxIncentive,
    EInvoice, EInvoiceLine, TaxSchedule,
    Result, ValidationError, VASValidationError,
)
from infrastructure.repositories.tax_repository import TaxRepository


class TaxUseCases:
    def __init__(self, session: Session):
        self.repo = TaxRepository(session)

    # ── TaxDeclaration ──────────────────────────────────────────────────

    def create_declaration(
        self,
        tax_type: TaxType,
        form_code: str,
        period_year: int,
        declaration_type: DeclarationType = DeclarationType.ORIGINAL,
        period_month: Optional[int] = None,
        period_quarter: Optional[int] = None,
        created_by: Optional[str] = None,
    ) -> Result:
        try:
            declaration = TaxDeclaration(
                tax_type=tax_type,
                declaration_type=declaration_type,
                form_code=form_code,
                period_year=period_year,
                period_month=period_month,
                period_quarter=period_quarter,
                created_by=created_by,
            )
        except VASValidationError as e:
            return Result.failure(e)
        return self.repo.create_declaration(declaration)

    def get_declaration(self, decl_id: int) -> Result:
        decl = self.repo.get_declaration(decl_id)
        if not decl:
            return Result.failure(ValidationError(f"Declaration {decl_id} not found"))
        return Result.success(decl)

    def list_declarations(
        self,
        tax_type: Optional[TaxType] = None,
        period_year: Optional[int] = None,
        status: Optional[DeclarationStatus] = None,
        declaration_type: Optional[DeclarationType] = None,
    ) -> List[TaxDeclaration]:
        return self.repo.list_declarations(
            tax_type=tax_type,
            period_year=period_year,
            status=status,
            declaration_type=declaration_type,
        )

    def update_declaration(self, decl_id: int, **kwargs) -> Result:
        return self.repo.update_declaration(decl_id, **kwargs)

    def submit_declaration(self, decl_id: int, gdt_reference: Optional[str] = None) -> Result:
        decl = self.repo.get_declaration(decl_id)
        if not decl:
            return Result.failure(ValidationError(f"Declaration {decl_id} not found"))
        if decl.status in (DeclarationStatus.SUBMITTED, DeclarationStatus.ACCEPTED):
            return Result.failure(ValidationError(f"Declaration {decl_id} already submitted"))
        return self.repo.update_declaration(
            decl_id,
            status=DeclarationStatus.SUBMITTED,
            submitted_date=date.today(),
            gdt_reference=gdt_reference,
        )

    def delete_declaration(self, decl_id: int) -> Result:
        return self.repo.delete_declaration(decl_id)

    def calculate_vat(
        self,
        decl_id: int,
        method: VATCalculationMethod = VATCalculationMethod.DEDUCTION,
        input_lines: Optional[List[Dict]] = None,
        output_lines: Optional[List[Dict]] = None,
    ) -> Result:
        decl = self.repo.get_declaration(decl_id)
        if not decl:
            return Result.failure(ValidationError(f"Declaration {decl_id} not found"))

        if method == VATCalculationMethod.DEDUCTION:
            total_output = sum(Decimal(str(l.get("amount", 0))) for l in (output_lines or []))
            total_input = sum(Decimal(str(l.get("amount", 0))) for l in (input_lines or []))
            deductible_input = total_input * Decimal("0.8")
            payable = total_output - deductible_input
        else:
            revenue = sum(Decimal(str(l.get("amount", 0))) for l in (output_lines or []))
            rate = Decimal("0.01")
            payable = revenue * rate

        payable = max(payable, Decimal("0"))
        self.repo.update_declaration(
            decl_id,
            total_payable=payable,
            status=DeclarationStatus.CALCULATED,
        )
        return Result.success({"total_payable": str(payable), "method": method.value})

    # ── TaxLine ─────────────────────────────────────────────────────────

    def create_line(
        self,
        declaration_id: int,
        line_code: str,
        label: str,
        amount: Decimal = Decimal("0.00"),
        is_calculated: bool = True,
        parent_line_id: Optional[int] = None,
        sort_order: int = 0,
        notes: Optional[str] = None,
    ) -> Result:
        try:
            line = TaxLine(
                declaration_id=declaration_id,
                line_code=line_code,
                label=label,
                amount=amount,
                is_calculated=is_calculated,
                parent_line_id=parent_line_id,
                sort_order=sort_order,
                notes=notes,
            )
        except VASValidationError as e:
            return Result.failure(e)
        return self.repo.create_line(line)

    def get_line(self, line_id: int) -> Result:
        line = self.repo.get_line(line_id)
        if not line:
            return Result.failure(ValidationError(f"TaxLine {line_id} not found"))
        return Result.success(line)

    def list_lines(self, declaration_id: int) -> List[TaxLine]:
        return self.repo.list_lines(declaration_id)

    def update_line(self, line_id: int, **kwargs) -> Result:
        return self.repo.update_line(line_id, **kwargs)

    def delete_line(self, line_id: int) -> Result:
        return self.repo.delete_line(line_id)

    # ── TaxPayment ──────────────────────────────────────────────────────

    def create_payment(
        self,
        declaration_id: int,
        amount: Decimal,
        due_date: date,
        payment_date: date,
        tax_type: TaxType,
        budget_account: str = "1701",
        payment_method: str = "etax",
        notes: Optional[str] = None,
    ) -> Result:
        try:
            payment = TaxPayment(
                declaration_id=declaration_id,
                tax_type=tax_type,
                amount=amount,
                payment_date=payment_date,
                due_date=due_date,
                budget_account=budget_account,
                payment_method=payment_method,
                notes=notes,
            )
        except VASValidationError as e:
            return Result.failure(e)
        return self.repo.create_payment(payment)

    def get_payment(self, payment_id: int) -> Result:
        payment = self.repo.get_payment(payment_id)
        if not payment:
            return Result.failure(ValidationError(f"TaxPayment {payment_id} not found"))
        return Result.success(payment)

    def list_payments(self, declaration_id: Optional[int] = None) -> List[TaxPayment]:
        return self.repo.list_payments(declaration_id=declaration_id)

    def update_payment(self, payment_id: int, **kwargs) -> Result:
        return self.repo.update_payment(payment_id, **kwargs)

    def delete_payment(self, payment_id: int) -> Result:
        return self.repo.delete_payment(payment_id)

    # ── TaxAdjustment ───────────────────────────────────────────────────

    def create_adjustment(
        self,
        declaration_id: int,
        adjustment_type: TaxAdjustmentType,
        reason: str,
        original_amount: Decimal,
        adjusted_amount: Decimal,
        supplemental_declaration_id: Optional[int] = None,
        penalty_interest: Decimal = Decimal("0.00"),
        penalty: Decimal = Decimal("0.00"),
        created_by: Optional[str] = None,
    ) -> Result:
        try:
            adjustment = TaxAdjustment(
                declaration_id=declaration_id,
                adjustment_type=adjustment_type,
                reason=reason,
                original_amount=original_amount,
                adjusted_amount=adjusted_amount,
                difference_amount=adjusted_amount - original_amount,
                penalty_interest=penalty_interest,
                penalty=penalty,
                supplemental_declaration_id=supplemental_declaration_id,
                created_by=created_by,
            )
        except VASValidationError as e:
            return Result.failure(e)
        return self.repo.create_adjustment(adjustment)

    def get_adjustment(self, adj_id: int) -> Result:
        adj = self.repo.get_adjustment(adj_id)
        if not adj:
            return Result.failure(ValidationError(f"TaxAdjustment {adj_id} not found"))
        return Result.success(adj)

    def list_adjustments(self, declaration_id: Optional[int] = None) -> List[TaxAdjustment]:
        return self.repo.list_adjustments(declaration_id=declaration_id)

    def update_adjustment(self, adj_id: int, **kwargs) -> Result:
        return self.repo.update_adjustment(adj_id, **kwargs)

    def delete_adjustment(self, adj_id: int) -> Result:
        return self.repo.delete_adjustment(adj_id)

    # ── TaxIncentive ────────────────────────────────────────────────────

    def create_incentive(
        self,
        tax_type: TaxType,
        incentive_type: TaxIncentiveType,
        code: str,
        name: str,
        legal_basis: str,
        rate_value: Decimal = Decimal("0"),
        is_percentage: bool = True,
        valid_from: date = ...,
        valid_to: Optional[date] = None,
        max_duration_months: Optional[int] = None,
        eligibility_condition: Optional[str] = None,
        requires_approval: bool = False,
    ) -> Result:
        try:
            incentive = TaxIncentive(
                tax_type=tax_type,
                incentive_type=incentive_type,
                code=code,
                name=name,
                legal_basis=legal_basis,
                rate_value=rate_value,
                is_percentage=is_percentage,
                valid_from=valid_from,
                valid_to=valid_to,
                max_duration_months=max_duration_months,
                eligibility_condition=eligibility_condition,
                requires_approval=requires_approval,
            )
        except VASValidationError as e:
            return Result.failure(e)
        return self.repo.create_incentive(incentive)

    def get_incentive(self, incentive_id: int) -> Result:
        inc = self.repo.get_incentive(incentive_id)
        if not inc:
            return Result.failure(ValidationError(f"TaxIncentive {incentive_id} not found"))
        return Result.success(inc)

    def list_incentives(self, tax_type: Optional[TaxType] = None) -> List[TaxIncentive]:
        return self.repo.list_incentives(tax_type=tax_type)

    def update_incentive(self, incentive_id: int, **kwargs) -> Result:
        return self.repo.update_incentive(incentive_id, **kwargs)

    def delete_incentive(self, incentive_id: int) -> Result:
        return self.repo.delete_incentive(incentive_id)

    # ── EInvoice ────────────────────────────────────────────────────────

    def create_invoice(self, invoice: EInvoice) -> Result:
        return self.repo.create_invoice(invoice)

    def get_invoice(self, invoice_id: int) -> Result:
        inv = self.repo.get_invoice(invoice_id)
        if not inv:
            return Result.failure(ValidationError(f"Invoice {invoice_id} not found"))
        return Result.success(inv)

    def list_invoices(self, status: Optional[InvoiceStatus] = None) -> List[EInvoice]:
        return self.repo.list_invoices(status=status)

    def update_invoice(self, invoice_id: int, **kwargs) -> Result:
        return self.repo.update_invoice(invoice_id, **kwargs)

    def update_invoice_status(self, invoice_id: int, status: InvoiceStatus, verification_code: Optional[str] = None) -> Result:
        return self.repo.update_invoice(invoice_id, status=status, verification_code=verification_code)

    def delete_invoice(self, invoice_id: int) -> Result:
        return self.repo.delete_invoice(invoice_id)

    # ── TaxSchedule ─────────────────────────────────────────────────────

    def get_tax_schedule(self, year: int, tax_type: Optional[TaxType] = None) -> List[TaxSchedule]:
        return self.repo.list_schedule(year=year, tax_type=tax_type)

    def get_schedule(self, schedule_id: int) -> Result:
        sched = self.repo.get_schedule(schedule_id)
        if not sched:
            return Result.failure(ValidationError(f"TaxSchedule {schedule_id} not found"))
        return Result.success(sched)

    def update_schedule(self, schedule_id: int, **kwargs) -> Result:
        return self.repo.update_schedule(schedule_id, **kwargs)

    def delete_schedule(self, schedule_id: int) -> Result:
        return self.repo.delete_schedule(schedule_id)

    def _generate_schedule_for_type(self, tax_type: TaxType, year: int) -> List[TaxSchedule]:
        rules = {
            TaxType.VAT_DEDUCTION: {"period": "monthly", "day_offset": 20},
            TaxType.VAT_DIRECT: {"period": "quarterly", "day_offset": 20},
            TaxType.CIT: {"period": "quarterly", "day_offset": 30},
            TaxType.PIT: {"period": "monthly", "day_offset": 20},
            TaxType.LICENSE: {"period": "annual", "day_offset": 30},
        }
        rule = rules.get(tax_type)
        if not rule:
            return []

        months = []
        if rule["period"] == "monthly":
            months = range(1, 13)
        elif rule["period"] == "quarterly":
            months = [3, 6, 9, 12]
        elif rule["period"] == "annual":
            months = [12]

        schedules = []
        for m in months:
            period_end = date(year, m, 1) + timedelta(days=32)
            period_end = period_end.replace(day=1) - timedelta(days=1)
            due = period_end + timedelta(days=rule["day_offset"])

            schedule = TaxSchedule(
                tax_type=tax_type,
                period_year=year,
                period_month=m if rule["period"] == "monthly" else None,
                period_quarter=(m // 3) if rule["period"] == "quarterly" else None,
                due_date=due,
            )
            schedules.append(schedule)
        return schedules

    def generate_schedule(self, year: int) -> Result:
        all_types = [TaxType.VAT_DEDUCTION, TaxType.VAT_DIRECT, TaxType.CIT, TaxType.PIT, TaxType.LICENSE]
        all_schedules = []
        for tt in all_types:
            all_schedules.extend(self._generate_schedule_for_type(tt, year))

        created = []
        for s in all_schedules:
            r = self.repo.create_schedule(s)
            if r.is_success():
                created.append(r.get_data())
        return Result.success({"created": len(created), "items": created})

    def get_due_reminders(self, days_ahead: int = 7) -> List[TaxSchedule]:
        return self.repo.get_upcoming_schedule(days_ahead=days_ahead)

    # ── Summary ─────────────────────────────────────────────────────────

    def get_summary(self) -> Result:
        declarations = self.repo.list_declarations()
        payments = self.repo.list_payments()
        invoices = self.repo.list_invoices()

        return Result.success({
            "total_declarations": len(declarations),
            "draft_declarations": sum(1 for d in declarations if d.status == DeclarationStatus.DRAFT),
            "submitted": sum(1 for d in declarations if d.status == DeclarationStatus.SUBMITTED),
            "accepted": sum(1 for d in declarations if d.status == DeclarationStatus.ACCEPTED),
            "total_payments": len(payments),
            "total_invoices": len(invoices),
        })
