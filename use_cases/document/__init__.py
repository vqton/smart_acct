import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from domain.document import (
    Document, DocumentCategory, DocumentVersion,
    DocumentType, DocumentStatus,
)
from domain.common import VASValidationError, Result
from domain.i18n import ErrorCodes
from infrastructure.repositories.document_repository import (
    DocumentRepository, DocumentCategoryRepository,
)

logger = logging.getLogger(__name__)

UPLOAD_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


class DocumentUseCases:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def _get_repos(self, session):
        return (
            DocumentRepository(session),
            DocumentCategoryRepository(session),
        )

    def _save_file(self, file, company_id: int, document_type: str) -> Dict[str, Any]:
        upload_dir = os.path.join(UPLOAD_BASE, str(company_id), document_type)
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(file.filename)[1] if file.filename else ""
        new_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        return {
            "file_path": file_path,
            "file_name": file.filename or new_filename,
            "file_size": os.path.getsize(file_path),
            "mime_type": file.mimetype or "application/octet-stream",
        }

    def upload_document(self, company_id: int, file, title: str,
                        document_type: str = "other",
                        reference_type: Optional[str] = None,
                        reference_id: Optional[int] = None,
                        uploaded_by: Optional[int] = None,
                        tags: Optional[str] = None,
                        category_id: Optional[int] = None,
                        description: Optional[str] = None,
                        notes: Optional[str] = None) -> Result:
        session = self._session_factory()
        try:
            if not title or not title.strip():
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_TITLE_EMPTY))
            if not file:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_FILE_REQUIRED))

            try:
                doc_type = DocumentType(document_type)
            except ValueError:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_INVALID_TYPE))

            file_info = self._save_file(file, company_id, document_type)

            doc = Document(
                company_id=company_id,
                title=title.strip(),
                description=description,
                document_type=doc_type,
                category_id=category_id,
                reference_type=reference_type,
                reference_id=reference_id,
                file_name=file_info["file_name"],
                file_size=file_info["file_size"],
                mime_type=file_info["mime_type"],
                file_path=file_info["file_path"],
                uploaded_by=uploaded_by,
                tags=tags,
                notes=notes,
            )

            repo = DocumentRepository(session)
            result = repo.create(doc)
            if result.is_failure():
                session.rollback()
                return result

            session.commit()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Upload document error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def upload_new_version(self, document_id: int, file, change_notes: Optional[str] = None,
                           uploaded_by: Optional[int] = None) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            doc = repo.get_by_id(document_id)
            if not doc:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
            if not file:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_FILE_REQUIRED))

            file_info = self._save_file(file, doc.company_id, doc.document_type.value)

            new_version = DocumentVersion(
                document_id=document_id,
                version_number=doc.version + 1,
                file_name=file_info["file_name"],
                file_size=file_info["file_size"],
                mime_type=file_info["mime_type"],
                file_path=file_info["file_path"],
                uploaded_by=uploaded_by,
                change_notes=change_notes,
            )

            result = repo.add_version(new_version)
            if result.is_failure():
                session.rollback()
                return result

            session.commit()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Upload version error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def get_document(self, document_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            doc = repo.get_with_versions(document_id)
            if not doc:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
            session.close()
            versions = getattr(doc, '_versions', [])
            return Result.success({
                "id": doc.id,
                "company_id": doc.company_id,
                "title": doc.title,
                "description": doc.description,
                "document_type": doc.document_type.value if hasattr(doc.document_type, 'value') else doc.document_type,
                "status": doc.status.value if hasattr(doc.status, 'value') else doc.status,
                "category_id": doc.category_id,
                "reference_type": doc.reference_type,
                "reference_id": doc.reference_id,
                "file_name": doc.file_name,
                "file_size": doc.file_size,
                "mime_type": doc.mime_type,
                "file_path": doc.file_path,
                "uploaded_by": doc.uploaded_by,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                "is_archived": doc.is_archived,
                "version": doc.version,
                "tags": doc.tags,
                "notes": doc.notes,
                "versions": [{
                    "id": v.id,
                    "version_number": v.version_number,
                    "file_name": v.file_name,
                    "file_size": v.file_size,
                    "mime_type": v.mime_type,
                    "uploaded_by": v.uploaded_by,
                    "uploaded_at": v.uploaded_at.isoformat() if v.uploaded_at else None,
                    "change_notes": v.change_notes,
                } for v in versions],
            })
        except Exception as e:
            logger.exception(f"Get document error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def list_documents(self, company_id: int, document_type: Optional[str] = None,
                       status: Optional[str] = None,
                       reference_type: Optional[str] = None,
                       reference_id: Optional[int] = None,
                       search: Optional[str] = None,
                       page: int = 1, per_page: int = 20) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            docs, total = repo.list(
                company_id, document_type=document_type, status=status,
                reference_type=reference_type, reference_id=reference_id,
                search=search, page=page, per_page=per_page,
            )
            session.close()
            return Result.success({
                "items": [{
                    "id": d.id,
                    "title": d.title,
                    "description": d.description,
                    "document_type": d.document_type.value if hasattr(d.document_type, 'value') else d.document_type,
                    "status": d.status.value if hasattr(d.status, 'value') else d.status,
                    "category_id": d.category_id,
                    "reference_type": d.reference_type,
                    "reference_id": d.reference_id,
                    "file_name": d.file_name,
                    "file_size": d.file_size,
                    "mime_type": d.mime_type,
                    "uploaded_by": d.uploaded_by,
                    "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                    "is_archived": d.is_archived,
                    "version": d.version,
                    "tags": d.tags,
                } for d in docs],
                "total": total,
                "page": page,
                "per_page": per_page,
            })
        except Exception as e:
            logger.exception(f"List documents error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def update_document(self, document_id: int, updates: Dict[str, Any]) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            allowed = {"title", "description", "category_id", "tags", "notes", "status"}
            filtered = {k: v for k, v in updates.items() if k in allowed and v is not None}
            if not filtered:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
            if "title" in filtered:
                if not filtered["title"].strip():
                    return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_TITLE_EMPTY))
                filtered["title"] = filtered["title"].strip()
            result = repo.update(document_id, filtered)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update document error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def delete_document(self, document_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            doc = repo.get_by_id(document_id)
            if not doc:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
            file_path = doc.file_path
            result = repo.delete(document_id)
            if result.is_success():
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Delete document error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def archive_document(self, document_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            result = repo.archive(document_id)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Archive document error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def get_documents_for_entity(self, entity_type: str, entity_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            docs = repo.get_by_entity(entity_type, entity_id)
            session.close()
            return Result.success([{
                "id": d.id,
                "title": d.title,
                "document_type": d.document_type.value if hasattr(d.document_type, 'value') else d.document_type,
                "status": d.status.value if hasattr(d.status, 'value') else d.status,
                "file_name": d.file_name,
                "file_size": d.file_size,
                "mime_type": d.mime_type,
                "uploaded_by": d.uploaded_by,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                "version": d.version,
            } for d in docs])
        except Exception as e:
            logger.exception(f"Get entity documents error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    def get_document_versions(self, document_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            doc = repo.get_by_id(document_id)
            if not doc:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
            versions = repo.get_versions(document_id)
            session.close()
            return Result.success([{
                "id": v.id,
                "version_number": v.version_number,
                "file_name": v.file_name,
                "file_size": v.file_size,
                "mime_type": v.mime_type,
                "uploaded_by": v.uploaded_by,
                "uploaded_at": v.uploaded_at.isoformat() if v.uploaded_at else None,
                "change_notes": v.change_notes,
            } for v in versions])
        except Exception as e:
            logger.exception(f"Get document versions error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_VERSION_NOT_FOUND))
        finally:
            session.close()

    def get_document_file_path(self, document_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentRepository(session)
            doc = repo.get_by_id(document_id)
            if not doc:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
            session.close()
            return Result.success({
                "file_path": doc.file_path,
                "file_name": doc.file_name,
                "mime_type": doc.mime_type,
            })
        except Exception as e:
            logger.exception(f"Get document file path error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        finally:
            session.close()

    # ── Category CRUD ───────────────────────────────────────────────────

    def create_category(self, req: DocumentCategory) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentCategoryRepository(session)
            result = repo.create(req)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Create category error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        finally:
            session.close()

    def update_category(self, category_id: int, updates: Dict[str, Any]) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentCategoryRepository(session)
            result = repo.update(category_id, updates)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Update category error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        finally:
            session.close()

    def list_categories(self, active_only: bool = False) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentCategoryRepository(session)
            categories = repo.list(active_only)
            session.close()
            return Result.success([{
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "description": c.description,
                "parent_id": c.parent_id,
                "is_active": c.is_active,
            } for c in categories])
        except Exception as e:
            logger.exception(f"List categories error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        finally:
            session.close()

    def get_category(self, category_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentCategoryRepository(session)
            cat = repo.get_by_id(category_id)
            if not cat:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
            session.close()
            return Result.success({
                "id": cat.id,
                "name": cat.name,
                "code": cat.code,
                "description": cat.description,
                "parent_id": cat.parent_id,
                "is_active": cat.is_active,
            })
        except Exception as e:
            logger.exception(f"Get category error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        finally:
            session.close()

    def delete_category(self, category_id: int) -> Result:
        session = self._session_factory()
        try:
            repo = DocumentCategoryRepository(session)
            result = repo.delete(category_id)
            if result.is_success():
                session.commit()
            else:
                session.rollback()
            return result
        except VASValidationError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            logger.exception(f"Delete category error: {e}")
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        finally:
            session.close()
