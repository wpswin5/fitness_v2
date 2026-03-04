"""User repository – Auth0 sync (upsert) and profile queries."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.orm_models import User
from src.models.users import UserCreate, UserUpdate
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    # -- lookup --------------------------------------------------------------

    def get_by_auth0_sub(self, auth0_sub: str) -> Optional[User]:
        """Find a user by their Auth0 subject identifier."""
        stmt = select(User).where(User.auth0_sub == auth0_sub)
        return self.db.execute(stmt).scalars().first()

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalars().first()

    # -- upsert (Auth0 sync) -------------------------------------------------

    def sync_user(self, data: UserCreate) -> User:
        """Create or update a user from an Auth0 login event.

        If a user with the given ``auth0_sub`` already exists, update fields
        that may have changed (email, name). Otherwise insert a new row.
        """
        existing = self.get_by_auth0_sub(data.auth0_sub)
        if existing is not None:
            existing.email = data.email
            if data.first_name is not None:
                existing.first_name = data.first_name
            if data.last_name is not None:
                existing.last_name = data.last_name
            self.db.flush()
            self.db.refresh(existing)
            return existing

        user = User(
            auth0_sub=data.auth0_sub,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return self.create(user)

    # -- profile update ------------------------------------------------------

    def update_profile(self, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.flush()
        self.db.refresh(user)
        return user
