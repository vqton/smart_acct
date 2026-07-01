from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from enum import Enum

from domain.i18n import ErrorCodes
from domain.common import VASValidationError


class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    PAYMENT = "payment"
    CONTRACT = "contract"
    REPORT = "report"
    TAX_DECLARATION = "tax_declaration"
    OTHER = "other"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DocumentCategory(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NAME_EMPTY)
        return v.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_CODE_EMPTY)
        return v.strip()


class Document(BaseModel):
    id: Optional[int] = None
    company_id: int
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    document_type: DocumentType = DocumentType.OTHER
    status: DocumentStatus = DocumentStatus.DRAFT
    category_id: Optional[int] = None
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    file_name: str = Field(..., min_length=1, max_length=500)
    file_size: int = 0
    mime_type: str = Field(default="application/octet-stream", max_length=100)
    file_path: str = Field(..., max_length=1000)
    uploaded_by: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_archived: bool = False
    version: int = 1
    tags: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_TITLE_EMPTY)
        if len(v) > 500:
            raise VASValidationError(ErrorCodes.DOCUMENT_TITLE_EMPTY)
        return v.strip()

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_REQUIRED)
        return v.strip()

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v < 0:
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_TOO_LARGE)
        MAX_SIZE = 50 * 1024 * 1024
        if v > MAX_SIZE:
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_TOO_LARGE)
        return v


class DocumentVersion(BaseModel):
    id: Optional[int] = None
    document_id: int
    version_number: int = 1
    file_name: str = Field(..., min_length=1, max_length=500)
    file_size: int = 0
    mime_type: str = Field(default="application/octet-stream", max_length=100)
    file_path: str = Field(..., max_length=1000)
    uploaded_by: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    change_notes: Optional[str] = Field(None, max_length=2000)

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_REQUIRED)
        return v.strip()

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v < 0:
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_TOO_LARGE)
        MAX_SIZE = 50 * 1024 * 1024
        if v > MAX_SIZE:
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_TOO_LARGE)
        return v


class DocumentAttachment(BaseModel):
    id: Optional[int] = None
    document_id: int
    entity_type: str = Field(..., max_length=50)
    entity_id: int
    file_name: str = Field(..., min_length=1, max_length=500)
    file_size: int = 0
    mime_type: str = Field(default="application/octet-stream", max_length=100)
    file_path: str = Field(..., max_length=1000)
    uploaded_by: Optional[int] = None

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_INVALID_TYPE)
        return v.strip()

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        if not v.strip():
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_REQUIRED)
        return v.strip()

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v < 0:
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_TOO_LARGE)
        MAX_SIZE = 50 * 1024 * 1024
        if v > MAX_SIZE:
            raise VASValidationError(ErrorCodes.DOCUMENT_FILE_TOO_LARGE)
        return v
