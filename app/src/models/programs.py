"""Program models - organized groups of workouts for training programs."""

from datetime import datetime
from enum import IntEnum
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from .base import DBModelBase, TimestampMixin, CreatedAtMixin
from .workouts import WorkoutSummary


class DayOfWeek(IntEnum):
    """Days of the week (0=Sunday convention)."""
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


# ============================================================================
# ProgramWorkout Models - Workout scheduling within programs
# ============================================================================

class ProgramWorkoutBase(DBModelBase):
    """Base program workout fields."""
    week_number: int = Field(..., ge=1, description="Week number (1 to duration_weeks)")
    day_of_week: DayOfWeek = Field(..., description="Day of week (0=Sunday, 6=Saturday)")
    is_rest_day: bool = Field(default=False, description="Whether this is a rest day")
    workout_id: Optional[UUID] = Field(
        None, 
        description="Workout to perform (null if rest day)"
    )

    @model_validator(mode='after')
    def validate_rest_day_logic(self):
        """Ensure rest day and workout_id are consistent."""
        if self.is_rest_day and self.workout_id is not None:
            raise ValueError("Rest days cannot have a workout assigned")
        if not self.is_rest_day and self.workout_id is None:
            raise ValueError("Non-rest days must have a workout assigned")
        return self


class ProgramWorkoutCreate(ProgramWorkoutBase):
    """Schema for scheduling a workout in a program."""
    pass


class ProgramWorkoutInDB(ProgramWorkoutBase, CreatedAtMixin):
    """Program workout as stored in the database."""
    program_id: UUID = Field(..., description="Parent program identifier")


class ProgramWorkoutResponse(DBModelBase):
    """Program workout response with optional workout details."""
    week_number: int
    day_of_week: DayOfWeek
    is_rest_day: bool
    workout: Optional[WorkoutSummary] = None  # Populated when joined


# ============================================================================
# Program Models - Multi-week training programs
# ============================================================================

class ProgramBase(DBModelBase):
    """Base program fields."""
    name: str = Field(..., max_length=255, description="Program name")
    description: Optional[str] = Field(None, description="Program description")
    is_shared: bool = Field(default=False, description="Whether program is publicly visible")
    duration_weeks: int = Field(default=1, ge=1, le=52, description="Program duration in weeks")


class ProgramCreate(ProgramBase):
    """Schema for creating a program with scheduled workouts."""
    schedule: List[ProgramWorkoutCreate] = Field(
        default_factory=list,
        description="Workout schedule for the program"
    )

    @field_validator('schedule')
    @classmethod
    def validate_schedule(cls, v, info):
        """Validate schedule entries are within program duration."""
        if not v:
            return v
        
        # Check for duplicate week/day combinations
        seen = set()
        for entry in v:
            key = (entry.week_number, entry.day_of_week)
            if key in seen:
                raise ValueError(
                    f"Duplicate schedule entry for week {entry.week_number}, "
                    f"day {entry.day_of_week.name}"
                )
            seen.add(key)
        
        return v


class ProgramUpdate(DBModelBase):
    """Schema for updating a program."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_shared: Optional[bool] = None
    duration_weeks: Optional[int] = Field(None, ge=1, le=52)


class ProgramInDB(ProgramBase, TimestampMixin):
    """Program as stored in the database."""
    program_id: UUID = Field(..., description="Unique program identifier")
    creator_id: UUID = Field(..., description="User who created this program")


class ProgramResponse(ProgramBase):
    """Full program response with schedule."""
    program_id: UUID
    creator_id: UUID
    created_at: datetime
    schedule: List[ProgramWorkoutResponse] = Field(default_factory=list)


class ProgramSummary(DBModelBase):
    """Minimal program info for lists."""
    program_id: UUID
    name: str
    duration_weeks: int
    is_shared: bool
    created_at: datetime
