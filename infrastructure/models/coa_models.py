from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
import enum


class Base(DeclarativeBase):
    pass


class AccountingRegime(str, enum.Enum):
    TT99_2025 = "tt99_2025"
    TT133_2016 = "tt133_2016"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class COAModel(Base):
    __tablename__ = "chart_of_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False)
    account_type = Column(String(50), nullable=False)
    regime = Column(SAEnum(AccountingRegime), default=AccountingRegime.TT99_2025, nullable=False)
    vas_compliant = Column(Boolean, default=True, nullable=False)
    drcr_direction = Column(String(10), nullable=False)
    level = Column(Integer, default=1, nullable=False)
    status = Column(SAEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    currency = Column(String(10), default="VND", nullable=False)
    unit = Column(String(10), default="VND", nullable=False)
    parent_code = Column(String(20), ForeignKey("chart_of_accounts.code"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    children = relationship("COAModel", back_populates="parent", remote_side=[code], lazy="selectin")
    parent = relationship("COAModel", back_populates="children", lazy="selectin")

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"<COAModel(code='{self.code}', name='{self.name}')>"


AccountModel = COAModel


class IFRSMappingModel(Base):
    __tablename__ = "ifrs_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vas_account_code = Column(String(20), nullable=False, index=True)
    ifrs_account_code = Column(String(20), nullable=False)
    mapping_type = Column(String(20), default="1:1", nullable=False)
    expression = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def __repr__(self) -> str:
        return f"<IFRSMappingModel(vas={self.vas_account_code}, ifrs={self.ifrs_account_code})>"


class COAVersionModel(Base):
    __tablename__ = "coa_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot = Column(JSON, nullable=False)
    account_count = Column(Integer, nullable=False)
    created_by = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<COAVersionModel(id={self.id}, accounts={self.account_count})>"
