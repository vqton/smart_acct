from datetime import datetime, timezone
import io
import os
import uuid
import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from domain.document import (
    DocumentType, DocumentStatus, DocumentCategory,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import Base
from infrastructure.models.document_models import (
    DocumentCategoryModel, DocumentModel, DocumentVersionModel,
    DocumentTypeDB, DocumentStatusDB,
)
from infrastructure.repositories.document_repository import (
    DocumentRepository, DocumentCategoryRepository,
)
from use_cases.document import DocumentUseCases


def _make_category_data(code: str = "DOC-001", name: str = "Hoa don", **kw) -> dict:
    data = {
        "code": code,
        "name": name,
        "description": "test category",
        "is_active": True,
    }
    data.update(kw)
    return data


@pytest.fixture(scope="module")
def app():
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture(scope="function")
def session(app):
    db_url = os.getenv("DATABASE_URL",
                       "postgresql+psycopg2://erp_admin:Erp%40dmin%231@172.21.208.1:5432/acct_erp")
    engine = create_engine(db_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    conn = engine.connect()
    tx = conn.begin()
    session = Session(bind=conn)
    yield session
    session.close()
    tx.rollback()
    conn.close()
    engine.dispose()


@pytest.fixture(scope="function")
def uc(app, session):
    def session_factory():
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        db_url = os.getenv("DATABASE_URL",
                           "postgresql+psycopg2://erp_admin:Erp%40dmin%231@172.21.208.1:5432/acct_erp")
        eng = create_engine(db_url, pool_pre_ping=True)
        return Session(bind=eng.connect())
    return DocumentUseCases(session_factory=lambda: session)


class TestDocumentCategoryRepository:
    def test_create_and_get(self, session):
        repo = DocumentCategoryRepository(session)
        cat = DocumentCategory(**_make_category_data())
        result = repo.create(cat)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None
        assert created.code == "DOC-001"

        fetched = repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.name == "Hoa don"

    def test_create_duplicate_code(self, session):
        repo = DocumentCategoryRepository(session)
        repo.create(DocumentCategory(**_make_category_data()))
        result = repo.create(DocumentCategory(**_make_category_data()))
        assert result.is_failure()

    def test_list(self, session):
        repo = DocumentCategoryRepository(session)
        repo.create(DocumentCategory(**_make_category_data(code="C1", name="Cat 1")))
        repo.create(DocumentCategory(**_make_category_data(code="C2", name="Cat 2")))
        cats = repo.list()
        assert len(cats) >= 2

    def test_list_active_only(self, session):
        repo = DocumentCategoryRepository(session)
        repo.create(DocumentCategory(**_make_category_data(code="A1", name="Active 1")))
        repo.create(DocumentCategory(**_make_category_data(code="A2", name="Active 2", is_active=False)))
        cats = repo.list(active_only=True)
        for c in cats:
            assert c.is_active is True

    def test_update(self, session):
        repo = DocumentCategoryRepository(session)
        result = repo.create(DocumentCategory(**_make_category_data()))
        created = result.get_data()
        result = repo.update(created.id, {"name": "Updated Name"})
        assert result.is_success()
        updated = repo.get_by_id(created.id)
        assert updated.name == "Updated Name"

    def test_delete(self, session):
        repo = DocumentCategoryRepository(session)
        result = repo.create(DocumentCategory(**_make_category_data()))
        created = result.get_data()
        result = repo.delete(created.id)
        assert result.is_success()
        assert repo.get_by_id(created.id) is None


class TestDocumentRepository:
    def test_create_and_get(self, session):
        repo = DocumentRepository(session)
        from domain.document import Document
        doc = Document(
            company_id=1,
            title="Test Document",
            file_name="test.pdf",
            file_path="/tmp/test.pdf",
            mime_type="application/pdf",
            file_size=1024,
        )
        result = repo.create(doc)
        assert result.is_success()
        created = result.get_data()
        assert created.id is not None

        fetched = repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.title == "Test Document"

    def test_get_with_versions(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Versioned Doc",
            file_name="v1.pdf",
            file_path="/tmp/v1.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()

        from domain.document import DocumentVersion
        ver = DocumentVersion(
            document_id=created.id,
            version_number=1,
            file_name="v1.pdf",
            file_path="/tmp/v1.pdf",
            change_notes="Initial upload",
        )
        repo.add_version(ver)

        fetched = repo.get_with_versions(created.id)
        assert fetched is not None

    def test_list_with_filters(self, session):
        repo = DocumentRepository(session)
        for i in range(3):
            doc = Document(
                company_id=1,
                title=f"Doc {i}",
                file_name=f"doc{i}.pdf",
                file_path=f"/tmp/doc{i}.pdf",
                document_type=DocumentType.INVOICE if i % 2 == 0 else DocumentType.CONTRACT,
                reference_type="ar_invoice" if i == 0 else None,
                reference_id=100 if i == 0 else None,
            )
            repo.create(doc)

        docs, total = repo.list(company_id=1)
        assert total >= 3

        docs, total = repo.list(company_id=1, document_type="invoice")
        assert total >= 2

    def test_list_with_search(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Invoice June 2026",
            file_name="inv_june.pdf",
            file_path="/tmp/inv_june.pdf",
            tags="invoice, june",
        )
        repo.create(doc)

        docs, total = repo.list(company_id=1, search="June")
        assert total >= 1

    def test_get_by_entity(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Entity Doc",
            file_name="entity.pdf",
            file_path="/tmp/entity.pdf",
            reference_type="ar_invoice",
            reference_id=42,
        )
        repo.create(doc)

        docs = repo.get_by_entity("ar_invoice", 42)
        assert len(docs) >= 1

    def test_update(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Original",
            file_name="orig.pdf",
            file_path="/tmp/orig.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()

        result = repo.update(created.id, {"title": "Updated"})
        assert result.is_success()
        updated = repo.get_by_id(created.id)
        assert updated.title == "Updated"

    def test_archive(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="To Archive",
            file_name="arch.pdf",
            file_path="/tmp/arch.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()

        result = repo.archive(created.id)
        assert result.is_success()
        archived = repo.get_by_id(created.id)
        assert archived.is_archived is True
        assert archived.status == DocumentStatus.ARCHIVED

    def test_archive_already_archived(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Already Archived",
            file_name="arch.pdf",
            file_path="/tmp/arch.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()
        repo.archive(created.id)
        result = repo.archive(created.id)
        assert result.is_failure()

    def test_delete(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="To Delete",
            file_name="del.pdf",
            file_path="/tmp/del.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()

        result = repo.delete(created.id)
        assert result.is_success()
        assert repo.get_by_id(created.id) is None

    def test_add_and_get_versions(self, session):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Multi Version",
            file_name="v1.pdf",
            file_path="/tmp/v1.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()

        from domain.document import DocumentVersion
        ver1 = DocumentVersion(
            document_id=created.id,
            version_number=1,
            file_name="v1.pdf",
            file_path="/tmp/v1.pdf",
        )
        repo.add_version(ver1)

        ver2 = DocumentVersion(
            document_id=created.id,
            version_number=2,
            file_name="v2.pdf",
            file_path="/tmp/v2.pdf",
            change_notes="Updated content",
        )
        repo.add_version(ver2)

        versions = repo.get_versions(created.id)
        assert len(versions) >= 2
        assert versions[0].version_number == 2


class TestDocumentUseCases:
    def test_upload_document(self, session, uc, app):
        from flask import Flask
        with app.app_context():
            class FakeFile:
                filename = "test.pdf"
                mimetype = "application/pdf"
                def save(self, path):
                    with open(path, "wb") as f:
                        f.write(b"test content")

            result = uc.upload_document(
                company_id=1,
                file=FakeFile(),
                title="Uploaded Doc",
                document_type="invoice",
                uploaded_by=1,
                tags="test",
            )
            assert result.is_success()

    def test_upload_document_empty_title(self, session, uc, app):
        with app.app_context():
            class FakeFile:
                filename = "test.pdf"
                mimetype = "application/pdf"
                def save(self, path):
                    with open(path, "wb") as f:
                        f.write(b"test content")

            result = uc.upload_document(
                company_id=1,
                file=FakeFile(),
                title="",
                document_type="invoice",
            )
            assert result.is_failure()

    def test_upload_document_no_file(self, session, uc, app):
        with app.app_context():
            result = uc.upload_document(
                company_id=1,
                file=None,
                title="No File",
                document_type="invoice",
            )
            assert result.is_failure()

    def test_get_document(self, session, uc):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Get Test",
            file_name="get.pdf",
            file_path="/tmp/get.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()
        session.flush()

        result = uc.get_document(created.id)
        assert result.is_success()
        data = result.get_data()
        assert data["title"] == "Get Test"

    def test_get_document_not_found(self, session, uc):
        result = uc.get_document(99999)
        assert result.is_failure()

    def test_list_documents(self, session, uc):
        repo = DocumentRepository(session)
        for i in range(3):
            doc = Document(
                company_id=1,
                title=f"List Doc {i}",
                file_name=f"list{i}.pdf",
                file_path=f"/tmp/list{i}.pdf",
            )
            repo.create(doc)
        session.flush()

        result = uc.list_documents(company_id=1)
        assert result.is_success()
        data = result.get_data()
        assert data["total"] >= 3

    def test_update_document(self, session, uc):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Update Me",
            file_name="update.pdf",
            file_path="/tmp/update.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()
        session.flush()

        result = uc.update_document(created.id, {"title": "Updated Title"})
        assert result.is_success()

    def test_archive_document(self, session, uc):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Archive Me",
            file_name="arch.pdf",
            file_path="/tmp/arch.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()
        session.flush()

        result = uc.archive_document(created.id)
        assert result.is_success()

    def test_delete_document(self, session, uc):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Delete Me",
            file_name="del.pdf",
            file_path="/tmp/del.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()
        session.flush()

        result = uc.delete_document(created.id)
        assert result.is_success()

    def test_get_documents_for_entity(self, session, uc):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Entity Doc",
            file_name="entity.pdf",
            file_path="/tmp/entity.pdf",
            reference_type="ar_invoice",
            reference_id=42,
        )
        repo.create(doc)
        session.flush()

        result = uc.get_documents_for_entity("ar_invoice", 42)
        assert result.is_success()
        docs = result.get_data()
        assert len(docs) >= 1

    def test_get_document_versions(self, session, uc):
        repo = DocumentRepository(session)
        doc = Document(
            company_id=1,
            title="Versioned",
            file_name="v1.pdf",
            file_path="/tmp/v1.pdf",
        )
        result = repo.create(doc)
        created = result.get_data()

        from domain.document import DocumentVersion
        ver = DocumentVersion(
            document_id=created.id,
            version_number=1,
            file_name="v1.pdf",
            file_path="/tmp/v1.pdf",
        )
        repo.add_version(ver)
        session.flush()

        result = uc.get_document_versions(created.id)
        assert result.is_success()

    def test_create_category(self, session, uc):
        result = uc.create_category(DocumentCategory(
            name="Test Category",
            code="TEST-CAT",
            description="A test category",
        ))
        assert result.is_success()

    def test_list_categories(self, session, uc):
        repo = DocumentCategoryRepository(session)
        repo.create(DocumentCategory(**_make_category_data(code="LC1", name="List Cat 1")))
        session.flush()

        result = uc.list_categories()
        assert result.is_success()
        cats = result.get_data()
        assert len(cats) >= 1

    def test_update_category(self, session, uc):
        repo = DocumentCategoryRepository(session)
        result = repo.create(DocumentCategory(**_make_category_data(code="UC1", name="Update Cat")))
        created = result.get_data()
        session.flush()

        result = uc.update_category(created.id, {"name": "Updated Cat Name"})
        assert result.is_success()

    def test_get_category(self, session, uc):
        repo = DocumentCategoryRepository(session)
        result = repo.create(DocumentCategory(**_make_category_data(code="GC1", name="Get Cat")))
        created = result.get_data()
        session.flush()

        result = uc.get_category(created.id)
        assert result.is_success()
        assert result.get_data()["name"] == "Get Cat"

    def test_delete_category(self, session, uc):
        repo = DocumentCategoryRepository(session)
        result = repo.create(DocumentCategory(**_make_category_data(code="DC1", name="Delete Cat")))
        created = result.get_data()
        session.flush()

        result = uc.delete_category(created.id)
        assert result.is_success()
