from decimal import Decimal
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError as PydanticValidationError

from domain.document import (
    DocumentType, DocumentStatus,
    DocumentCategory, Document, DocumentVersion, DocumentAttachment,
)
from domain.common import VASValidationError


class TestDocumentType:
    def test_enum_values(self):
        assert DocumentType.INVOICE.value == "invoice"
        assert DocumentType.RECEIPT.value == "receipt"
        assert DocumentType.PAYMENT.value == "payment"
        assert DocumentType.CONTRACT.value == "contract"
        assert DocumentType.REPORT.value == "report"
        assert DocumentType.TAX_DECLARATION.value == "tax_declaration"
        assert DocumentType.OTHER.value == "other"


class TestDocumentStatus:
    def test_enum_values(self):
        assert DocumentStatus.DRAFT.value == "draft"
        assert DocumentStatus.PENDING.value == "pending"
        assert DocumentStatus.APPROVED.value == "approved"
        assert DocumentStatus.REJECTED.value == "rejected"
        assert DocumentStatus.ARCHIVED.value == "archived"


class TestDocumentCategory:
    def test_valid_category_all_fields(self):
        cat = DocumentCategory(
            name="Hoa don",
            code="INVOICE",
            description="Hoa don ban hang",
            parent_id=None,
            is_active=True,
        )
        assert cat.name == "Hoa don"
        assert cat.code == "INVOICE"
        assert cat.description == "Hoa don ban hang"
        assert cat.is_active is True

    def test_valid_category_minimal(self):
        cat = DocumentCategory(name="Hop dong", code="CONTRACT")
        assert cat.is_active is True
        assert cat.description is None
        assert cat.parent_id is None

    def test_name_empty_raises(self):
        with pytest.raises(VASValidationError):
            DocumentCategory(name="", code="TEST")

    def test_name_whitespace_only_raises(self):
        with pytest.raises(VASValidationError):
            DocumentCategory(name="   ", code="TEST")

    def test_code_empty_raises(self):
        with pytest.raises(VASValidationError):
            DocumentCategory(name="Test", code="")

    def test_code_whitespace_only_raises(self):
        with pytest.raises(VASValidationError):
            DocumentCategory(name="Test", code="   ")


class TestDocument:
    def test_valid_document_all_fields(self):
        doc = Document(
            company_id=1,
            title="Hoa don so 001",
            description="Hoa don ban hang thang 6",
            document_type=DocumentType.INVOICE,
            status=DocumentStatus.APPROVED,
            category_id=1,
            reference_type="ar_invoice",
            reference_id=100,
            file_name="invoice_001.pdf",
            file_size=102400,
            mime_type="application/pdf",
            file_path="/uploads/1/invoice/uuid.pdf",
            uploaded_by=1,
            tags="invoice, june",
            notes="Da gui cho khach hang",
        )
        assert doc.company_id == 1
        assert doc.title == "Hoa don so 001"
        assert doc.document_type == DocumentType.INVOICE
        assert doc.status == DocumentStatus.APPROVED
        assert doc.file_name == "invoice_001.pdf"
        assert doc.file_size == 102400
        assert doc.version == 1

    def test_valid_document_minimal(self):
        doc = Document(
            company_id=1,
            title="File dinh kem",
            file_name="file.pdf",
            file_path="/uploads/1/other/uuid.pdf",
        )
        assert doc.document_type == DocumentType.OTHER
        assert doc.status == DocumentStatus.DRAFT
        assert doc.is_archived is False
        assert doc.version == 1
        assert doc.file_size == 0

    def test_title_empty_raises(self):
        with pytest.raises(VASValidationError):
            Document(
                company_id=1,
                title="",
                file_name="file.pdf",
                file_path="/path/file.pdf",
            )

    def test_title_whitespace_only_raises(self):
        with pytest.raises(VASValidationError):
            Document(
                company_id=1,
                title="   ",
                file_name="file.pdf",
                file_path="/path/file.pdf",
            )

    def test_file_name_empty_raises(self):
        with pytest.raises(VASValidationError):
            Document(
                company_id=1,
                title="Test",
                file_name="",
                file_path="/path/file.pdf",
            )

    def test_file_name_whitespace_only_raises(self):
        with pytest.raises(VASValidationError):
            Document(
                company_id=1,
                title="Test",
                file_name="   ",
                file_path="/path/file.pdf",
            )

    def test_file_size_negative_raises(self):
        with pytest.raises(VASValidationError):
            Document(
                company_id=1,
                title="Test",
                file_name="file.pdf",
                file_size=-1,
                file_path="/path/file.pdf",
            )

    def test_file_size_exceeds_max_raises(self):
        with pytest.raises(VASValidationError):
            Document(
                company_id=1,
                title="Test",
                file_name="file.pdf",
                file_size=51 * 1024 * 1024,
                file_path="/path/file.pdf",
            )

    def test_file_size_at_max_allowed(self):
        doc = Document(
            company_id=1,
            title="Test",
            file_name="file.pdf",
            file_size=50 * 1024 * 1024,
            file_path="/path/file.pdf",
        )
        assert doc.file_size == 50 * 1024 * 1024

    def test_default_timestamps(self):
        doc = Document(
            company_id=1,
            title="Test",
            file_name="file.pdf",
            file_path="/path/file.pdf",
        )
        assert doc.uploaded_at is not None

    def test_document_type_enum_conversion(self):
        doc = Document(
            company_id=1,
            title="Test",
            document_type=DocumentType.CONTRACT,
            file_name="contract.pdf",
            file_path="/path/contract.pdf",
        )
        assert doc.document_type == DocumentType.CONTRACT
        assert doc.document_type.value == "contract"


