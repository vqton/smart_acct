from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from domain import (
    ChartOfAccounts, AccountType, DCRDirection,
    AccountingRegime, AccountStatus,
    Result, ChartError, ValidationError
)
from domain.i18n import ErrorCodes
from infrastructure.models.coa_models import COAModel, AccountingRegime as DBRegime, AccountStatus as DBStatus


class COARepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: COAModel) -> ChartOfAccounts:
        return ChartOfAccounts(
            code=model.code,
            name=model.name,
            account_type=AccountType(model.account_type),
            regime=AccountingRegime(model.regime.value),
            vas_compliant=model.vas_compliant,
            drcr_direction=DCRDirection(model.drcr_direction),
            level=model.level,
            status=AccountStatus(model.status.value),
            currency=model.currency,
            unit=model.unit,
            parent_code=model.parent_code,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, domain: ChartOfAccounts) -> COAModel:
        return COAModel(
            code=domain.code,
            name=domain.name,
            account_type=domain.account_type.value,
            regime=DBRegime(domain.regime.value),
            vas_compliant=domain.vas_compliant,
            drcr_direction=domain.drcr_direction.value,
            level=domain.level,
            status=DBStatus(domain.status.value),
            currency=domain.currency,
            unit=domain.unit,
            parent_code=domain.parent_code,
            description=domain.description,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    def create(self, account: ChartOfAccounts) -> Result:
        existing = self.session.execute(
            select(COAModel).where(COAModel.code == account.code)
        ).scalar_one_or_none()
        if existing:
            return Result.failure(ChartError(ErrorCodes.ALREADY_EXISTS, type="Account", id=account.code))

        model = self._to_model(account)
        self.session.add(model)
        self.session.flush()
        return Result.success(self._to_domain(model))

    def get_by_code(self, code: str) -> Optional[ChartOfAccounts]:
        model = self.session.execute(
            select(COAModel).where(COAModel.code == code)
        ).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def get_by_id(self, account_id: int) -> Optional[ChartOfAccounts]:
        model = self.session.get(COAModel, account_id)
        return self._to_domain(model) if model else None

    def list_all(
        self,
        regime: Optional[AccountingRegime] = None,
        status: Optional[AccountStatus] = None,
        account_type: Optional[AccountType] = None,
        parent_code: Optional[str] = None,
    ) -> List[ChartOfAccounts]:
        stmt = select(COAModel)
        if regime:
            stmt = stmt.where(COAModel.regime == DBRegime(regime.value))
        if status:
            stmt = stmt.where(COAModel.status == DBStatus(status.value))
        if account_type:
            stmt = stmt.where(COAModel.account_type == account_type.value)
        if parent_code is not None:
            stmt = stmt.where(COAModel.parent_code == parent_code)
        stmt = stmt.order_by(COAModel.code)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def search(self, query: str) -> List[ChartOfAccounts]:
        pattern = f"%{query}%"
        stmt = select(COAModel).where(
            or_(COAModel.code.ilike(pattern), COAModel.name.ilike(pattern))
        ).order_by(COAModel.code)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def update(self, code: str, **kwargs) -> Result:
        model = self.session.execute(
            select(COAModel).where(COAModel.code == code)
        ).scalar_one_or_none()
        if not model:
            return Result.failure(ChartError(ErrorCodes.ACCOUNT_NOT_FOUND, code=code))

        allowed = {"name", "description", "status", "currency", "unit", "vas_compliant", "parent_code"}
        for key, value in kwargs.items():
            if key not in allowed:
                return Result.failure(ValidationError(ErrorCodes.FIELD_CANNOT_BE_UPDATED, field=key))
            if key == "status" and isinstance(value, AccountStatus):
                setattr(model, key, DBStatus(value.value))
            elif key == "regime" and isinstance(value, AccountingRegime):
                setattr(model, key, DBRegime(value.value))
            else:
                setattr(model, key, value)

        model.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        self.session.refresh(model)
        return Result.success(self._to_domain(model))

    def delete(self, code: str) -> Result:
        children = self.session.execute(
            select(COAModel).where(COAModel.parent_code == code)
        ).scalars().all()
        if children:
            return Result.failure(
                ChartError(f"Cannot delete '{code}': it has {len(children)} child account(s)")
            )

        model = self.session.execute(
            select(COAModel).where(COAModel.code == code)
        ).scalar_one_or_none()
        if not model:
            return Result.failure(ChartError(ErrorCodes.ACCOUNT_NOT_FOUND, code=code))

        self.session.delete(model)
        self.session.flush()
        return Result.success(None)

    def count(self) -> int:
        from sqlalchemy import select, func
        return self.session.execute(
            select(func.count()).select_from(COAModel)
        ).scalar()
