"""Workout log repository – logging completed workouts with nested sets/steps."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, joinedload

from src.db.orm_models import (
    SetLog,
    SetStepLog,
    WorkoutLog,
)
from src.models.logs import (
    WorkoutLogCreate,
    WorkoutLogUpdate,
    SetLogCreate,
    SetLogUpdate,
    SetStepLogCreate,
    SetStepLogUpdate,
)
from src.repositories.base import BaseRepository


class LogRepository(BaseRepository[WorkoutLog]):
    model = WorkoutLog

    # -- read ----------------------------------------------------------------

    def get_with_tree(self, workout_log_id: uuid.UUID) -> Optional[WorkoutLog]:
        """Load a workout log with its full set-log → step-log tree."""
        stmt = (
            select(WorkoutLog)
            .options(
                selectinload(WorkoutLog.set_logs)
                .selectinload(SetLog.step_logs),
                selectinload(WorkoutLog.set_logs)
                .joinedload(SetLog.exercise),
            )
            .where(WorkoutLog.workout_log_id == workout_log_id)
        )
        return self.db.execute(stmt).scalars().first()

    def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> List[WorkoutLog]:
        """Recent workout logs for a user (summaries, no nested tree)."""
        stmt = (
            select(WorkoutLog)
            .where(WorkoutLog.user_id == user_id)
            .order_by(WorkoutLog.start_time.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    # -- create (full tree) --------------------------------------------------

    def create_workout_log(
        self,
        data: WorkoutLogCreate,
        user_id: uuid.UUID,
        set_logs: Optional[List[SetLogCreate]] = None,
    ) -> WorkoutLog:
        """Create a workout log, optionally with nested set/step logs.

        The caller can also add set logs later via ``add_set_log``.
        """
        log = WorkoutLog(
            user_id=user_id,
            original_workout_id=data.original_workout_id,
            program_id=data.program_id,
            start_time=data.start_time,
            end_time=data.end_time,
            notes=data.notes,
        )
        self.db.add(log)
        self.db.flush()

        if set_logs:
            for sl_data in set_logs:
                self._add_set_log(log.workout_log_id, sl_data)

        self.db.flush()
        return self.get_with_tree(log.workout_log_id)  # type: ignore[return-value]

    # -- update --------------------------------------------------------------

    def finish_workout(
        self,
        log: WorkoutLog,
        data: WorkoutLogUpdate,
    ) -> WorkoutLog:
        """Mark a workout log as finished (set end_time, notes)."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(log, field, value)
        self.db.flush()
        self.db.refresh(log)
        return log

    # -- add set log to existing workout log ---------------------------------

    def add_set_log(
        self,
        workout_log_id: uuid.UUID,
        data: SetLogCreate,
    ) -> SetLog:
        """Append a set log (with step logs) to an existing workout log."""
        return self._add_set_log(workout_log_id, data)

    # -- private helpers -----------------------------------------------------

    def _add_set_log(
        self,
        workout_log_id: uuid.UUID,
        data: SetLogCreate,
    ) -> SetLog:
        set_log = SetLog(
            workout_log_id=workout_log_id,
            original_set_id=data.original_set_id,
            set_order=data.set_order,
            exercise_id=data.exercise_id,
            set_number=data.set_number,
        )
        self.db.add(set_log)
        self.db.flush()

        for step_data in data.steps:
            step_log = SetStepLog(
                set_log_id=set_log.set_log_id,
                original_set_step_id=step_data.original_set_step_id,
                step_order=step_data.step_order,
                completed_reps=step_data.completed_reps,
                completed_weight=step_data.completed_weight,
                completed_time_seconds=step_data.completed_time_seconds,
                rest_time_after_seconds=step_data.rest_time_after_seconds,
                notes=step_data.notes,
            )
            self.db.add(step_log)

        self.db.flush()
        self.db.refresh(set_log)
        return set_log

    # -- set log CRUD -------------------------------------------------------

    def get_set_log(self, set_log_id: uuid.UUID) -> Optional[SetLog]:
        """Get a single set log with its step logs."""
        stmt = (
            select(SetLog)
            .options(selectinload(SetLog.step_logs))
            .where(SetLog.set_log_id == set_log_id)
        )
        return self.db.execute(stmt).scalars().first()

    def update_set_log(self, set_log: SetLog, data) -> SetLog:
        """Update set log fields."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(set_log, field, value)
        self.db.flush()
        self.db.refresh(set_log)
        return set_log

    def delete_set_log(self, set_log: SetLog) -> None:
        """Delete a set log (and cascade to step logs)."""
        self.db.delete(set_log)
        self.db.flush()

    # -- step log CRUD ------------------------------------------------------

    def get_step_log(self, step_log_id: uuid.UUID) -> Optional[SetStepLog]:
        """Get a single step log."""
        stmt = select(SetStepLog).where(SetStepLog.set_step_log_id == step_log_id)
        return self.db.execute(stmt).scalars().first()

    def update_step_log(self, step_log: SetStepLog, data) -> SetStepLog:
        """Update step log fields."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(step_log, field, value)
        self.db.flush()
        self.db.refresh(step_log)
        return step_log

    def delete_step_log(self, step_log: SetStepLog) -> None:
        """Delete a step log."""
        self.db.delete(step_log)
        self.db.flush()
    def create_step_log(self, set_log_id: uuid.UUID, data: SetStepLogCreate) -> SetStepLog:
        """Create a new step log for an existing set log."""
        step_log = SetStepLog(
            set_log_id=set_log_id,
            original_set_step_id=data.original_set_step_id,
            step_order=data.step_order,
            completed_reps=data.completed_reps,
            completed_weight=data.completed_weight,
            completed_time_seconds=data.completed_time_seconds,
            rest_time_after_seconds=data.rest_time_after_seconds,
            notes=data.notes,
        )
        self.db.add(step_log)
        self.db.flush()
        self.db.refresh(step_log)
        return step_log