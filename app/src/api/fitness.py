"""
Fitness Endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.auth.dependencies import get_current_user
from src.auth.models import UserContext
from src.db.query import execute_query

router = APIRouter(tags=["fitness"])
logger = logging.getLogger(__name__)


class WorkoutSession(BaseModel):
    """Request/Response model for workout logging"""
    id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_minutes: Optional[int] = None
    notes: Optional[str] = None


@router.get("/workouts", response_model=List[WorkoutSession])
async def get_workout_logs(user: UserContext = Depends(get_current_user)):
    """
    Get all workout logs for authenticated user, sorted by most recent
    """
    try:
        query = """
        SELECT wl.WorkoutLogId, wl.StartTime, wl.EndTime, wl.TotalDurationMinutes, wl.Notes
        FROM [dbo].[WorkoutLogs] wl
        ORDER BY wl.StartTime DESC
        """
        
        results = execute_query(query, ())
        
        if not results:
            return []
        
        sessions = [
            WorkoutSession(
                id=str(row["WorkoutLogId"]),
                start_time=row["StartTime"],
                end_time=row["EndTime"],
                total_duration_minutes=row["TotalDurationMinutes"],
                notes=row["Notes"],
            )
            for row in results
        ]
        
        return sessions
        
    except Exception as e:
        logger.error(f"Error fetching workout logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch workout logs",
        ) from e


@router.post("/workouts/start", response_model=WorkoutSession)
async def start_workout_session(
    session: WorkoutSession,
    user: UserContext = Depends(get_current_user)
):
    """
    Create a new workout log session for authenticated user
    """
    try:
        # Get user ID from Auth0Sub
        user_query = "SELECT UserId FROM [dbo].[Users] WHERE Auth0Sub = ?"
        user_result = execute_query(user_query, (user.auth0_sub,))
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        user_id = user_result[0]["UserId"]
        
        # Insert workout log
        insert_query = """
        INSERT INTO [dbo].[WorkoutLogs] 
            (UserId, StartTime, EndTime, Notes, CreatedAt)
        OUTPUT inserted.WorkoutLogId, inserted.StartTime, inserted.EndTime, inserted.TotalDurationMinutes, inserted.Notes
        VALUES (?, ?, ?, ?, GETUTCDATE())
        """
        
        start_time = session.start_time or datetime.utcnow()
        
        result = execute_query(
            insert_query,
            (
                user_id,
                start_time,
                session.end_time,
                session.notes,
            ),
        )
        
        if result:
            new_session = WorkoutSession(
                id=str(result[0]["WorkoutLogId"]),
                start_time=result[0]["StartTime"],
                end_time=result[0]["EndTime"],
                total_duration_minutes=result[0]["TotalDurationMinutes"],
                notes=result[0]["Notes"],
            )
            logger.info(f"Created workout session {new_session.id} for user {user.auth0_sub}")
            return new_session
        
        raise Exception("Failed to retrieve inserted workout log")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workout session for user {user.auth0_sub}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workout session",
        ) from e
