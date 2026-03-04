"""
Fitness Endpoints — Workouts (templates) & workout logs.
All raw SQL replaced by SQLAlchemy repository layer.
"""
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.auth.models import UserContext
from src.db.session import get_db
from src.models.workouts import (
    WorkoutCreate,
    WorkoutResponse,
    WorkoutSummary,
    WorkoutUpdate,
    SetCreate,
    SetUpdate,
    SetResponse,
    SetStepResponse,
)
from src.models.exercises import ExerciseSummary
from src.models.logs import (
    WorkoutLogCreate,
    WorkoutLogResponse,
    WorkoutLogSummary,
    WorkoutLogUpdate,
    SetLogCreate,
    SetLogUpdate,
    SetLogResponse,
    SetStepLogCreate,
    SetStepLogUpdate,
    SetStepLogResponse,
)
from src.repositories.user_repository import UserRepository
from src.repositories.workout_repository import WorkoutRepository
from src.repositories.log_repository import LogRepository

router = APIRouter(tags=["fitness"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_user_id(user: UserContext, db: Session) -> uuid.UUID:
    """Look up the internal user_id from the Auth0 sub claim."""
    db_user = UserRepository(db).get_by_auth0_sub(user.auth0_sub)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found – call /users/sync first",
        )
    return db_user.user_id


def _workout_to_response(w) -> WorkoutResponse:
    """Map an ORM Workout (with eager-loaded tree) to the Pydantic response."""
    sets_list = getattr(w, "sets", []) or []
    return WorkoutResponse(
        workout_id=w.workout_id,
        creator_id=w.creator_id,
        name=w.name,
        description=w.description,
        is_shared=w.is_shared,
        created_at=w.created_at,
        sets=[
            SetResponse(
                set_id=s.set_id,
                set_order=s.set_order,
                exercise_id=s.exercise_id,
                num_sets=s.num_sets,
                rest_seconds=s.rest_seconds,
                notes=s.notes,
                steps=[
                    SetStepResponse(
                        set_step_id=st.set_step_id,
                        step_order=st.step_order,
                        planned_reps=st.planned_reps,
                        planned_weight=st.planned_weight,
                    )
                    for st in s.steps
                ],
                exercise=(
                    ExerciseSummary(
                        exercise_id=s.exercise.exercise_id,
                        name=s.exercise.name,
                        primary_muscle_group=s.exercise.primary_muscle_group,
                    )
                    if s.exercise
                    else None
                ),
            )
            for s in sets_list
        ],
    )


# ---------------------------------------------------------------------------
# Workout template CRUD
# ---------------------------------------------------------------------------

@router.post("/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    data: WorkoutCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new workout template with nested sets and steps.

    Sets may reference an existing exercise (``exercise_id``) or create one
    inline (``new_exercise``). See ``SetCreate`` for details.
    """
    user_id = _resolve_user_id(user, db)
    repo = WorkoutRepository(db)
    try:
        workout = repo.create_workout(data, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return _workout_to_response(workout)


@router.get("/workouts", response_model=List[WorkoutSummary])
def list_workouts(
    shared: bool = Query(False, description="If true, list public workouts instead of own"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List workout summaries (own or shared)."""
    repo = WorkoutRepository(db)
    if shared:
        workouts = repo.list_shared(offset=offset, limit=limit)
    else:
        user_id = _resolve_user_id(user, db)
        workouts = repo.list_by_creator(user_id, offset=offset, limit=limit)

    return [
        WorkoutSummary(
            workout_id=w.workout_id,
            name=w.name,
            is_shared=w.is_shared,
            created_at=w.created_at,
        )
        for w in workouts
    ]


@router.get("/workouts/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single workout with its full set/step tree."""
    repo = WorkoutRepository(db)
    workout = repo.get_with_tree(workout_id)
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return _workout_to_response(workout)


@router.patch("/workouts/{workout_id}", response_model=WorkoutResponse)
def update_workout(
    workout_id: uuid.UUID,
    data: WorkoutUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update top-level workout fields."""
    user_id = _resolve_user_id(user, db)
    repo = WorkoutRepository(db)
    workout = repo.get_with_tree(workout_id)
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    if workout.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the workout owner")
    updated = repo.update_workout(workout, data)
    return _workout_to_response(updated)


@router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete a workout."""
    user_id = _resolve_user_id(user, db)
    repo = WorkoutRepository(db)
    workout = repo.get_by_id(workout_id)
    if workout is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    if workout.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the workout owner")
    repo.delete(workout)


# ---------------------------------------------------------------------------
# Workout logging (sessions)
# ---------------------------------------------------------------------------

def _log_to_response(log) -> WorkoutLogResponse:
    set_logs_list = getattr(log, "set_logs", []) or []
    return WorkoutLogResponse(
        workout_log_id=log.workout_log_id,
        user_id=log.user_id,
        original_workout_id=log.original_workout_id,
        program_id=log.program_id,
        start_time=log.start_time,
        end_time=log.end_time,
        total_duration_minutes=log.total_duration_minutes,
        notes=log.notes,
        set_logs=[
            SetLogResponse(
                set_log_id=sl.set_log_id,
                original_set_id=sl.original_set_id,
                set_order=sl.set_order,
                exercise_id=sl.exercise_id,
                set_number=sl.set_number,
                steps=[
                    SetStepLogResponse(
                        set_step_log_id=stl.set_step_log_id,
                        original_set_step_id=stl.original_set_step_id,
                        step_order=stl.step_order,
                        completed_reps=stl.completed_reps,
                        completed_weight=stl.completed_weight,
                        completed_time_seconds=stl.completed_time_seconds,
                        rest_time_after_seconds=stl.rest_time_after_seconds,
                        notes=stl.notes,
                    )
                    for stl in sl.step_logs
                ],
                exercise=(
                    ExerciseSummary(
                        exercise_id=sl.exercise.exercise_id,
                        name=sl.exercise.name,
                        primary_muscle_group=sl.exercise.primary_muscle_group,
                    )
                    if sl.exercise
                    else None
                ),
            )
            for sl in set_logs_list
        ],
    )


@router.post("/workouts/logs", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
def start_workout_log(
    data: WorkoutLogCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new workout log session."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    log = repo.create_workout_log(data, user_id)
    return _log_to_response(log)


@router.get("/workouts/logs", response_model=List[WorkoutLogSummary])
def list_workout_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List workout log summaries for the current user."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    logs = repo.list_by_user(user_id, offset=offset, limit=limit)
    return [
        WorkoutLogSummary(
            workout_log_id=l.workout_log_id,
            start_time=l.start_time,
            end_time=l.end_time,
            total_duration_minutes=l.total_duration_minutes,
            original_workout_id=l.original_workout_id,
        )
        for l in logs
    ]


@router.get("/workouts/logs/{log_id}", response_model=WorkoutLogResponse)
def get_workout_log(
    log_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single workout log with its full set/step tree."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    return _log_to_response(log)


@router.patch("/workouts/logs/{log_id}", response_model=WorkoutLogResponse)
def finish_workout_log(
    log_id: uuid.UUID,
    data: WorkoutLogUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Finish a workout log (set end_time, notes)."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    updated = repo.finish_workout(log, data)
    return _log_to_response(updated)


# ---------------------------------------------------------------------------
# Nested CRUD: Workout Sets
# ---------------------------------------------------------------------------

@router.post("/workouts/{workout_id}/sets", response_model=SetResponse)
def create_workout_set(
    workout_id: uuid.UUID,
    data: SetCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new set within a workout template."""
    user_id = _resolve_user_id(user, db)
    repo = WorkoutRepository(db)
    
    # Verify ownership
    workout = repo.get_by_id(workout_id)
    if workout is None or workout.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    
    set_obj = repo.create_set(workout_id, data, user_id)
    return SetResponse.model_validate(set_obj)


@router.patch("/workouts/{workout_id}/sets/{set_id}", response_model=SetResponse)
def update_workout_set(
    workout_id: uuid.UUID,
    set_id: uuid.UUID,
    data: SetUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a set within a workout template."""
    user_id = _resolve_user_id(user, db)
    repo = WorkoutRepository(db)
    
    # Verify ownership
    workout = repo.get_by_id(workout_id)
    if workout is None or workout.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    
    # Fetch the set
    set_obj = repo.get_set(set_id)
    if set_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found")
    
    updated_set = repo.update_set(set_obj, data)
    return SetResponse.model_validate(updated_set)


@router.delete("/workouts/{workout_id}/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_set(
    workout_id: uuid.UUID,
    set_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a set from a workout template."""
    user_id = _resolve_user_id(user, db)
    repo = WorkoutRepository(db)
    
    # Verify ownership
    workout = repo.get_by_id(workout_id)
    if workout is None or workout.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    
    # Fetch the set
    set_obj = repo.get_set(set_id)
    if set_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found")
    
    repo.delete_set(set_obj)



# ---------------------------------------------------------------------------
# Nested CRUD: Workout Log Sets & Steps
# ---------------------------------------------------------------------------

@router.post("/workouts/logs/{log_id}/sets", response_model=SetLogResponse)
def add_set_log(
    log_id: uuid.UUID,
    data: SetLogCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a set log mid-workout (reuse from template or create inline)."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    
    # Verify ownership
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    set_log = repo.add_set_log(log_id, data)
    return SetLogResponse.model_validate(set_log)



@router.patch("/workouts/logs/{log_id}/sets/{set_log_id}", response_model=SetLogResponse)
def update_set_log(
    log_id: uuid.UUID,
    set_log_id: uuid.UUID,
    data: SetLogUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a set log during/after workout."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    
    # Verify ownership
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    # Fetch the set log
    set_log = repo.get_set_log(set_log_id)
    if set_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set log not found")
    
    updated_set_log = repo.update_set_log(set_log, data)
    return SetLogResponse.model_validate(updated_set_log)


@router.delete("/workouts/logs/{log_id}/sets/{set_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set_log(
    log_id: uuid.UUID,
    set_log_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a set log from a workout."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    
    # Verify ownership
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    # Fetch the set log
    set_log = repo.get_set_log(set_log_id)
    if set_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set log not found")
    
    repo.delete_set_log(set_log)


@router.post("/workouts/logs/{log_id}/sets/{set_log_id}/steps", response_model=SetStepLogResponse)
def add_step_log(
    log_id: uuid.UUID,
    set_log_id: uuid.UUID,
    data: SetStepLogCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a step log to a set log during/after workout."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    
    # Verify ownership
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    step_log = repo.create_step_log(set_log_id, data)
    return SetStepLogResponse.model_validate(step_log)


@router.patch("/workouts/logs/{log_id}/sets/{set_log_id}/steps/{step_log_id}", response_model=SetStepLogResponse)
def update_step_log(
    log_id: uuid.UUID,
    set_log_id: uuid.UUID,
    step_log_id: uuid.UUID,
    data: SetStepLogUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a step log during/after workout."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    
    # Verify ownership
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    # Fetch the step log
    step_log = repo.get_step_log(step_log_id)
    if step_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step log not found")
    
    updated_step_log = repo.update_step_log(step_log, data)
    return SetStepLogResponse.model_validate(updated_step_log)


@router.delete("/workouts/logs/{log_id}/sets/{set_log_id}/steps/{step_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step_log(
    log_id: uuid.UUID,
    set_log_id: uuid.UUID,
    step_log_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a step log from a set log."""
    user_id = _resolve_user_id(user, db)
    repo = LogRepository(db)
    
    # Verify ownership
    log = repo.get_with_tree(log_id)
    if log is None or log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    
    # Fetch the step log
    step_log = repo.get_step_log(step_log_id)
    if step_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step log not found")
    
    repo.delete_step_log(step_log)
