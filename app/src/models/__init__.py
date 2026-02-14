"""Pydantic models for the Fitness API.

This module provides all data models organized by domain:
- users: User accounts and Auth0 integration
- exercises: Master exercise definitions
- workouts: Workout templates, sets, and set steps
- programs: Training programs and scheduling
- logs: Workout logging and performance tracking
"""

# Base utilities
from .base import (
    DBModelBase,
    TimestampMixin,
    CreatedAtMixin,
)

# User models
from .users import (
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
)

# Exercise models
from .exercises import (
    DifficultyLevel,
    MuscleGroup,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseInDB,
    ExerciseResponse,
    ExerciseSummary,
)

# Workout models (includes Sets and SetSteps)
from .workouts import (
    SetStepCreate,
    SetStepUpdate,
    SetStepInDB,
    SetStepResponse,
    SetCreate,
    SetUpdate,
    SetInDB,
    SetResponse,
    SetSummary,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutInDB,
    WorkoutResponse,
    WorkoutSummary,
)

# Program models (includes ProgramWorkouts)
from .programs import (
    DayOfWeek,
    ProgramWorkoutCreate,
    ProgramWorkoutInDB,
    ProgramWorkoutResponse,
    ProgramCreate,
    ProgramUpdate,
    ProgramInDB,
    ProgramResponse,
    ProgramSummary,
)

# Log models
from .logs import (
    SetStepLogCreate,
    SetStepLogInDB,
    SetStepLogResponse,
    SetLogCreate,
    SetLogInDB,
    SetLogResponse,
    SetLogSummary,
    WorkoutLogCreate,
    WorkoutLogUpdate,
    WorkoutLogInDB,
    WorkoutLogResponse,
    WorkoutLogSummary,
    ExercisePerformance,
    WorkoutStats,
)

__all__ = [
    # Base
    "DBModelBase",
    "TimestampMixin",
    "CreatedAtMixin",
    # Users
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    # Exercises
    "DifficultyLevel",
    "MuscleGroup",
    "ExerciseCreate",
    "ExerciseUpdate",
    "ExerciseInDB",
    "ExerciseResponse",
    "ExerciseSummary",
    # SetSteps
    "SetStepCreate",
    "SetStepUpdate",
    "SetStepInDB",
    "SetStepResponse",
    # Sets
    "SetCreate",
    "SetUpdate",
    "SetInDB",
    "SetResponse",
    "SetSummary",
    # Workouts
    "WorkoutCreate",
    "WorkoutUpdate",
    "WorkoutInDB",
    "WorkoutResponse",
    "WorkoutSummary",
    # ProgramWorkouts
    "DayOfWeek",
    "ProgramWorkoutCreate",
    "ProgramWorkoutInDB",
    "ProgramWorkoutResponse",
    # Programs
    "ProgramCreate",
    "ProgramUpdate",
    "ProgramInDB",
    "ProgramResponse",
    "ProgramSummary",
    # SetStepLogs
    "SetStepLogCreate",
    "SetStepLogInDB",
    "SetStepLogResponse",
    # SetLogs
    "SetLogCreate",
    "SetLogInDB",
    "SetLogResponse",
    "SetLogSummary",
    # WorkoutLogs
    "WorkoutLogCreate",
    "WorkoutLogUpdate",
    "WorkoutLogInDB",
    "WorkoutLogResponse",
    "WorkoutLogSummary",
    # Analytics
    "ExercisePerformance",
    "WorkoutStats",
]
