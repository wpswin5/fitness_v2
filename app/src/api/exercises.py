"""
Exercise Endpoints — CRUD, search, and ownership.
"""
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.auth.models import UserContext
from src.db.session import get_db
from src.models.exercises import (
    DifficultyLevel,
    ExerciseCreate,
    ExerciseResponse,
    ExerciseSummary,
    ExerciseUpdate,
    MuscleGroup,
)
from src.repositories.exercise_repository import ExerciseRepository
from src.repositories.user_repository import UserRepository

router = APIRouter(tags=["exercises"])
logger = logging.getLogger(__name__)


def _resolve_user_id(user: UserContext, db: Session) -> uuid.UUID:
    db_user = UserRepository(db).get_by_auth0_sub(user.auth0_sub)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user.user_id


def _to_response(e) -> ExerciseResponse:
    return ExerciseResponse(
        exercise_id=e.exercise_id,
        creator_id=e.creator_id,
        name=e.name,
        description=e.description,
        equipment_required=e.equipment_required.split(",") if e.equipment_required else None,
        primary_muscle_group=e.primary_muscle_group,
        difficulty_level=e.difficulty_level,
        instructions=e.instructions,
        created_at=e.created_at,
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get("/exercises", response_model=List[ExerciseResponse])
def search_exercises(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    muscle_group: Optional[MuscleGroup] = Query(None),
    difficulty: Optional[DifficultyLevel] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search / list exercises. All exercises are visible to all users."""
    repo = ExerciseRepository(db)
    exercises = repo.search(
        name=name,
        muscle_group=muscle_group,
        difficulty=difficulty,
        offset=offset,
        limit=limit,
    )
    return [_to_response(e) for e in exercises]


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single exercise by ID."""
    repo = ExerciseRepository(db)
    exercise = repo.get_by_id(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return _to_response(exercise)


@router.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(
    data: ExerciseCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new exercise owned by the current user."""
    user_id = _resolve_user_id(user, db)
    repo = ExerciseRepository(db)

    # Check for name collision
    existing = repo.get_by_name(data.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An exercise named '{data.name}' already exists",
        )

    exercise = repo.create_exercise(data, user_id)
    return _to_response(exercise)


@router.patch("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: uuid.UUID,
    data: ExerciseUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an exercise. Only the creator (or admin for system exercises) may edit."""
    user_id = _resolve_user_id(user, db)
    repo = ExerciseRepository(db)
    exercise = repo.get_by_id(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if not repo.is_owner(exercise, user_id) and not repo.is_system_exercise(exercise):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the exercise owner")
    updated = repo.update_exercise(exercise, data)
    return _to_response(updated)


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete an exercise. Only the creator may delete."""
    user_id = _resolve_user_id(user, db)
    repo = ExerciseRepository(db)
    exercise = repo.get_by_id(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    if not repo.is_owner(exercise, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the exercise owner")
    repo.delete(exercise)
