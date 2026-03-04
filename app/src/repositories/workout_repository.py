"""Workout repository – full tree CRUD (workout → sets → set steps).

Supports the inline-exercise creation flow: when a set's ``new_exercise``
field is populated instead of ``exercise_id``, the exercise is created first
and the generated ID is wired in — all within a single transaction.
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.db.orm_models import Exercise, Set, SetStep, Workout
from src.models.exercises import ExerciseCreate
from src.models.workouts import WorkoutCreate, WorkoutUpdate, SetCreate
from src.repositories.base import BaseRepository
from src.repositories.exercise_repository import ExerciseRepository


class WorkoutRepository(BaseRepository[Workout]):
    model = Workout

    def __init__(self, db: Session):
        super().__init__(db)
        self._exercise_repo = ExerciseRepository(db)

    # -- read ----------------------------------------------------------------

    def get_with_tree(self, workout_id: uuid.UUID) -> Optional[Workout]:
        """Load a workout with its full set → step tree eagerly."""
        stmt = (
            select(Workout)
            .options(
                selectinload(Workout.sets)
                .selectinload(Set.steps),
                selectinload(Workout.sets)
                .joinedload(Set.exercise),
            )
            .where(Workout.workout_id == workout_id)
        )
        stmt = self._active_filter(stmt)
        return self.db.execute(stmt).scalars().first()

    def list_by_creator(
        self,
        creator_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Workout]:
        """Workouts owned by a user (summary — no nested tree)."""
        stmt = (
            select(Workout)
            .where(Workout.creator_id == creator_id)
        )
        stmt = self._active_filter(stmt)
        stmt = stmt.order_by(Workout.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def list_shared(self, *, offset: int = 0, limit: int = 50) -> List[Workout]:
        """Publicly shared workouts."""
        stmt = (
            select(Workout)
            .where(Workout.is_shared.is_(True))
        )
        stmt = self._active_filter(stmt)
        stmt = stmt.order_by(Workout.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    # -- create (full tree) --------------------------------------------------

    def create_workout(
        self,
        data: WorkoutCreate,
        creator_id: uuid.UUID,
    ) -> Workout:
        """Create a workout together with all nested sets and steps.

        For each set:
        - If ``exercise_id`` is given, validate it exists.
        - If ``new_exercise`` is given, create the exercise first.
        Everything happens in the caller's session (single transaction).
        """
        workout = Workout(
            creator_id=creator_id,
            name=data.name,
            description=data.description,
            is_shared=data.is_shared,
        )
        self.db.add(workout)
        self.db.flush()  # gives us workout.workout_id

        for set_data in data.sets:
            exercise_id = self._resolve_exercise(set_data, creator_id)
            db_set = Set(
                workout_id=workout.workout_id,
                set_order=set_data.set_order,
                exercise_id=exercise_id,
                num_sets=set_data.num_sets,
                rest_seconds=set_data.rest_seconds,
                notes=set_data.notes,
            )
            self.db.add(db_set)
            self.db.flush()

            for step_data in set_data.steps:
                db_step = SetStep(
                    set_id=db_set.set_id,
                    step_order=step_data.step_order,
                    planned_reps=step_data.planned_reps,
                    planned_weight=step_data.planned_weight,
                )
                self.db.add(db_step)

        self.db.flush()
        # Return fully-loaded tree
        return self.get_with_tree(workout.workout_id)  # type: ignore[return-value]

    # -- update --------------------------------------------------------------

    def update_workout(self, workout: Workout, data: WorkoutUpdate) -> Workout:
        """Patch top-level workout fields (name, description, is_shared)."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workout, field, value)
        self.db.flush()
        self.db.refresh(workout)
        return workout

    # -- private helpers -----------------------------------------------------

    def _resolve_exercise(
        self, set_data: SetCreate, creator_id: uuid.UUID
    ) -> uuid.UUID:
        """Return an exercise_id — either the one supplied or from a newly created exercise."""
        if set_data.exercise_id is not None:
            # Validate existence
            exercise = self._exercise_repo.get_by_id(set_data.exercise_id)
            if exercise is None:
                raise ValueError(
                    f"Exercise {set_data.exercise_id} not found or has been deleted."
                )
            return exercise.exercise_id

        # ``new_exercise`` must be set (Pydantic validator guarantees one-of)
        assert set_data.new_exercise is not None
        exercise = self._exercise_repo.create_exercise(
            set_data.new_exercise, creator_id
        )
        return exercise.exercise_id
