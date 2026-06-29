from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain import IFRSMapping, Result, VASValidationError
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import IFRSMappingModel
from infrastructure.repositories.coa_repository import COARepository


class COAIFRSUseCase:
    def __init__(self, session: Session):
        self.session = session
        self.repo = COARepository(session)

    def _to_domain(self, m: IFRSMappingModel) -> dict:
        return {
            "id": m.id,
            "vas_account_code": m.vas_account_code,
            "ifrs_account_code": m.ifrs_account_code,
            "mapping_type": m.mapping_type,
            "expression": m.expression,
            "description": m.description,
            "created_by": m.created_by,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }

    def create_mapping(self, vas_account_code: str, ifrs_account_code: str,
                       mapping_type: str = "1:1", expression: Optional[str] = None,
                       description: Optional[str] = None,
                       created_by: Optional[str] = None) -> Result:
        domain = IFRSMapping(
            vas_account_code=vas_account_code,
            ifrs_account_code=ifrs_account_code,
            mapping_type=mapping_type,
            expression=expression,
            description=description,
            created_by=created_by,
        )

        existing = self.session.execute(
            select(IFRSMappingModel).where(
                IFRSMappingModel.vas_account_code == vas_account_code,
                IFRSMappingModel.ifrs_account_code == ifrs_account_code,
            )
        ).scalar_one_or_none()
        if existing:
            return Result.failure(VASValidationError(
                ErrorCodes.IFRS_MAPPING_EXISTS, source=vas_account_code, target=ifrs_account_code
            ))

        vas_exists = self.repo.get_by_code(vas_account_code)
        if not vas_exists:
            return Result.failure(VASValidationError(ErrorCodes.VAS_ACCOUNT_NOT_FOUND, code=vas_account_code))

        model = IFRSMappingModel(
            vas_account_code=domain.vas_account_code,
            ifrs_account_code=domain.ifrs_account_code,
            mapping_type=domain.mapping_type,
            expression=domain.expression,
            description=domain.description,
            created_by=domain.created_by,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success(self._to_domain(model))

    def list_mappings(self, vas_account_code: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[dict]:
        stmt = select(IFRSMappingModel).order_by(IFRSMappingModel.vas_account_code)
        if vas_account_code:
            stmt = stmt.where(IFRSMappingModel.vas_account_code == vas_account_code)
        stmt = stmt.limit(limit).offset(offset)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def get_mapping(self, mapping_id: int) -> Result:
        model = self.session.get(IFRSMappingModel, mapping_id)
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.IFRS_MAPPING_NOT_FOUND, mapping_id=mapping_id))
        return Result.success(self._to_domain(model))

    def delete_mapping(self, mapping_id: int) -> Result:
        model = self.session.get(IFRSMappingModel, mapping_id)
        if not model:
            return Result.failure(VASValidationError(ErrorCodes.IFRS_MAPPING_NOT_FOUND, mapping_id=mapping_id))
        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def get_coverage(self) -> dict:
        all_accounts = self.repo.list_all()
        mappings = self.session.execute(
            select(IFRSMappingModel)
        ).scalars().all()

        mapped_vas = {m.vas_account_code for m in mappings}
        total = len(all_accounts)
        mapped = sum(1 for a in all_accounts if a.code in mapped_vas)
        unmapped = [{"code": a.code, "name": a.name} for a in all_accounts if a.code not in mapped_vas]

        return {
            "total_vas_accounts": total,
            "mapped_accounts": mapped,
            "unmapped_accounts": total - mapped,
            "coverage_percent": round((mapped / total * 100), 1) if total > 0 else 0,
            "unmapped": unmapped,
        }
