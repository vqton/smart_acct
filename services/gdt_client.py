"""GDT (General Department of Taxation) API client stub for Vietnam eTax."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, date

from domain import Result, EInvoice, ValidationError

logger = logging.getLogger(__name__)

DECLARATION_STATUSES = {
    "draft": "DRAFT",
    "submitted": "SUBMITTED",
    "processing": "PROCESSING",
    "accepted": "ACCEPTED",
    "rejected": "REJECTED",
    "cancelled": "CANCELLED",
}

INVOICE_STATUSES = {
    "pending": "PENDING_VERIFICATION",
    "verified": "VERIFIED",
    "rejected": "REJECTED",
    "cancelled": "CANCELLED",
}


class GDTClient:
    """Stub client for Vietnam General Department of Taxation eTax API.

    Connects to GDT's electronic tax processing system for declaration
    submission, invoice verification, and tax code validation.
    """

    def __init__(
        self,
        base_url: str = "https://etax.gdt.gov.vn/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_key = api_key
        logger.info(
            "GDTClient initialized with base_url=%s, timeout=%d, max_retries=%d",
            self.base_url, self.timeout, self.max_retries,
        )

    def submit_declaration(
        self,
        tax_code: str,
        form_code: str,
        period_year: int,
        period_month: Optional[int] = None,
        period_quarter: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Result:
        """Submit a tax declaration to GDT eTax system."""
        logger.info(
            "Submitting declaration: tax_code=%s, form=%s, period=%s-%s",
            tax_code, form_code, period_year, period_month or period_quarter or "N/A",
        )
        if not tax_code:
            return Result.failure(ValidationError("tax_code is required"))
        return Result.success({
            "submission_id": f"GDT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{tax_code[:5]}",
            "status": DECLARATION_STATUSES["submitted"],
            "submitted_at": datetime.utcnow().isoformat(),
            "form_code": form_code,
        })

    def get_declaration_status(self, submission_id: str) -> Result:
        """Check the processing status of a submitted declaration."""
        logger.info("Checking declaration status: submission_id=%s", submission_id)
        if not submission_id:
            return Result.failure(ValidationError("submission_id is required"))
        return Result.success({
            "submission_id": submission_id,
            "status": DECLARATION_STATUSES["accepted"],
            "accepted_at": datetime.utcnow().isoformat(),
            "gdt_reference": f"REF-{submission_id[-8:]}",
        })

    def submit_invoice(self, invoice: EInvoice) -> Result:
        """Submit an e-invoice to GDT for verification and coding."""
        logger.info(
            "Submitting invoice: series=%s, number=%s, seller=%s",
            invoice.invoice_series, invoice.invoice_number, invoice.seller_tax_code,
        )
        return Result.success({
            "transaction_id": f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "invoice_number": invoice.invoice_number,
            "invoice_series": invoice.invoice_series,
            "status": INVOICE_STATUSES["pending"],
            "submitted_at": datetime.utcnow().isoformat(),
        })

    def get_invoice_status(self, transaction_id: str) -> Result:
        """Check verification status of a submitted e-invoice."""
        logger.info("Checking invoice status: transaction_id=%s", transaction_id)
        if not transaction_id:
            return Result.failure(ValidationError("transaction_id is required"))
        return Result.success({
            "transaction_id": transaction_id,
            "status": INVOICE_STATUSES["verified"],
            "verification_code": f"VC-{transaction_id[-8:]}",
            "verified_at": datetime.utcnow().isoformat(),
        })

    def verify_tax_code(self, tax_code: str) -> Result:
        """Verify a tax code against GDT's registered taxpayer database."""
        logger.info("Verifying tax code: %s", tax_code)
        if not tax_code or len(tax_code) < 10:
            return Result.failure(ValidationError(f"Invalid tax code format: {tax_code}"))
        return Result.success({
            "tax_code": tax_code,
            "is_valid": True,
            "taxpayer_name": f"CONG TY TNHH {tax_code[:5].upper()}",
            "tax_office": "CUC THUE TP. HA NOI",
            "registered_date": "2020-01-01",
            "status": "ACTIVE",
        })

    def check_payment_status(
        self,
        tax_code: str,
        declaration_id: str,
        period_year: int,
    ) -> Result:
        """Check payment status for a tax declaration."""
        logger.info(
            "Checking payment: tax_code=%s, declaration=%s, year=%d",
            tax_code, declaration_id, period_year,
        )
        if not tax_code:
            return Result.failure(ValidationError("tax_code is required"))
        return Result.success({
            "tax_code": tax_code,
            "declaration_id": declaration_id,
            "period_year": period_year,
            "payment_status": "PAID",
            "total_paid": 1_500_000.00,
            "paid_date": date.today().isoformat(),
            "outstanding_balance": 0.00,
        })
