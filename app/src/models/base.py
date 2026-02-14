"""Base models and common utilities for Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimestampMixin(BaseModel):
    """Mixin for models with created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreatedAtMixin(BaseModel):
    """Mixin for models with only created_at timestamp (logs)."""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DBModelBase(BaseModel):
    """Base class for all database models with common config."""
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy compatibility
        populate_by_name=True,
        str_strip_whitespace=True,
    )


# Common field definitions for reuse
def uuid_field(description: str = "Unique identifier"):
    """Create a UUID field with standard settings."""
    return Field(description=description)


def optional_uuid_field(description: str = "Optional unique identifier"):
    """Create an optional UUID field."""
    return Field(default=None, description=description)
