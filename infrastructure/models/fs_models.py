import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, Enum as SAEnum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from decimal import Decimal

from infrastructure.models.coa_models import Base


class FSStatementTypeDB(str, enum.Enum):
    B01_DN = "B01_DN"
    B01_DNKLT = "B01_DNKLT"
    B02_DN = "B02_DN"
    B02_DNKLT = "B02_DNKLT"
    B03_DN = "B03_DN"
    B03_DNKLT = "B03_DNKLT"
    B09_DN = "B09_DN"
    B09_DNKLT = "B09_DNKLT"
    B01a_DN = "B01a_DN"
    B02a_DN = "B02a_DN"
    B03a_DN = "B03a_DN"
    B09a_DN = "B09a_DN"
    B01b_DN = "B01b_DN"
    B02b_DN = "B02b_DN"
    B03b_DN = "B03b_DN"


class FSStatusDB(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    SIGNED = "SIGNED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"


class FSCashFlowMethodDB(str, enum.Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"


class FSStatementModel(Base):
    __tablename__ = "fs_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, default=1, nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)
    statement_type = Column(SAEnum(FSStatementTypeDB), nullable=False)
    status = Column(SAEnum(FSStatusDB), default=FSStatusDB.DRAFT, nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    cash_flow_method = Column(SAEnum(FSCashFlowMethodDB), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approval_date = Column(Date, nullable=True)
    signed_by = Column(String(100), nullable=True)
    signed_date = Column(Date, nullable=True)
    generated_by = Column(String(100), nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_consolidated = Column(Boolean, default=False, nullable=False)
    consolidation_group_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    lines = relationship("FSLineItemModel", back_populates="statement", cascade="all, delete-orphan")
    audit_logs = relationship("FSAuditLogModel", back_populates="statement", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_fs_entity_period_type", "entity_id", "period", "statement_type"),
    )

    def __repr__(self) -> str:
        return f"<FSStatementModel(id={self.id}, period={self.period}, type={self.statement_type}, status={self.status})>"


class FSLineItemModel(Base):
    __tablename__ = "fs_line_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fs_id = Column(Integer, ForeignKey("fs_statements.id", ondelete="CASCADE"), nullable=False, index=True)
    ma_so = Column(String(10), nullable=False)
    ten_chi_tieu = Column(String(500), nullable=False)
    so_thu_tu = Column(Integer, nullable=False)
    parent_ma_so = Column(String(10), nullable=True)
    current_year = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    previous_year = Column(Numeric(18, 2), nullable=True)
    is_subtotal = Column(Boolean, default=False, nullable=False)
    is_calculated = Column(Boolean, default=False, nullable=False)
    calculation_formula = Column(String(200), nullable=True)
    thuyet_minh = Column(String(1000), nullable=True)

    statement = relationship("FSStatementModel", back_populates="lines")

    __table_args__ = (
        Index("ix_fs_line_item_ma_so", "fs_id", "ma_so"),
    )

    def __repr__(self) -> str:
        return f"<FSLineItemModel(fs={self.fs_id}, ma_so={self.ma_so}, amount={self.current_year})>"


class FSAuditLogModel(Base):
    __tablename__ = "fs_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fs_id = Column(Integer, ForeignKey("fs_statements.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    user = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    details = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)

    statement = relationship("FSStatementModel", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<FSAuditLogModel(fs={self.fs_id}, action={self.action}, user={self.user})>"


class FSAccountMappingModel(Base):
    __tablename__ = "fs_account_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fs_ma_so = Column(String(10), nullable=False)
    account_code = Column(String(20), nullable=False, index=True)
    weight = Column(Numeric(5, 2), default=Decimal("1.00"), nullable=False)
    direction = Column(String(10), default="both", nullable=False)
    statement_type = Column(SAEnum(FSStatementTypeDB), nullable=False)

    __table_args__ = (
        Index("ix_fs_mapping_unique", "account_code", "fs_ma_so", "statement_type", unique=True),
    )

    def __repr__(self) -> str:
        return f"<FSAccountMappingModel(account={self.account_code}, fs={self.fs_ma_so}, type={self.statement_type})>"


class FSConsolidationGroupModel(Base):
    __tablename__ = "fs_consolidation_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    parent_entity_id = Column(Integer, nullable=False)
    consolidation_method = Column(String(20), default="full", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    members = relationship("FSConsolidationMemberModel", back_populates="group", cascade="all, delete-orphan")


class FSConsolidationMemberModel(Base):
    __tablename__ = "fs_consolidation_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("fs_consolidation_groups.id", ondelete="CASCADE"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    ownership_percentage = Column(Numeric(5, 2), default=Decimal("100.00"), nullable=False)
    consolidation_method = Column(String(20), default="full", nullable=False)

    group = relationship("FSConsolidationGroupModel", back_populates="members")
