"""
User Management and Sync — uses UserRepository (SQLAlchemy).
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.auth.models import UserContext
from src.db.session import get_db
from src.models.users import UserCreate, UserResponse, UserUpdate
from src.repositories.user_repository import UserRepository

router = APIRouter(tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/users/sync", response_model=UserResponse)
def sync_user(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sync or create user from Auth0 token claims.
    Called on first login to store user in database.
    """
    try:
        repo = UserRepository(db)
        data = UserCreate(
            auth0_sub=user.auth0_sub,
            email=user.email or "",
            first_name=user.first_name,
            last_name=user.last_name,
        )
        db_user = repo.sync_user(data)
        logger.info(f"Synced user {user.auth0_sub} → {db_user.user_id}")
        return UserResponse(
            user_id=db_user.user_id,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            created_at=db_user.created_at,
        )
    except Exception as e:
        logger.error(f"Error syncing user {user.auth0_sub}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync user",
        ) from e


@router.get("/users/me", response_model=UserResponse)
def get_current_user_profile(
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current authenticated user's profile."""
    repo = UserRepository(db)
    db_user = repo.get_by_auth0_sub(user.auth0_sub)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(
        user_id=db_user.user_id,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        created_at=db_user.created_at,
    )


@router.patch("/users/me", response_model=UserResponse)
def update_current_user_profile(
    data: UserUpdate,
    user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile (first_name, last_name)."""
    repo = UserRepository(db)
    db_user = repo.get_by_auth0_sub(user.auth0_sub)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    updated = repo.update_profile(db_user, data)
    return UserResponse(
        user_id=updated.user_id,
        email=updated.email,
        first_name=updated.first_name,
        last_name=updated.last_name,
        created_at=updated.created_at,
    )

