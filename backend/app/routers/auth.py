from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import PyJWTError

from app.core.config import settings


router = APIRouter(tags=["auth"])

# Security scheme
security = HTTPBearer()


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Validate JWT token from Supabase.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        
        # Check if token is expired
        if "exp" in payload and payload["exp"] < import_time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        return payload
    
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )


def import_time():
    """Import time module and return current timestamp."""
    import time
    return int(time.time())


async def get_current_user(
    token: Dict[str, Any] = Depends(validate_token)
) -> str:
    """
    Get current user ID from token.
    
    Args:
        token: Decoded JWT token
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If user is not found in token
    """
    # Extract user ID from token
    if "sub" not in token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing user ID"
        )
    
    return token["sub"]


@router.get("/verify-token", response_model=Dict[str, Any])
async def verify_token(
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify that the provided token is valid.
    
    Args:
        user_id: User ID from validated token
        
    Returns:
        Dictionary with user ID
    """
    return {"user_id": user_id, "verified": True} 