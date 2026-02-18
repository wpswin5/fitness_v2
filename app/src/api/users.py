"""
User Management and Sync
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user
from src.auth.models import UserContext
from src.db.query import execute_query

router = APIRouter(tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/users/sync", response_model=dict)
async def sync_user(user: UserContext = Depends(get_current_user)):
    """
    Sync or create user from Auth0 token claims.
    Called on first login to store user in database.
    
    Returns user record with database ID.
    """
    try:
        # Check if user already exists
        query = """
        SELECT UserId, Auth0Sub, Email, FirstName, LastName
        FROM [dbo].[Users]
        WHERE Auth0Sub = ?
        """
        
        result = execute_query(query, (user.auth0_sub,))
        
        if result:
            # User exists - update LastLogin
            update_query = """
            UPDATE [dbo].[Users]
            SET UpdatedAt = GETUTCDATE()
            WHERE Auth0Sub = ?
            """
            execute_query(update_query, (user.auth0_sub,))
            
            logger.info(f"User {user.auth0_sub} already exists, updated LastLogin")
            user_row = result[0]
            return {
                "status": "existing_user",
                "user_id": str(user_row["UserId"]),
                "auth0_sub": user_row["Auth0Sub"],
                "email": user_row["Email"],
            }
        
        # User doesn't exist - create new record
        insert_query = """
        INSERT INTO [dbo].[Users] (Auth0Sub, Email, FirstName, LastName, CreatedAt, UpdatedAt)
        OUTPUT inserted.UserId
        VALUES (?, ?, ?, ?, GETUTCDATE(), GETUTCDATE())
        """
        
        user_id_result = execute_query(
            insert_query,
            (
                user.auth0_sub,
                user.email,
                user.first_name or "",
                user.last_name or "",
            ),
        )
        
        new_user_id = str(user_id_result[0]["UserId"]) if user_id_result else None
        
        logger.info(f"Created new user {user.auth0_sub} with ID {new_user_id}")
        
        return {
            "status": "new_user",
            "user_id": new_user_id,
            "auth0_sub": user.auth0_sub,
            "email": user.email,
        }
        
    except Exception as e:
        logger.error(f"Error syncing user {user.auth0_sub}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync user",
        ) from e


@router.get("/users/me", response_model=dict)
async def get_current_user_profile(user: UserContext = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    """
    try:
        query = """
        SELECT UserId, Auth0Sub, Email, FirstName, LastName, CreatedAt, UpdatedAt
        FROM [dbo].[Users]
        WHERE Auth0Sub = ?
        """
        
        result = execute_query(query, (user.auth0_sub,))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        row = result[0]
        return {
            "user_id": str(row["UserId"]),
            "auth0_sub": row["Auth0Sub"],
            "email": row["Email"],
            "first_name": row["FirstName"],
            "last_name": row["LastName"],
            "created_at": row["CreatedAt"],
            "updated_at": row["UpdatedAt"],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile for {user.auth0_sub}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile",
        ) from e
