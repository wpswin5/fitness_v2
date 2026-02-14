"""User models for Auth0 integration."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from .base import DBModelBase, TimestampMixin


class UserBase(DBModelBase):
    """Base user fields shared across create/update/response."""
    email: EmailStr = Field(..., max_length=255, description="User's email address")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")


class UserCreate(UserBase):
    """Schema for creating a new user (from Auth0 callback)."""
    auth0_sub: str = Field(..., max_length=255, description="Auth0 subject identifier")


class UserUpdate(DBModelBase):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserInDB(UserBase, TimestampMixin):
    """User as stored in the database."""
    user_id: UUID = Field(..., description="Unique user identifier")
    auth0_sub: str = Field(..., max_length=255, description="Auth0 subject identifier")


class UserResponse(UserBase):
    """User response returned to clients (excludes sensitive fields)."""
    user_id: UUID = Field(..., description="Unique user identifier")
    created_at: datetime
