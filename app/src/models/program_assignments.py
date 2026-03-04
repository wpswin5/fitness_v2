"""Program assignment and progress tracking models."""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import Field, computed_field

from .base import DBModelBase, TimestampMixin


# ============================================================================
# Enums
# ============================================================================

class AssignmentStatus(str, Enum):
    """Program assignment lifecycle status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class WorkoutLogStatus(str, Enum):
    """Status of a scheduled workout within a program assignment."""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ============================================================================
# ProgramWorkoutLog Models - Per-slot completion tracking
# ============================================================================

class ProgramWorkoutLogBase(DBModelBase):
    """Base program workout log fields."""
    week_number: int = Field(..., ge=1, description="Week number in the program")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Sunday, 6=Saturday)")
    status: WorkoutLogStatus = Field(
        default=WorkoutLogStatus.PENDING,
        description="Completion status"
    )
    scheduled_date: Optional[date] = Field(
        None,
        description="Actual calendar date this workout is scheduled for"
    )
    notes: Optional[str] = Field(None, description="Notes for this entry")


class ProgramWorkoutLogCreate(DBModelBase):
    """Schema for creating a program workout log entry (typically auto-generated)."""
    week_number: int = Field(..., ge=1)
    day_of_week: int = Field(..., ge=0, le=6)
    scheduled_date: Optional[date] = None


class ProgramWorkoutLogUpdate(DBModelBase):
    """Schema for updating a program workout log (marking complete/skipped)."""
    status: Optional[WorkoutLogStatus] = None
    workout_log_id: Optional[UUID] = Field(
        None,
        description="Link to actual WorkoutLog when completed"
    )
    notes: Optional[str] = None


class ProgramWorkoutLogInDB(ProgramWorkoutLogBase, TimestampMixin):
    """Program workout log as stored in the database."""
    program_workout_log_id: UUID
    assignment_id: UUID
    workout_log_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None


class ProgramWorkoutLogResponse(ProgramWorkoutLogBase):
    """Program workout log response."""
    program_workout_log_id: UUID
    assignment_id: UUID
    workout_log_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None


# ============================================================================
# UserProgramAssignment Models - Program enrollment
# ============================================================================

class UserProgramAssignmentBase(DBModelBase):
    """Base assignment fields."""
    start_date: date = Field(..., description="Date the user started this program")


class UserProgramAssignmentCreate(UserProgramAssignmentBase):
    """Schema for enrolling a user in a program."""
    program_id: UUID = Field(..., description="Program to enroll in")


class UserProgramAssignmentUpdate(DBModelBase):
    """Schema for updating an assignment (pause, resume, complete, abandon)."""
    status: Optional[AssignmentStatus] = None
    current_week: Optional[int] = Field(None, ge=1)
    current_day_of_week: Optional[int] = Field(None, ge=0, le=6)


class UserProgramAssignmentInDB(UserProgramAssignmentBase, TimestampMixin):
    """Assignment as stored in the database."""
    assignment_id: UUID
    user_id: UUID
    program_id: UUID
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    current_week: int = 1
    current_day_of_week: int = 0
    completed_at: Optional[datetime] = None


class UserProgramAssignmentResponse(UserProgramAssignmentBase):
    """Assignment response with progress info."""
    assignment_id: UUID
    user_id: UUID
    program_id: UUID
    status: AssignmentStatus
    current_week: int
    current_day_of_week: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    workout_logs: List[ProgramWorkoutLogResponse] = Field(default_factory=list)


class UserProgramAssignmentSummary(DBModelBase):
    """Minimal assignment info for lists."""
    assignment_id: UUID
    program_id: UUID
    status: AssignmentStatus
    start_date: date
    current_week: int
    current_day_of_week: int
    created_at: datetime


# ============================================================================
# Progress aggregation models
# ============================================================================

class ProgramProgress(DBModelBase):
    """Calculated progress for a program assignment."""
    assignment_id: UUID
    program_id: UUID
    total_workouts: int = Field(..., description="Total scheduled workout slots")
    completed_workouts: int = Field(..., description="Number completed")
    skipped_workouts: int = Field(..., description="Number skipped")
    pending_workouts: int = Field(..., description="Number remaining")

    @computed_field
    @property
    def completion_percentage(self) -> float:
        """Percentage of workouts completed (completed / total)."""
        if self.total_workouts == 0:
            return 0.0
        return round((self.completed_workouts / self.total_workouts) * 100, 1)

    @computed_field
    @property
    def progress_percentage(self) -> float:
        """Percentage of workouts addressed (completed + skipped / total)."""
        if self.total_workouts == 0:
            return 0.0
        return round(
            ((self.completed_workouts + self.skipped_workouts) / self.total_workouts) * 100, 1
        )
