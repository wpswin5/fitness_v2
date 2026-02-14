"""Workout logging models - tracking completed workouts, sets, and performance."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import Field, computed_field

from .base import DBModelBase, CreatedAtMixin
from .exercises import ExerciseSummary


# ============================================================================
# SetStepLog Models - Actual performance for each step
# ============================================================================

class SetStepLogBase(DBModelBase):
    """Base set step log fields."""
    step_order: int = Field(..., ge=1, description="Order within the set")
    completed_reps: int = Field(..., ge=0, description="Actual reps completed")
    completed_weight: Optional[Decimal] = Field(
        None, 
        ge=0,
        decimal_places=2,
        description="Actual weight used"
    )
    completed_time_seconds: Optional[int] = Field(
        None, 
        ge=0, 
        description="Time to complete this step"
    )
    rest_time_after_seconds: Optional[int] = Field(
        None, 
        ge=0, 
        description="Rest taken after this step"
    )
    notes: Optional[str] = Field(None, description="Notes for this step")


class SetStepLogCreate(SetStepLogBase):
    """Schema for logging a set step."""
    original_set_step_id: Optional[UUID] = Field(
        None, 
        description="Reference to planned set step (null for ad-hoc)"
    )


class SetStepLogInDB(SetStepLogBase, CreatedAtMixin):
    """Set step log as stored in the database."""
    set_step_log_id: UUID
    set_log_id: UUID
    original_set_step_id: Optional[UUID] = None


class SetStepLogResponse(SetStepLogBase):
    """Set step log response."""
    set_step_log_id: UUID
    original_set_step_id: Optional[UUID] = None


# ============================================================================
# SetLog Models - Individual set executions
# ============================================================================

class SetLogBase(DBModelBase):
    """Base set log fields."""
    set_order: int = Field(..., ge=1, description="Order in the workout")
    exercise_id: UUID = Field(..., description="Exercise performed")
    set_number: int = Field(..., ge=1, description="Which occurrence (1st, 2nd, 3rd...)")


class SetLogCreate(SetLogBase):
    """Schema for logging a set with its steps."""
    original_set_id: Optional[UUID] = Field(
        None, 
        description="Reference to planned set (null for ad-hoc)"
    )
    steps: List[SetStepLogCreate] = Field(
        default_factory=list,
        description="Logged steps within this set"
    )


class SetLogInDB(SetLogBase, CreatedAtMixin):
    """Set log as stored in the database."""
    set_log_id: UUID
    workout_log_id: UUID
    original_set_id: Optional[UUID] = None


class SetLogResponse(SetLogBase):
    """Set log response with nested step logs."""
    set_log_id: UUID
    original_set_id: Optional[UUID] = None
    steps: List[SetStepLogResponse] = Field(default_factory=list)
    exercise: Optional[ExerciseSummary] = None  # Populated when joined


class SetLogSummary(DBModelBase):
    """Minimal set log info."""
    set_log_id: UUID
    set_order: int
    set_number: int
    exercise_id: UUID


# ============================================================================
# WorkoutLog Models - Completed workout sessions
# ============================================================================

class WorkoutLogBase(DBModelBase):
    """Base workout log fields."""
    start_time: datetime = Field(..., description="When the workout started")
    end_time: Optional[datetime] = Field(None, description="When the workout ended")
    notes: Optional[str] = Field(None, description="Workout notes")


class WorkoutLogCreate(WorkoutLogBase):
    """Schema for starting/logging a workout."""
    original_workout_id: Optional[UUID] = Field(
        None, 
        description="Reference to workout template (null for ad-hoc)"
    )
    program_id: Optional[UUID] = Field(
        None, 
        description="If completed as part of a program"
    )


class WorkoutLogUpdate(DBModelBase):
    """Schema for updating a workout log (e.g., marking complete)."""
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class WorkoutLogInDB(WorkoutLogBase, CreatedAtMixin):
    """Workout log as stored in the database."""
    workout_log_id: UUID
    user_id: UUID
    original_workout_id: Optional[UUID] = None
    program_id: Optional[UUID] = None

    @computed_field
    @property
    def total_duration_minutes(self) -> Optional[int]:
        """Calculate workout duration in minutes."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None


class WorkoutLogResponse(WorkoutLogBase):
    """Full workout log response with nested set logs."""
    workout_log_id: UUID
    user_id: UUID
    original_workout_id: Optional[UUID] = None
    program_id: Optional[UUID] = None
    total_duration_minutes: Optional[int] = None
    set_logs: List[SetLogResponse] = Field(default_factory=list)


class WorkoutLogSummary(DBModelBase):
    """Minimal workout log info for lists."""
    workout_log_id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_minutes: Optional[int] = None
    original_workout_id: Optional[UUID] = None


# ============================================================================
# Aggregation Models - For analytics and summaries
# ============================================================================

class ExercisePerformance(DBModelBase):
    """Performance summary for an exercise across logs."""
    exercise_id: UUID
    exercise_name: str
    total_sets: int
    total_reps: int
    max_weight: Optional[Decimal] = None
    avg_weight: Optional[Decimal] = None


class WorkoutStats(DBModelBase):
    """Aggregated stats for a user's workout history."""
    total_workouts: int
    total_duration_minutes: int
    avg_duration_minutes: float
    workouts_this_week: int
    workouts_this_month: int
