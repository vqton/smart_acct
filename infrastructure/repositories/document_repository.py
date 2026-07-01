import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session

from domain.document import (
    Document, DocumentCategory, DocumentVersion,
    DocumentType, DocumentStatus,
)
from domain.i18n import ErrorCodes
from domain.common import VASValidationError, Result
from infrastructure.models.document_models import (
    DocumentModel, DocumentCategoryModel, DocumentVersionModel,
    DocumentTypeDB, DocumentStatusDB,
)

logger = logging.getLogger(__name__)


class DocumentCategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, category: DocumentCategory) -> Result:
        existing = self.session.query(DocumentCategoryModel).filter(
            DocumentCategoryModel.code == category.code
        ).first()
        if existing:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_CODE_DUPLICATE))
        model = DocumentCategoryModel(
            name=category.name,
            code=category.code,
            description=category.description,
            parent_id=category.parent_id,
            is_active=category.is_active,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def get_by_id(self, category_id: int) -> Optional[DocumentCategory]:
        model = self.session.query(DocumentCategoryModel).filter(
            DocumentCategoryModel.id == category_id
        ).first()
        return self._model_to_domain(model) if model else None

    def list(self, active_only: bool = False) -> List[DocumentCategory]:
        query = self.session.query(DocumentCategoryModel)
        if active_only:
            query = query.filter(DocumentCategoryModel.is_active.is_(True))
        models = query.order_by(DocumentCategoryModel.code).all()
        return [self._model_to_domain(m) for m in models]

    def update(self, category_id: int, updates: Dict[str, Any]) -> Result:
        model = self.session.query(DocumentCategoryModel).filter(
            DocumentCategoryModel.id == category_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        if "code" in updates:
            existing = self.session.query(DocumentCategoryModel).filter(
                DocumentCategoryModel.code == updates["code"],
                DocumentCategoryModel.id != category_id,
            ).first()
            if existing:
                return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_CODE_DUPLICATE))
        for key, value in updates.items():
            setattr(model, key, value)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def delete(self, category_id: int) -> Result:
        model = self.session.query(DocumentCategoryModel).filter(
            DocumentCategoryModel.id == category_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_NOT_FOUND))
        children = self.session.query(DocumentCategoryModel).filter(
            DocumentCategoryModel.parent_id == category_id
        ).count()
        if children > 0:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_HAS_CHILDREN))
        docs = self.session.query(DocumentModel).filter(
            DocumentModel.category_id == category_id
        ).count()
        if docs > 0:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_CATEGORY_HAS_DOCUMENTS))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def _model_to_domain(self, model: DocumentCategoryModel) -> DocumentCategory:
        return DocumentCategory(
            id=model.id,
            name=model.name,
            code=model.code,
            description=model.description,
            parent_id=model.parent_id,
            is_active=model.is_active,
        )


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, document: Document) -> Result:
        model = DocumentModel(
            company_id=document.company_id,
            title=document.title,
            description=document.description,
            document_type=document.document_type.value if isinstance(document.document_type, DocumentType) else document.document_type,
            status=document.status.value if isinstance(document.status, DocumentStatus) else document.status,
            category_id=document.category_id,
            reference_type=document.reference_type,
            reference_id=document.reference_id,
            file_name=document.file_name,
            file_size=document.file_size,
            mime_type=document.mime_type,
            file_path=document.file_path,
            uploaded_by=document.uploaded_by,
            version=document.version,
            tags=document.tags,
            notes=document.notes,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def get_by_id(self, document_id: int) -> Optional[Document]:
        model = self.session.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()
        return self._model_to_domain(model) if model else None

    def get_with_versions(self, document_id: int) -> Optional[Document]:
        model = self.session.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()
        return self._model_to_domain(model, include_versions=True) if model else None

    def list(self, company_id: int, document_type: Optional[str] = None,
             status: Optional[str] = None, reference_type: Optional[str] = None,
             reference_id: Optional[int] = None, search: Optional[str] = None,
             page: int = 1, per_page: int = 20) -> Tuple[List[Document], int]:
        query = self.session.query(DocumentModel).filter(
            DocumentModel.company_id == company_id
        )
        if document_type:
            query = query.filter(DocumentModel.document_type == document_type)
        if status:
            query = query.filter(DocumentModel.status == status)
        if reference_type:
            query = query.filter(DocumentModel.reference_type == reference_type)
        if reference_id is not None:
            query = query.filter(DocumentModel.reference_id == reference_id)
        if search:
            like_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    DocumentModel.title.ilike(like_pattern),
                    DocumentModel.description.ilike(like_pattern),
                    DocumentModel.tags.ilike(like_pattern),
                    DocumentModel.file_name.ilike(like_pattern),
                )
            )
        total = query.count()
        offset = (page - 1) * per_page
        models = query.order_by(DocumentModel.uploaded_at.desc()).offset(offset).limit(per_page).all()
        return [self._model_to_domain(m) for m in models], total

    def get_by_entity(self, entity_type: str, entity_id: int) -> List[Document]:
        models = self.session.query(DocumentModel).filter(
            DocumentModel.reference_type == entity_type,
            DocumentModel.reference_id == entity_id,
        ).order_by(DocumentModel.uploaded_at.desc()).all()
        return [self._model_to_domain(m) for m in models]

    def update(self, document_id: int, updates: Dict[str, Any]) -> Result:
        model = self.session.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def archive(self, document_id: int) -> Result:
        model = self.session.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        if model.is_archived:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_ALREADY_ARCHIVED))
        model.is_archived = True
        model.status = "archived"
        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._model_to_domain(model))

    def delete(self, document_id: int) -> Result:
        model = self.session.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def add_version(self, version: DocumentVersion) -> Result:
        doc = self.session.query(DocumentModel).filter(
            DocumentModel.id == version.document_id
        ).first()
        if not doc:
            return Result.failure(VASValidationError(ErrorCodes.DOCUMENT_NOT_FOUND))
        model = DocumentVersionModel(
            document_id=version.document_id,
            version_number=version.version_number,
            file_name=version.file_name,
            file_size=version.file_size,
            mime_type=version.mime_type,
            file_path=version.file_path,
            uploaded_by=version.uploaded_by,
            change_notes=version.change_notes,
        )
        self.session.add(model)
        doc.version = version.version_number
        doc.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return Result.success(self._version_to_domain(model))

    def get_versions(self, document_id: int) -> List[DocumentVersion]:
        models = self.session.query(DocumentVersionModel).filter(
            DocumentVersionModel.document_id == document_id
        ).order_by(DocumentVersionModel.version_number.desc()).all()
        return [self._version_to_domain(m) for m in models]

    def _model_to_domain(self, model: DocumentModel,
                         include_versions: bool = False) -> Document:
        doc = Document(
            id=model.id,
            company_id=model.company_id,
            title=model.title,
            description=model.description,
            document_type=DocumentType(model.document_type) if model.document_type else DocumentType.OTHER,
            status=DocumentStatus(model.status) if model.status else DocumentStatus.DRAFT,
            category_id=model.category_id,
            reference_type=model.reference_type,
            reference_id=model.reference_id,
            file_name=model.file_name,
            file_size=model.file_size,
            mime_type=model.mime_type,
            file_path=model.file_path,
            uploaded_by=model.uploaded_by,
            uploaded_at=model.uploaded_at,
            is_archived=model.is_archived,
            version=model.version,
            tags=model.tags,
            notes=model.notes,
        )
        if include_versions and hasattr(model, 'versions'):
            doc._versions = [self._version_to_domain(v) for v in model.versions]
        return doc

    def _version_to_domain(self, model: DocumentVersionModel) -> DocumentVersion:
        return DocumentVersion(
            id=model.id,
            document_id=model.document_id,
            version_number=model.version_number,
            file_name=model.file_name,
            file_size=model.file_size,
            mime_type=model.mime_type,
            file_path=model.file_path,
            uploaded_by=model.uploaded_by,
            uploaded_at=model.uploaded_at,
            change_notes=model.change_notes,
        )
