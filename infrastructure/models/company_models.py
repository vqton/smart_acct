from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from infrastructure.models.coa_models import Base


class CompDocumentTypeDB(str, enum.Enum):
    AR_INVOICE = "ar_invoice"
    AP_INVOICE = "ap_invoice"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"
    JOURNAL_ENTRY = "journal_entry"
    PURCHASE_ORDER = "purchase_order"
    SALES_ORDER = "sales_order"
    INVENTORY_RECEIPT = "inventory_receipt"
    INVENTORY_ISSUE = "inventory_issue"
    PAYMENT = "payment"
    RECEIPT = "receipt"


class SetupSectionDB(str, enum.Enum):
    COMPANY_INFO = "company_info"
    FISCAL_YEAR = "fiscal_year"
    CURRENCY = "currency"
    COA = "coa"
    OPENING_BALANCES = "opening_balances"
    DEPARTMENTS = "departments"
    WAREHOUSES = "warehouses"
    EMPLOYEES = "employees"
    CUSTOMERS = "customers"
    VENDORS = "vendors"
    TAX_RATES = "tax_rates"
    NUMBERING_RULES = "numbering_rules"
    USER_PERMISSIONS = "user_permissions"


class CompanyModel(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    tax_code = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    business_reg_number = Column(String(50), nullable=True)
    date_format = Column(String(20), nullable=False, default="DD/MM/YYYY")
    currency_code = Column(String(3), nullable=False, default="VND")
    fiscal_year_start_month = Column(Integer, nullable=False, default=1)
    accounting_regime = Column(String(10), nullable=False, default="TT99")
    locale = Column(String(10), nullable=False, default="vi")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    fiscal_years = relationship("FiscalYearConfigModel", back_populates="company", lazy="selectin",
                                cascade="all, delete-orphan")
    numbering_rules = relationship("NumberingRuleModel", back_populates="company", lazy="selectin",
                                   cascade="all, delete-orphan")
    setup_checklist = relationship("SetupChecklistItemModel", back_populates="company", lazy="selectin",
                                   cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CompanyModel(id={self.id}, name='{self.name}')>"


class FiscalYearConfigModel(Base):
    __tablename__ = "company_fiscal_years"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)

    company = relationship("CompanyModel", back_populates="fiscal_years")

    __table_args__ = (
        UniqueConstraint("company_id", "fiscal_year", name="uq_company_fiscal_year"),
        Index("ix_fiscal_year_company", "company_id", "fiscal_year"),
    )

    def __repr__(self) -> str:
        return f"<FiscalYearConfigModel(id={self.id}, year={self.fiscal_year})>"


class NumberingRuleModel(Base):
    __tablename__ = "company_numbering_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(SAEnum(CompDocumentTypeDB), nullable=False)
    prefix = Column(String(10), nullable=False, default="")
    suffix = Column(String(10), nullable=False, default="")
    next_number = Column(Integer, nullable=False, default=1)
    pad_length = Column(Integer, nullable=False, default=6)
    fiscal_year = Column(Integer, nullable=False)

    company = relationship("CompanyModel", back_populates="numbering_rules")

    __table_args__ = (
        UniqueConstraint("company_id", "document_type", "fiscal_year", name="uq_company_doc_type_fiscal_year"),
        Index("ix_numbering_rule_company", "company_id", "document_type", "fiscal_year"),
    )

    def __repr__(self) -> str:
        return f"<NumberingRuleModel(id={self.id}, doc_type='{self.document_type}', year={self.fiscal_year})>"


class SetupChecklistItemModel(Base):
    __tablename__ = "company_setup_checklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    section = Column(SAEnum(SetupSectionDB), nullable=False)
    label = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    company = relationship("CompanyModel", back_populates="setup_checklist")

    __table_args__ = (
        UniqueConstraint("company_id", "section", name="uq_company_setup_section"),
        Index("ix_setup_checklist_company", "company_id", "section"),
    )

    def __repr__(self) -> str:
        return f"<SetupChecklistItemModel(id={self.id}, section='{self.section}')>"
