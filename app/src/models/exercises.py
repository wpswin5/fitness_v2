"""Exercise models - master list of available exercises."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from .base import DBModelBase, TimestampMixin


class DifficultyLevel(str, Enum):
    """Exercise difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MuscleGroup(str, Enum):
    """Primary muscle groups."""
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    ABS = "abs"
    OBLIQUES = "obliques"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    FULL_BODY = "full_body"
    CARDIO = "cardio"


class ExerciseBase(DBModelBase):
    """Base exercise fields."""
    name: str = Field(..., max_length=255, description="Exercise name")
    description: Optional[str] = Field(None, description="Exercise description")
    equipment_required: Optional[List[str]] = Field(
        default=None, 
        description="List of equipment needed (e.g., ['barbell', 'bench'])"
    )
    primary_muscle_group: Optional[MuscleGroup] = Field(
        None, 
        description="Primary muscle group targeted"
    )
    difficulty_level: Optional[DifficultyLevel] = Field(
        None, 
        description="Exercise difficulty level"
    )
    instructions: Optional[str] = Field(None, description="Step-by-step instructions")


class ExerciseCreate(ExerciseBase):
    """Schema for creating a new exercise."""
    pass


class ExerciseUpdate(DBModelBase):
    """Schema for updating an exercise."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    equipment_required: Optional[List[str]] = None
    primary_muscle_group: Optional[MuscleGroup] = None
    difficulty_level: Optional[DifficultyLevel] = None
    instructions: Optional[str] = None


class ExerciseInDB(ExerciseBase, TimestampMixin):
    """Exercise as stored in the database."""
    exercise_id: UUID = Field(..., description="Unique exercise identifier")


class ExerciseResponse(ExerciseBase):
    """Exercise response returned to clients."""
    exercise_id: UUID = Field(..., description="Unique exercise identifier")
    created_at: datetime


class ExerciseSummary(DBModelBase):
    """Minimal exercise info for embedding in other responses."""
    exercise_id: UUID
    name: str
    primary_muscle_group: Optional[MuscleGroup] = None
