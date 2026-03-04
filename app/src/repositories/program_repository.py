"""Program & assignment repositories."""

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.db.orm_models import (
    Program,
    ProgramWorkout,
    ProgramWorkoutLog,
    UserProgramAssignment,
    Workout,
)
from src.models.programs import ProgramCreate, ProgramUpdate
from src.models.program_assignments import (
    AssignmentStatus,
    ProgramWorkoutLogCreate,
    ProgramWorkoutLogUpdate,
    UserProgramAssignmentCreate,
    UserProgramAssignmentUpdate,
    WorkoutLogStatus,
)
from src.repositories.base import BaseRepository


# ============================================================================
# Program Repository
# ============================================================================

class ProgramRepository(BaseRepository[Program]):
    model = Program

    # -- read ----------------------------------------------------------------

    def get_with_schedule(self, program_id: uuid.UUID) -> Optional[Program]:
        """Load a program with its full schedule (ProgramWorkouts)."""
        stmt = (
            select(Program)
            .options(
                selectinload(Program.program_workouts)
                .joinedload(ProgramWorkout.workout),
            )
            .where(Program.program_id == program_id)
        )
        stmt = self._active_filter(stmt)
        return self.db.execute(stmt).scalars().first()

    def list_by_creator(
        self,
        creator_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Program]:
        stmt = (
            select(Program)
            .where(Program.creator_id == creator_id)
        )
        stmt = self._active_filter(stmt)
        stmt = stmt.order_by(Program.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def list_shared(self, *, offset: int = 0, limit: int = 50) -> List[Program]:
        stmt = (
            select(Program)
            .where(Program.is_shared == True)
        )
        stmt = self._active_filter(stmt)
        stmt = stmt.order_by(Program.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    # -- create (with schedule) ----------------------------------------------

    def create_program(
        self,
        data: ProgramCreate,
        creator_id: uuid.UUID,
    ) -> Program:
        program = Program(
            creator_id=creator_id,
            name=data.name,
            description=data.description,
            is_shared=data.is_shared,
            duration_weeks=data.duration_weeks,
        )
        self.db.add(program)
        self.db.flush()

        for slot in data.schedule:
            pw = ProgramWorkout(
                program_id=program.program_id,
                week_number=slot.week_number,
                day_of_week=slot.day_of_week,
                workout_id=slot.workout_id,
                is_rest_day=slot.is_rest_day,
            )
            self.db.add(pw)

        self.db.flush()
        return self.get_with_schedule(program.program_id)  # type: ignore[return-value]

    # -- update --------------------------------------------------------------

    def update_program(self, program: Program, data: ProgramUpdate) -> Program:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(program, field, value)
        self.db.flush()
        self.db.refresh(program)
        return program


# ============================================================================
# Assignment Repository
# ============================================================================

class ProgramAssignmentRepository(BaseRepository[UserProgramAssignment]):
    model = UserProgramAssignment

    # -- read ----------------------------------------------------------------

    def get_with_logs(self, assignment_id: uuid.UUID) -> Optional[UserProgramAssignment]:
        stmt = (
            select(UserProgramAssignment)
            .options(selectinload(UserProgramAssignment.program_workout_logs))
            .where(UserProgramAssignment.assignment_id == assignment_id)
        )
        return self.db.execute(stmt).scalars().first()

    def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        status: Optional[AssignmentStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[UserProgramAssignment]:
        stmt = select(UserProgramAssignment).where(
            UserProgramAssignment.user_id == user_id
        )
        if status is not None:
            stmt = stmt.where(UserProgramAssignment.status == status.value)
        stmt = stmt.order_by(UserProgramAssignment.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_active_for_program(
        self,
        user_id: uuid.UUID,
        program_id: uuid.UUID,
    ) -> Optional[UserProgramAssignment]:
        """Find an active assignment for a given user + program."""
        stmt = (
            select(UserProgramAssignment)
            .where(
                UserProgramAssignment.user_id == user_id,
                UserProgramAssignment.program_id == program_id,
                UserProgramAssignment.status == AssignmentStatus.ACTIVE.value,
            )
        )
        return self.db.execute(stmt).scalars().first()

    # -- enroll --------------------------------------------------------------

    def enroll(
        self,
        data: UserProgramAssignmentCreate,
        user_id: uuid.UUID,
    ) -> UserProgramAssignment:
        """Enrol a user in a program, auto-generating ProgramWorkoutLog slots."""
        assignment = UserProgramAssignment(
            user_id=user_id,
            program_id=data.program_id,
            start_date=data.start_date,
        )
        self.db.add(assignment)
        self.db.flush()

        # Auto-create pending log slots for every non-rest-day in the program schedule
        schedule_stmt = select(ProgramWorkout).where(
            ProgramWorkout.program_id == data.program_id,
            ProgramWorkout.is_rest_day.is_(False),
        )
        schedule_entries = list(self.db.execute(schedule_stmt).scalars().all())

        for entry in schedule_entries:
            log = ProgramWorkoutLog(
                assignment_id=assignment.assignment_id,
                week_number=entry.week_number,
                day_of_week=entry.day_of_week,
                status="pending",
            )
            self.db.add(log)

        self.db.flush()
        return self.get_with_logs(assignment.assignment_id)  # type: ignore[return-value]

    # -- update status -------------------------------------------------------

    def update_assignment(
        self,
        assignment: UserProgramAssignment,
        data: UserProgramAssignmentUpdate,
    ) -> UserProgramAssignment:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                value = value.value if isinstance(value, AssignmentStatus) else value
            setattr(assignment, field, value)
        if assignment.status == AssignmentStatus.COMPLETED.value:
            assignment.completed_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(assignment)
        return assignment

    # -- workout log updates -------------------------------------------------

    def update_workout_log(
        self,
        log: ProgramWorkoutLog,
        data: ProgramWorkoutLogUpdate,
    ) -> ProgramWorkoutLog:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                value = value.value if isinstance(value, WorkoutLogStatus) else value
            setattr(log, field, value)
        if log.status == WorkoutLogStatus.COMPLETED.value:
            log.completed_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(log)
        return log

    def get_workout_log(
        self,
        log_id: uuid.UUID,
    ) -> Optional[ProgramWorkoutLog]:
        stmt = select(ProgramWorkoutLog).where(
            ProgramWorkoutLog.program_workout_log_id == log_id
        )
        return self.db.execute(stmt).scalars().first()

    # -- progress ------------------------------------------------------------

    def get_progress_counts(
        self, assignment_id: uuid.UUID
    ) -> dict:
        """Return {total, completed, skipped, pending} counts."""
        base = select(
            func.count().label("total"),
            func.count().filter(
                ProgramWorkoutLog.status == WorkoutLogStatus.COMPLETED.value
            ).label("completed"),
            func.count().filter(
                ProgramWorkoutLog.status == WorkoutLogStatus.SKIPPED.value
            ).label("skipped"),
            func.count().filter(
                ProgramWorkoutLog.status == WorkoutLogStatus.PENDING.value
            ).label("pending"),
        ).where(ProgramWorkoutLog.assignment_id == assignment_id)

        row = self.db.execute(base).one()
        return {
            "total": row.total,
            "completed": row.completed,
            "skipped": row.skipped,
            "pending": row.pending,
        }

    # -- program workout log CRUD -------------------------------------------

    def get_program_workout_log(
        self, log_id: uuid.UUID
    ) -> Optional[ProgramWorkoutLog]:
        """Get a single program workout log."""
        stmt = select(ProgramWorkoutLog).where(
            ProgramWorkoutLog.program_workout_log_id == log_id
        )
        return self.db.execute(stmt).scalars().first()

    def update_program_workout_log(
        self, log_id: uuid.UUID, data: ProgramWorkoutLogUpdate
    ) -> Optional[ProgramWorkoutLog]:
        """Update a program workout log (status, notes, completed_at)."""
        log = self.get_program_workout_log(log_id)
        if log is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(log, field, value)
        self.db.flush()
        self.db.refresh(log)
        return log
