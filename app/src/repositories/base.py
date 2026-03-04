"""Base repository with common CRUD helpers."""

import uuid
from datetime import datetime
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.orm_models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic CRUD repository.

    Subclasses set ``model`` to the ORM class they manage.
    """

    model: Type[T]

    def __init__(self, db: Session):
        self.db = db

    # -- helpers -------------------------------------------------------------

    def _active_filter(self, stmt: Any) -> Any:
        """If the model has a ``deleted_at`` column, exclude soft-deleted rows."""
        col = getattr(self.model, "deleted_at", None)
        if col is not None:
            stmt = stmt.where(col.is_(None))
        return stmt

    # -- read ----------------------------------------------------------------

    def get_by_id(self, entity_id: uuid.UUID) -> Optional[T]:
        pk_col = list(self.model.__table__.primary_key)[0]
        stmt = select(self.model).where(pk_col == entity_id)
        stmt = self._active_filter(stmt)
        return self.db.execute(stmt).scalars().first()

    def list_all(self, *, offset: int = 0, limit: int = 50) -> List[T]:
        stmt = select(self.model)
        stmt = self._active_filter(stmt)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    # -- write ---------------------------------------------------------------

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.flush()  # assigns server-side defaults (e.g. PK)
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Soft-delete if supported, otherwise hard-delete."""
        if hasattr(entity, "deleted_at"):
            setattr(entity, "deleted_at", datetime.utcnow())
        else:
            self.db.delete(entity)
        self.db.flush()
