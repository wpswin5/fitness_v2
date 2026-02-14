"""Workout models - workout templates, sets, and set steps."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from .base import DBModelBase, TimestampMixin
from .exercises import ExerciseSummary


# ============================================================================
# SetStep Models - Individual rep/weight segments within a set
# ============================================================================

class SetStepBase(DBModelBase):
    """Base set step fields."""
    step_order: int = Field(..., ge=1, description="Order within the set (1, 2, 3...)")
    planned_reps: int = Field(..., ge=1, description="Target reps for this step")
    planned_weight: Optional[Decimal] = Field(
        None, 
        ge=0, 
        decimal_places=2,
        description="Target weight in lbs/kg (null for bodyweight)"
    )


class SetStepCreate(SetStepBase):
    """Schema for creating a set step."""
    pass


class SetStepUpdate(DBModelBase):
    """Schema for updating a set step."""
    step_order: Optional[int] = Field(None, ge=1)
    planned_reps: Optional[int] = Field(None, ge=1)
    planned_weight: Optional[Decimal] = Field(None, ge=0)


class SetStepInDB(SetStepBase, TimestampMixin):
    """Set step as stored in the database."""
    set_step_id: UUID = Field(..., description="Unique set step identifier")
    set_id: UUID = Field(..., description="Parent set identifier")


class SetStepResponse(SetStepBase):
    """Set step response returned to clients."""
    set_step_id: UUID


# ============================================================================
# Set Models - Exercise entries within a workout
# ============================================================================

class SetBase(DBModelBase):
    """Base set fields."""
    set_order: int = Field(..., ge=1, description="Order within the workout (1, 2, 3...)")
    exercise_id: UUID = Field(..., description="Reference to the exercise")
    num_sets: int = Field(default=1, ge=1, description="Number of times to perform this set")
    rest_seconds: Optional[int] = Field(None, ge=0, description="Rest time between sets in seconds")
    notes: Optional[str] = Field(None, description="Notes for this set")


class SetCreate(SetBase):
    """Schema for creating a set with its steps."""
    steps: List[SetStepCreate] = Field(
        default_factory=list,
        description="Rep/weight steps within this set"
    )

    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v):
        """Ensure at least one step is provided."""
        if not v:
            raise ValueError("At least one set step is required")
        # Validate step_order is sequential starting from 1
        orders = sorted([step.step_order for step in v])
        expected = list(range(1, len(v) + 1))
        if orders != expected:
            raise ValueError("step_order must be sequential starting from 1")
        return v


class SetUpdate(DBModelBase):
    """Schema for updating a set."""
    set_order: Optional[int] = Field(None, ge=1)
    exercise_id: Optional[UUID] = None
    num_sets: Optional[int] = Field(None, ge=1)
    rest_seconds: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class SetInDB(SetBase, TimestampMixin):
    """Set as stored in the database."""
    set_id: UUID = Field(..., description="Unique set identifier")
    workout_id: UUID = Field(..., description="Parent workout identifier")


class SetResponse(SetBase):
    """Set response with nested steps."""
    set_id: UUID
    steps: List[SetStepResponse] = Field(default_factory=list)
    exercise: Optional[ExerciseSummary] = None  # Populated when joined


class SetSummary(DBModelBase):
    """Minimal set info for lists."""
    set_id: UUID
    set_order: int
    exercise_id: UUID
    num_sets: int


# ============================================================================
# Workout Models - Workout templates
# ============================================================================

class WorkoutBase(DBModelBase):
    """Base workout fields."""
    name: str = Field(..., max_length=255, description="Workout name")
    description: Optional[str] = Field(None, description="Workout description")
    is_shared: bool = Field(default=False, description="Whether workout is publicly visible")


class WorkoutCreate(WorkoutBase):
    """Schema for creating a workout with sets."""
    sets: List[SetCreate] = Field(
        default_factory=list,
        description="Exercise sets in this workout"
    )


class WorkoutUpdate(DBModelBase):
    """Schema for updating a workout."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_shared: Optional[bool] = None


class WorkoutInDB(WorkoutBase, TimestampMixin):
    """Workout as stored in the database."""
    workout_id: UUID = Field(..., description="Unique workout identifier")
    creator_id: UUID = Field(..., description="User who created this workout")


class WorkoutResponse(WorkoutBase):
    """Full workout response with nested sets."""
    workout_id: UUID
    creator_id: UUID
    created_at: datetime
    sets: List[SetResponse] = Field(default_factory=list)


class WorkoutSummary(DBModelBase):
    """Minimal workout info for lists."""
    workout_id: UUID
    name: str
    is_shared: bool
    created_at: datetime
