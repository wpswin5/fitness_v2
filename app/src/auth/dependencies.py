"""
FastAPI Dependencies for Auth0 Protected Routes
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.auth0 import auth0_manager
from src.auth.models import UserContext, TokenPayload
from jose import JWTError
from jose.exceptions import JWTClaimsError

logger = logging.getLogger(__name__)

# Security scheme for Swagger UI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserContext:
    """
    Dependency: Extract and validate user from Auth0 token
    
    Usage:
        @app.get("/api/v1/workouts")
        async def get_workouts(user: UserContext = Depends(get_current_user)):
            # user.auth0_id is guaranteed to be present and valid
    
    Returns:
        UserContext with authenticated user information
        
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    
    try:
        # Verify and decode token
        token_payload: TokenPayload = auth0_manager.verify_token(token)
        
        # Build user context from token claims
        user_context = UserContext(
            auth0_sub=token_payload.sub,
            email=token_payload.email,
            first_name=token_payload.given_name,
            last_name=token_payload.family_name,
            picture=token_payload.picture,
        )
        
        logger.info(f"User authenticated: {user_context.auth0_sub}")
        return user_context
        
    except JWTClaimsError as e:
        logger.warning(f"Token claims invalid: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
