from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from infrastructure.models.coa_models import Base


class DocumentTypeDB(str, enum.Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    PAYMENT = "payment"
    CONTRACT = "contract"
    REPORT = "report"
    TAX_DECLARATION = "tax_declaration"
    OTHER = "other"


class DocumentStatusDB(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DocumentCategoryModel(Base):
    __tablename__ = "document_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    parent_id = Column(Integer, ForeignKey("document_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    children = relationship("DocumentCategoryModel", back_populates="parent",
                            lazy="selectin", cascade="all, delete-orphan",
                            remote_side=[id])
    parent = relationship("DocumentCategoryModel", back_populates="children",
                          lazy="selectin", remote_side=[parent_id])

    def __repr__(self) -> str:
        return f"<DocumentCategoryModel(id={self.id}, code='{self.code}', name='{self.name}')>"


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="draft", index=True)
    category_id = Column(Integer, ForeignKey("document_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    reference_type = Column(String(50), nullable=True, index=True)
    reference_id = Column(Integer, nullable=True, index=True)
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    mime_type = Column(String(100), nullable=False, default="application/octet-stream")
    file_path = Column(String(1000), nullable=False)
    uploaded_by = Column(Integer, nullable=True, index=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    tags = Column(String(1000), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    category = relationship("DocumentCategoryModel", lazy="selectin")
    versions = relationship("DocumentVersionModel", back_populates="document", lazy="selectin",
                            cascade="all, delete-orphan", order_by="DocumentVersionModel.version_number.desc()")

    __table_args__ = (
        Index("ix_documents_company_type", "company_id", "document_type"),
        Index("ix_documents_reference", "reference_type", "reference_id"),
        Index("ix_documents_company_status", "company_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<DocumentModel(id={self.id}, title='{self.title}', type='{self.document_type}')>"


class DocumentVersionModel(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    mime_type = Column(String(100), nullable=False, default="application/octet-stream")
    file_path = Column(String(1000), nullable=False)
    uploaded_by = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    change_notes = Column(Text, nullable=True)

    document = relationship("DocumentModel", back_populates="versions")

    __table_args__ = (
        Index("ix_doc_versions_doc_id_number", "document_id", "version_number"),
    )

    def __repr__(self) -> str:
        return f"<DocumentVersionModel(id={self.id}, doc_id={self.document_id}, v{self.version_number})>"
