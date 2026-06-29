from typing import TypeVar, Generic, List, Optional, Any
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def create(self, entity: T) -> Any:
        ...

    @abstractmethod
    def get(self, id: Any) -> Optional[T]:
        ...

    @abstractmethod
    def list_all(self, **filters) -> List[T]:
        ...

    @abstractmethod
    def delete(self, id: Any) -> Any:
        ...
