# Changelog

## [Unreleased]

### Added
- Tax Module: complete domain entities for Vietnam tax compliance
  - TaxDeclaration, TaxLine, TaxPayment, TaxAdjustment, TaxIncentive
  - EInvoice, EInvoiceLine, TaxSchedule
  - Enums: TaxType, DeclarationType, DeclarationStatus, TaxAdjustmentStatus,
    InvoiceType, ScheduleStatus, IncentiveStatus, EInvoiceAdjustmentType
  - VAS validators: Decimal quantize, VAT rate 0-1 scale, period mutual exclusivity
- Infrastructure: 8 SQLAlchemy DB models (tax_declarations, tax_lines,
  tax_payments, tax_adjustments, tax_incentives, einvoices, tax_schedules)
- TaxRepository: full CRUD with domain mapping for all entities
- TaxUseCases: declaration flow, VAT calculation, schedule generation,
  due reminders, all CRUD operations
- REST API: 40 endpoints under /api/v1/tax/*
- Tests: 89 total (22 domain + 45 integration + 15 COA domain + 7 tax domain)
- GDT client stub: submit_declaration, get_declaration_status, submit_invoice,
  get_invoice_status, verify_tax_code, check_payment_status
- Signing service stub: RSA-SHA256 e-invoice signing
- Alembic migration for all tax tables
- BRD: TAX_MODULE_BRD.md with Circular 133/2016 compliance

### Changed
- Domain models hardened with VAS compliance validators
- Repository layer: all CRUD methods return domain objects (not raw DB models)
- Routes: complete JSON serialization with all fields, enum conversion
- Use cases: full CRUD for all entities, Decimal coercion in VAT calc

### Fixed
- EInvoice vat_rate: changed from 0-100 scale to 0-1 decimal scale
- EInvoiceLine vat_rate, discount_rate: 0-1 scale
- TaxAdjustment: field names aligned (declaration_id, difference_amount, status)
- Missing timestamps added to TaxLine, TaxPayment, TaxAdjustment,
  TaxIncentive, TaxSchedule
- TaxAdjustment.supplemental_declaration_id: changed to Optional
- Repository: create_payment, create_adjustment, create_schedule return domain
- Repository: list_payments, list_schedule return domain objects
