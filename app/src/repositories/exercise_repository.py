"""Exercise repository – CRUD, search, and ownership checks."""

import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.db.orm_models import Exercise
from src.models.exercises import ExerciseCreate, ExerciseUpdate, MuscleGroup, DifficultyLevel
from src.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise]):
    model = Exercise

    # -- search / filter -----------------------------------------------------

    def search(
        self,
        *,
        name: Optional[str] = None,
        muscle_group: Optional[MuscleGroup] = None,
        difficulty: Optional[DifficultyLevel] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Exercise]:
        """Search exercises with optional filters.

        All exercises are visible to all users regardless of creator.
        """
        stmt = select(Exercise)
        stmt = self._active_filter(stmt)

        if name:
            stmt = stmt.where(Exercise.name.ilike(f"%{name}%"))
        if muscle_group:
            stmt = stmt.where(Exercise.primary_muscle_group == muscle_group.value)
        if difficulty:
            stmt = stmt.where(Exercise.difficulty_level == difficulty.value)

        stmt = stmt.order_by(Exercise.name).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_name(self, name: str) -> Optional[Exercise]:
        """Exact (case-insensitive) name lookup."""
        stmt = (
            select(Exercise)
            .where(Exercise.name.ilike(name))
        )
        stmt = self._active_filter(stmt)
        return self.db.execute(stmt).scalars().first()

    # -- create --------------------------------------------------------------

    def create_exercise(self, data: ExerciseCreate, creator_id: uuid.UUID) -> Exercise:
        """Create a new exercise owned by ``creator_id``."""
        exercise = Exercise(
            creator_id=creator_id,
            name=data.name,
            description=data.description,
            equipment_required=(
                ",".join(data.equipment_required)
                if data.equipment_required
                else None
            ),
            primary_muscle_group=(
                data.primary_muscle_group.value if data.primary_muscle_group else None
            ),
            difficulty_level=(
                data.difficulty_level.value if data.difficulty_level else None
            ),
            instructions=data.instructions,
        )
        return self.create(exercise)

    # -- update --------------------------------------------------------------

    def update_exercise(
        self,
        exercise: Exercise,
        data: ExerciseUpdate,
    ) -> Exercise:
        """Patch a subset of fields on an existing exercise."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "equipment_required" and value is not None:
                value = ",".join(value)
            if field == "primary_muscle_group" and value is not None:
                value = value.value if isinstance(value, MuscleGroup) else value
            if field == "difficulty_level" and value is not None:
                value = value.value if isinstance(value, DifficultyLevel) else value
            setattr(exercise, field, value)
        self.db.flush()
        self.db.refresh(exercise)
        return exercise

    # -- ownership -----------------------------------------------------------

    def is_owner(self, exercise: Exercise, user_id: uuid.UUID) -> bool:
        """Check whether ``user_id`` is the creator (or if it's a system exercise)."""
        return exercise.creator_id == user_id

    def is_system_exercise(self, exercise: Exercise) -> bool:
        """System-seeded exercises have ``creator_id IS NULL``."""
        return exercise.creator_id is None
