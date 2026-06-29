from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain import (
    ChartOfAccounts, AccountingRegime, AccountStatus, Result, ChartError,
)
from domain.i18n import ErrorCodes
from infrastructure.repositories.coa_repository import COARepository
from infrastructure.models.coa_models import COAVersionModel


class COAVersioningUseCase:
    def __init__(self, session: Session):
        self.repo = COARepository(session)
        self.session = session

    def _snapshot(self) -> List[Dict[str, Any]]:
        accounts = self.repo.list_all()
        return [
            {
                "code": a.code, "name": a.name,
                "account_type": a.account_type.value,
                "drcr_direction": a.drcr_direction.value,
                "level": a.level, "status": a.status.value,
                "regime": a.regime.value, "parent_code": a.parent_code,
                "description": a.description, "currency": a.currency,
                "unit": a.unit, "vas_compliant": a.vas_compliant,
            }
            for a in accounts
        ]

    def create_snapshot(self, created_by: Optional[str] = None,
                        notes: Optional[str] = None) -> Result:
        snapshot = self._snapshot()
        model = COAVersionModel(
            snapshot=snapshot,
            account_count=len(snapshot),
            created_by=created_by,
            notes=notes,
        )
        self.session.add(model)
        self.session.flush()
        return Result.success({
            "id": model.id,
            "account_count": model.account_count,
            "created_by": model.created_by,
            "notes": model.notes,
            "created_at": model.created_at.isoformat(),
        })

    def list_versions(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        models = self.session.execute(
            select(COAVersionModel)
            .order_by(COAVersionModel.created_at.desc())
            .limit(limit).offset(offset)
        ).scalars().all()
        return [
            {
                "id": m.id, "account_count": m.account_count,
                "created_by": m.created_by, "notes": m.notes,
                "created_at": m.created_at.isoformat(),
            }
            for m in models
        ]

    def get_version(self, version_id: int) -> Result:
        model = self.session.get(COAVersionModel, version_id)
        if not model:
            return Result.failure(ChartError(ErrorCodes.VERSION_NOT_FOUND, version_id=version_id))
        return Result.success({
            "id": model.id,
            "account_count": model.account_count,
            "created_by": model.created_by,
            "notes": model.notes,
            "created_at": model.created_at.isoformat(),
            "snapshot": model.snapshot,
        })

    def diff_versions(self, v1_id: int, v2_id: int) -> Result:
        v1 = self.session.get(COAVersionModel, v1_id)
        v2 = self.session.get(COAVersionModel, v2_id)
        if not v1:
            return Result.failure(ChartError(ErrorCodes.VERSION_NOT_FOUND, version_id=v1_id))
        if not v2:
            return Result.failure(ChartError(ErrorCodes.VERSION_NOT_FOUND, version_id=v2_id))

        snap1 = {a["code"]: a for a in v1.snapshot}
        snap2 = {a["code"]: a for a in v2.snapshot}

        added = [snap2[c] for c in snap2 if c not in snap1]
        removed = [snap1[c] for c in snap1 if c not in snap2]
        changed = [
            {"code": c, "before": snap1[c], "after": snap2[c]}
            for c in snap2 if c in snap1 and snap1[c] != snap2[c]
        ]

        return Result.success({
            "version_1": {"id": v1.id, "created_at": v1.created_at.isoformat()},
            "version_2": {"id": v2.id, "created_at": v2.created_at.isoformat()},
            "added": added,
            "added_count": len(added),
            "removed": removed,
            "removed_count": len(removed),
            "changed": changed,
            "changed_count": len(changed),
        })

    def auto_snapshot(self, created_by: Optional[str] = None) -> Result:
        return self.create_snapshot(
            created_by=created_by or "system",
            notes="Auto-snapshot before modification",
        )
