"""
Program Endpoints — CRUD for programs and program assignments.
"""
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.auth.models import UserContext
from src.db.session import get_db
from src.models.programs import (
    ProgramCreate,
    ProgramResponse,
    ProgramSummary,
    ProgramUpdate,
    ProgramWorkoutResponse,
)
from src.models.program_assignments import (
    AssignmentStatus,
    ProgramProgress,
    ProgramWorkoutLogResponse,
    ProgramWorkoutLogUpdate,
    UserProgramAssignmentCreate,
    UserProgramAssignmentResponse,
    UserProgramAssignmentSummary,
    UserProgramAssignmentUpdate,
)
from src.models.workouts import WorkoutSummary
from src.repositories.program_repository import ProgramAssignmentRepository, ProgramRepository
from src.repositories.user_repository import UserRepository

router = APIRouter(tags=["programs"])
logger = logging.getLogger(__name__)


def _resolve_user_id(user: UserContext, db: Session) -> uuid.UUID:
    db_user = UserRepository(db).get_by_auth0_sub(user.auth0_sub)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user.user_id


def _program_to_response(p) -> ProgramResponse:
    schedule = getattr(p, "program_workouts", []) or []
    return ProgramResponse(
        program_id=p.program_id,
        creator_id=p.creator_id,
        name=p.name,
        description=p.description,
        is_shared=p.is_shared,
        duration_weeks=p.duration_weeks,
        created_at=p.created_at,
        schedule=[
            ProgramWorkoutResponse(
                week_number=pw.week_number,
                day_of_week=pw.day_of_week,
                is_rest_day=pw.is_rest_day,
                workout=(
                    WorkoutSummary(
                        workout_id=pw.workout.workout_id,
                        name=pw.workout.name,
                        is_shared=pw.workout.is_shared,
                        created_at=pw.workout.created_at,
                    )
                    if pw.workout
                    else None
                ),
            )
            for pw in schedule
        ],
    )


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------

@router.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    data: ProgramCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a program with its workout schedule."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramRepository(db)
    program = repo.create_program(data, user_id)
    return _program_to_response(program)


@router.get("/programs", response_model=List[ProgramSummary])
def list_programs(
    shared: bool = Query(False),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List programs (own or shared)."""
    repo = ProgramRepository(db)
    if shared:
        programs = repo.list_shared(offset=offset, limit=limit)
    else:
        user_id = _resolve_user_id(user, db)
        programs = repo.list_by_creator(user_id, offset=offset, limit=limit)
    return [
        ProgramSummary(
            program_id=p.program_id,
            name=p.name,
            duration_weeks=p.duration_weeks,
            is_shared=p.is_shared,
            created_at=p.created_at,
        )
        for p in programs
    ]


@router.get("/programs/{program_id}", response_model=ProgramResponse)
def get_program(
    program_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a program with its full schedule."""
    repo = ProgramRepository(db)
    program = repo.get_with_schedule(program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return _program_to_response(program)


@router.patch("/programs/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: uuid.UUID,
    data: ProgramUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a program's top-level fields."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramRepository(db)
    program = repo.get_with_schedule(program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    if program.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the program owner")
    updated = repo.update_program(program, data)
    return _program_to_response(updated)


@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete a program."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramRepository(db)
    program = repo.get_by_id(program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    if program.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the program owner")
    repo.delete(program)


# ---------------------------------------------------------------------------
# Program Assignments
# ---------------------------------------------------------------------------

@router.post("/programs/{program_id}/enroll", response_model=UserProgramAssignmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_program(
    program_id: uuid.UUID,
    data: UserProgramAssignmentCreate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enrol the current user in a program."""
    user_id = _resolve_user_id(user, db)
    # Validate program exists
    p_repo = ProgramRepository(db)
    if p_repo.get_by_id(program_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    # Check for existing active assignment
    a_repo = ProgramAssignmentRepository(db)
    existing = a_repo.get_active_for_program(user_id, program_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already enrolled in this program",
        )
    # Override program_id from path
    data.program_id = program_id
    assignment = a_repo.enroll(data, user_id)
    return _assignment_to_response(assignment)


@router.get("/programs/assignments", response_model=List[UserProgramAssignmentSummary])
def list_assignments(
    assignment_status: Optional[AssignmentStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's program assignments."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramAssignmentRepository(db)
    assignments = repo.list_by_user(user_id, status=assignment_status, offset=offset, limit=limit)
    return [
        UserProgramAssignmentSummary(
            assignment_id=a.assignment_id,
            program_id=a.program_id,
            status=AssignmentStatus(a.status),
            start_date=a.start_date,
            current_week=a.current_week,
            current_day_of_week=a.current_day_of_week,
            created_at=a.created_at,
        )
        for a in assignments
    ]


@router.get("/programs/assignments/{assignment_id}", response_model=UserProgramAssignmentResponse)
def get_assignment(
    assignment_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single assignment with its workout logs."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramAssignmentRepository(db)
    assignment = repo.get_with_logs(assignment_id)
    if assignment is None or assignment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    return _assignment_to_response(assignment)


@router.patch("/programs/assignments/{assignment_id}", response_model=UserProgramAssignmentResponse)
def update_assignment(
    assignment_id: uuid.UUID,
    data: UserProgramAssignmentUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update assignment status (pause, resume, complete, abandon)."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramAssignmentRepository(db)
    assignment = repo.get_with_logs(assignment_id)
    if assignment is None or assignment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    updated = repo.update_assignment(assignment, data)
    return _assignment_to_response(updated)


@router.get("/programs/assignments/{assignment_id}/progress", response_model=ProgramProgress)
def get_assignment_progress(
    assignment_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get calculated progress for an assignment."""
    user_id = _resolve_user_id(user, db)
    repo = ProgramAssignmentRepository(db)
    assignment = repo.get_by_id(assignment_id)
    if assignment is None or assignment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    counts = repo.get_progress_counts(assignment_id)
    return ProgramProgress(
        assignment_id=assignment_id,
        program_id=assignment.program_id,
        **counts,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assignment_to_response(a) -> UserProgramAssignmentResponse:
    logs = getattr(a, "program_workout_logs", []) or []
    return UserProgramAssignmentResponse(
        assignment_id=a.assignment_id,
        user_id=a.user_id,
        program_id=a.program_id,
        status=AssignmentStatus(a.status),
        start_date=a.start_date,
        current_week=a.current_week,
        current_day_of_week=a.current_day_of_week,
        completed_at=a.completed_at,
        created_at=a.created_at,
        workout_logs=[
            ProgramWorkoutLogResponse(
                program_workout_log_id=l.program_workout_log_id,
                assignment_id=l.assignment_id,
                week_number=l.week_number,
                day_of_week=l.day_of_week,
                status=l.status,
                scheduled_date=l.scheduled_date,
                workout_log_id=l.workout_log_id,
                completed_at=l.completed_at,
                notes=l.notes,
            )
            for l in logs
        ],
    )
