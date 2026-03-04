"""
SQLAlchemy ORM table models mapped to the existing Azure SQL schema.

These are the database-side models (Table definitions). They map 1:1 to the
SQL tables created by the migration scripts. Pydantic models in src/models/
remain the API-facing request/response schemas.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Computed,
)
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""
    pass


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "Users"
    __table_args__ = {"schema": "dbo"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        "UserId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    auth0_sub: Mapped[str] = mapped_column("Auth0Sub", String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column("Email", String(255), unique=True, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column("FirstName", String(100))
    last_name: Mapped[Optional[str]] = mapped_column("LastName", String(100))
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    exercises: Mapped[List["Exercise"]] = relationship(back_populates="creator", foreign_keys="Exercise.creator_id")
    workouts: Mapped[List["Workout"]] = relationship(back_populates="creator")
    programs: Mapped[List["Program"]] = relationship(back_populates="creator")
    workout_logs: Mapped[List["WorkoutLog"]] = relationship(back_populates="user")
    program_assignments: Mapped[List["UserProgramAssignment"]] = relationship(back_populates="user")


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------

class Exercise(Base):
    __tablename__ = "Exercises"
    __table_args__ = {"schema": "dbo"}

    exercise_id: Mapped[uuid.UUID] = mapped_column(
        "ExerciseId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "CreatorId", UNIQUEIDENTIFIER, ForeignKey("dbo.Users.UserId", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column("Name", String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column("Description", Text)
    equipment_required: Mapped[Optional[str]] = mapped_column("EquipmentRequired", Text)  # JSON string
    primary_muscle_group: Mapped[Optional[str]] = mapped_column("PrimaryMuscleGroup", String(100))
    difficulty_level: Mapped[Optional[str]] = mapped_column("DifficultyLevel", String(50))
    instructions: Mapped[Optional[str]] = mapped_column("Instructions", Text)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("DeletedAt", DateTime)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(back_populates="exercises", foreign_keys=[creator_id])
    sets: Mapped[List["Set"]] = relationship(back_populates="exercise")


# ---------------------------------------------------------------------------
# Workouts
# ---------------------------------------------------------------------------

class Workout(Base):
    __tablename__ = "Workouts"
    __table_args__ = {"schema": "dbo"}

    workout_id: Mapped[uuid.UUID] = mapped_column(
        "WorkoutId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        "CreatorId", UNIQUEIDENTIFIER, ForeignKey("dbo.Users.UserId", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column("Name", String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column("Description", Text)
    is_shared: Mapped[bool] = mapped_column("IsShared", Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("DeletedAt", DateTime)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator: Mapped["User"] = relationship(back_populates="workouts")
    sets: Mapped[List["Set"]] = relationship(back_populates="workout", cascade="all, delete-orphan", order_by="Set.set_order")
    program_workouts: Mapped[List["ProgramWorkout"]] = relationship(back_populates="workout")
    workout_logs: Mapped[List["WorkoutLog"]] = relationship(back_populates="original_workout")


# ---------------------------------------------------------------------------
# Sets
# ---------------------------------------------------------------------------

class Set(Base):
    __tablename__ = "Sets"
    __table_args__ = (
        UniqueConstraint("WorkoutId", "SetOrder", name="IX_Sets_WorkoutId_SetOrder"),
        {"schema": "dbo"},
    )

    set_id: Mapped[uuid.UUID] = mapped_column(
        "SetId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        "WorkoutId", UNIQUEIDENTIFIER, ForeignKey("dbo.Workouts.WorkoutId", ondelete="CASCADE"), nullable=False
    )
    set_order: Mapped[int] = mapped_column("SetOrder", Integer, nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        "ExerciseId", UNIQUEIDENTIFIER, ForeignKey("dbo.Exercises.ExerciseId", ondelete="NO ACTION"), nullable=False
    )
    num_sets: Mapped[int] = mapped_column("NumSets", Integer, default=1, nullable=False)
    rest_seconds: Mapped[Optional[int]] = mapped_column("RestSeconds", Integer)
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workout: Mapped["Workout"] = relationship(back_populates="sets")
    exercise: Mapped["Exercise"] = relationship(back_populates="sets")
    steps: Mapped[List["SetStep"]] = relationship(back_populates="set_", cascade="all, delete-orphan", order_by="SetStep.step_order")
    set_logs: Mapped[List["SetLog"]] = relationship(back_populates="original_set")


# ---------------------------------------------------------------------------
# SetSteps
# ---------------------------------------------------------------------------

class SetStep(Base):
    __tablename__ = "SetSteps"
    __table_args__ = (
        UniqueConstraint("SetId", "StepOrder", name="IX_SetSteps_SetId_StepOrder"),
        {"schema": "dbo"},
    )

    set_step_id: Mapped[uuid.UUID] = mapped_column(
        "SetStepId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    set_id: Mapped[uuid.UUID] = mapped_column(
        "SetId", UNIQUEIDENTIFIER, ForeignKey("dbo.Sets.SetId", ondelete="CASCADE"), nullable=False
    )
    step_order: Mapped[int] = mapped_column("StepOrder", Integer, nullable=False)
    planned_reps: Mapped[int] = mapped_column("PlannedReps", Integer, nullable=False)
    planned_weight: Mapped[Optional[Decimal]] = mapped_column("PlannedWeight", Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    set_: Mapped["Set"] = relationship(back_populates="steps")
    set_step_logs: Mapped[List["SetStepLog"]] = relationship(back_populates="original_set_step")


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------

class Program(Base):
    __tablename__ = "Programs"
    __table_args__ = {"schema": "dbo"}

    program_id: Mapped[uuid.UUID] = mapped_column(
        "ProgramId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        "CreatorId", UNIQUEIDENTIFIER, ForeignKey("dbo.Users.UserId", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column("Name", String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column("Description", Text)
    is_shared: Mapped[bool] = mapped_column("IsShared", Boolean, default=False, nullable=False)
    duration_weeks: Mapped[int] = mapped_column("DurationWeeks", Integer, default=1, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("DeletedAt", DateTime)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator: Mapped["User"] = relationship(back_populates="programs")
    program_workouts: Mapped[List["ProgramWorkout"]] = relationship(back_populates="program", cascade="all, delete-orphan")
    workout_logs: Mapped[List["WorkoutLog"]] = relationship(back_populates="program")
    assignments: Mapped[List["UserProgramAssignment"]] = relationship(back_populates="program")


# ---------------------------------------------------------------------------
# ProgramWorkouts
# ---------------------------------------------------------------------------

class ProgramWorkout(Base):
    __tablename__ = "ProgramWorkouts"
    __table_args__ = (
        CheckConstraint("DayOfWeek >= 0 AND DayOfWeek <= 6", name="CK_ProgramWorkouts_DayOfWeek"),
        CheckConstraint(
            "(IsRestDay = 1 AND WorkoutId IS NULL) OR (IsRestDay = 0 AND WorkoutId IS NOT NULL)",
            name="CK_ProgramWorkouts_RestDay",
        ),
        {"schema": "dbo"},
    )

    program_id: Mapped[uuid.UUID] = mapped_column(
        "ProgramId", UNIQUEIDENTIFIER, ForeignKey("dbo.Programs.ProgramId", ondelete="CASCADE"), primary_key=True
    )
    week_number: Mapped[int] = mapped_column("WeekNumber", Integer, primary_key=True)
    day_of_week: Mapped[int] = mapped_column("DayOfWeek", Integer, primary_key=True)
    workout_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "WorkoutId", UNIQUEIDENTIFIER, ForeignKey("dbo.Workouts.WorkoutId", ondelete="NO ACTION")
    )
    is_rest_day: Mapped[bool] = mapped_column("IsRestDay", Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    program: Mapped["Program"] = relationship(back_populates="program_workouts")
    workout: Mapped[Optional["Workout"]] = relationship(back_populates="program_workouts")


# ---------------------------------------------------------------------------
# WorkoutLogs
# ---------------------------------------------------------------------------

class WorkoutLog(Base):
    __tablename__ = "WorkoutLogs"
    __table_args__ = {"schema": "dbo"}

    workout_log_id: Mapped[uuid.UUID] = mapped_column(
        "WorkoutLogId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        "UserId", UNIQUEIDENTIFIER, ForeignKey("dbo.Users.UserId", ondelete="CASCADE"), nullable=False
    )
    original_workout_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "OriginalWorkoutId", UNIQUEIDENTIFIER, ForeignKey("dbo.Workouts.WorkoutId", ondelete="NO ACTION")
    )
    program_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "ProgramId", UNIQUEIDENTIFIER, ForeignKey("dbo.Programs.ProgramId", ondelete="NO ACTION")
    )
    start_time: Mapped[datetime] = mapped_column("StartTime", DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column("EndTime", DateTime)
    total_duration_minutes: Mapped[Optional[int]] = mapped_column(
        "TotalDurationMinutes", Integer, Computed("DATEDIFF(MINUTE, StartTime, EndTime)")
    )
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="workout_logs")
    original_workout: Mapped[Optional["Workout"]] = relationship(back_populates="workout_logs")
    program: Mapped[Optional["Program"]] = relationship(back_populates="workout_logs")
    set_logs: Mapped[List["SetLog"]] = relationship(back_populates="workout_log", cascade="all, delete-orphan", order_by="SetLog.set_order")
    program_workout_logs: Mapped[List["ProgramWorkoutLog"]] = relationship(back_populates="workout_log")


# ---------------------------------------------------------------------------
# SetLogs
# ---------------------------------------------------------------------------

class SetLog(Base):
    __tablename__ = "SetLogs"
    __table_args__ = {"schema": "dbo"}

    set_log_id: Mapped[uuid.UUID] = mapped_column(
        "SetLogId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    workout_log_id: Mapped[uuid.UUID] = mapped_column(
        "WorkoutLogId", UNIQUEIDENTIFIER, ForeignKey("dbo.WorkoutLogs.WorkoutLogId", ondelete="CASCADE"), nullable=False
    )
    original_set_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "OriginalSetId", UNIQUEIDENTIFIER, ForeignKey("dbo.Sets.SetId", ondelete="NO ACTION")
    )
    set_order: Mapped[int] = mapped_column("SetOrder", Integer, nullable=False)
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        "ExerciseId", UNIQUEIDENTIFIER, ForeignKey("dbo.Exercises.ExerciseId", ondelete="NO ACTION"), nullable=False
    )
    set_number: Mapped[int] = mapped_column("SetNumber", Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workout_log: Mapped["WorkoutLog"] = relationship(back_populates="set_logs")
    original_set: Mapped[Optional["Set"]] = relationship(back_populates="set_logs")
    exercise: Mapped["Exercise"] = relationship()
    step_logs: Mapped[List["SetStepLog"]] = relationship(back_populates="set_log", cascade="all, delete-orphan", order_by="SetStepLog.step_order")


# ---------------------------------------------------------------------------
# SetStepLogs
# ---------------------------------------------------------------------------

class SetStepLog(Base):
    __tablename__ = "SetStepLogs"
    __table_args__ = (
        UniqueConstraint("SetLogId", "StepOrder", name="IX_SetStepLogs_SetLogId_StepOrder"),
        {"schema": "dbo"},
    )

    set_step_log_id: Mapped[uuid.UUID] = mapped_column(
        "SetStepLogId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    set_log_id: Mapped[uuid.UUID] = mapped_column(
        "SetLogId", UNIQUEIDENTIFIER, ForeignKey("dbo.SetLogs.SetLogId", ondelete="CASCADE"), nullable=False
    )
    original_set_step_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "OriginalSetStepId", UNIQUEIDENTIFIER, ForeignKey("dbo.SetSteps.SetStepId", ondelete="NO ACTION")
    )
    step_order: Mapped[int] = mapped_column("StepOrder", Integer, nullable=False)
    completed_reps: Mapped[int] = mapped_column("CompletedReps", Integer, nullable=False)
    completed_weight: Mapped[Optional[Decimal]] = mapped_column("CompletedWeight", Numeric(10, 2))
    completed_time_seconds: Mapped[Optional[int]] = mapped_column("CompletedTimeSeconds", Integer)
    rest_time_after_seconds: Mapped[Optional[int]] = mapped_column("RestTimeAfterSeconds", Integer)
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    set_log: Mapped["SetLog"] = relationship(back_populates="step_logs")
    original_set_step: Mapped[Optional["SetStep"]] = relationship(back_populates="set_step_logs")


# ---------------------------------------------------------------------------
# UserProgramAssignments
# ---------------------------------------------------------------------------

class UserProgramAssignment(Base):
    __tablename__ = "UserProgramAssignments"
    __table_args__ = (
        UniqueConstraint("UserId", "ProgramId", "StartDate", name="UQ_UserProgramAssignments_Active"),
        CheckConstraint("Status IN ('active','completed','paused','abandoned')", name="CK_UserProgramAssignments_Status"),
        CheckConstraint("CurrentWeek >= 1", name="CK_UserProgramAssignments_CurrentWeek"),
        CheckConstraint("CurrentDayOfWeek >= 0 AND CurrentDayOfWeek <= 6", name="CK_UserProgramAssignments_CurrentDay"),
        {"schema": "dbo"},
    )

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        "AssignmentId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        "UserId", UNIQUEIDENTIFIER, ForeignKey("dbo.Users.UserId", ondelete="CASCADE"), nullable=False
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        "ProgramId", UNIQUEIDENTIFIER, ForeignKey("dbo.Programs.ProgramId", ondelete="NO ACTION"), nullable=False
    )
    start_date: Mapped[date] = mapped_column("StartDate", Date, nullable=False)
    status: Mapped[str] = mapped_column("Status", String(20), default="active", nullable=False)
    current_week: Mapped[int] = mapped_column("CurrentWeek", Integer, default=1, nullable=False)
    current_day_of_week: Mapped[int] = mapped_column("CurrentDayOfWeek", Integer, default=0, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column("CompletedAt", DateTime)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="program_assignments")
    program: Mapped["Program"] = relationship(back_populates="assignments")
    program_workout_logs: Mapped[List["ProgramWorkoutLog"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# ProgramWorkoutLogs
# ---------------------------------------------------------------------------

class ProgramWorkoutLog(Base):
    __tablename__ = "ProgramWorkoutLogs"
    __table_args__ = (
        UniqueConstraint("AssignmentId", "WeekNumber", "DayOfWeek", name="UQ_ProgramWorkoutLogs_Slot"),
        CheckConstraint("Status IN ('pending','completed','skipped')", name="CK_ProgramWorkoutLogs_Status"),
        CheckConstraint("DayOfWeek >= 0 AND DayOfWeek <= 6", name="CK_ProgramWorkoutLogs_DayOfWeek"),
        {"schema": "dbo"},
    )

    program_workout_log_id: Mapped[uuid.UUID] = mapped_column(
        "ProgramWorkoutLogId", UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        "AssignmentId", UNIQUEIDENTIFIER, ForeignKey("dbo.UserProgramAssignments.AssignmentId", ondelete="CASCADE"), nullable=False
    )
    week_number: Mapped[int] = mapped_column("WeekNumber", Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column("DayOfWeek", Integer, nullable=False)
    workout_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "WorkoutLogId", UNIQUEIDENTIFIER, ForeignKey("dbo.WorkoutLogs.WorkoutLogId", ondelete="NO ACTION")
    )
    status: Mapped[str] = mapped_column("Status", String(20), default="pending", nullable=False)
    scheduled_date: Mapped[Optional[date]] = mapped_column("ScheduledDate", Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column("CompletedAt", DateTime)
    notes: Mapped[Optional[str]] = mapped_column("Notes", Text)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assignment: Mapped["UserProgramAssignment"] = relationship(back_populates="program_workout_logs")
    workout_log: Mapped[Optional["WorkoutLog"]] = relationship(back_populates="program_workout_logs")