class TestDocumentVersion:
    def test_valid_version_all_fields(self):
        ver = DocumentVersion(
            document_id=1,
            version_number=2,
            file_name="v2_invoice.pdf",
            file_size=204800,
            mime_type="application/pdf",
            file_path="/uploads/1/invoice/uuid_v2.pdf",
            uploaded_by=1,
            change_notes="Da sua so tien",
        )
        assert ver.document_id == 1
        assert ver.version_number == 2
        assert ver.file_name == "v2_invoice.pdf"
        assert ver.change_notes == "Da sua so tien"

    def test_valid_version_minimal(self):
        ver = DocumentVersion(
            document_id=1,
            file_name="file.pdf",
            file_path="/path/file.pdf",
        )
        assert ver.version_number == 1
        assert ver.file_size == 0
        assert ver.change_notes is None

    def test_file_name_empty_raises(self):
        with pytest.raises(VASValidationError):
            DocumentVersion(
                document_id=1,
                file_name="",
                file_path="/path/file.pdf",
            )

    def test_file_size_negative_raises(self):
        with pytest.raises(VASValidationError):
            DocumentVersion(
                document_id=1,
                file_name="file.pdf",
                file_size=-1,
                file_path="/path/file.pdf",
            )

    def test_file_size_exceeds_max_raises(self):
        with pytest.raises(VASValidationError):
            DocumentVersion(
                document_id=1,
                file_name="file.pdf",
                file_size=51 * 1024 * 1024,
                file_path="/path/file.pdf",
            )


class TestDocumentAttachment:
    def test_valid_attachment(self):
        att = DocumentAttachment(
            document_id=1,
            entity_type="ar_invoice",
            entity_id=100,
            file_name="attachment.pdf",
            file_size=51200,
            mime_type="application/pdf",
            file_path="/uploads/attachments/uuid.pdf",
            uploaded_by=1,
        )
        assert att.document_id == 1
        assert att.entity_type == "ar_invoice"
        assert att.entity_id == 100

    def test_entity_type_empty_raises(self):
        with pytest.raises(VASValidationError):
            DocumentAttachment(
                document_id=1,
                entity_type="",
                entity_id=1,
                file_name="file.pdf",
                file_path="/path/file.pdf",
            )

    def test_file_name_empty_raises(self):
        with pytest.raises(VASValidationError):
            DocumentAttachment(
                document_id=1,
                entity_type="ar_invoice",
                entity_id=1,
                file_name="",
                file_path="/path/file.pdf",
            )
