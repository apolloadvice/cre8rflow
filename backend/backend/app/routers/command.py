from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.routers.auth import get_current_user
from app.services.nlp import process_command
from app.services.worker import enqueue_task
from app.core.config import settings


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/command",
    tags=["command"]
)


@router.post("/", response_model=Dict[str, Any])
@limiter.limit(f"{settings.command_rate_limit}/minute")
async def execute_command(
    request_data: Dict[str, Any] = Body(
        ...,
        example={
            "project_id": "123e4567-e89b-12d3-a456-426614174000",
            "command_text": "Cut from the part where John says 'Hello world' to the scene with the sunset",
            "user_id": "user123"
        }
    ),
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process a natural language video editing command.
    
    This endpoint:
    1. Parses the natural language command
    2. Resolves references to timestamps in the video
    3. Plans the edit operations using GPT-4o
    4. Persists the operations to the database
    5. Enqueues heavy processing tasks in the background
    6. Returns the planned operations
    
    Args:
        request_data: Dictionary with command details
        user_id: ID of the authenticated user
        
    Returns:
        Dictionary with operations and status
        
    Raises:
        HTTPException: If command processing fails
    """
    try:
        # Validate request data
        project_id = request_data.get("project_id")
        command_text = request_data.get("command_text")
        
        if not project_id or not command_text:
            raise ValueError("Missing required fields: project_id, command_text")
        
        # Process command and get operations
        result = await process_command(
            project_id=project_id,
            command_text=command_text,
            user_id=user_id
        )
        
        # Enqueue each operation for background processing
        for i, operation in enumerate(result["operations"]):
            # Enqueue task
            job_id = await enqueue_task("process_clip", {
                "operation_id": result["operation_ids"][i],
                "project_id": project_id,
                "operation_type": operation["operation_type"],
                "start_time": operation.get("start_time"),
                "end_time": operation.get("end_time"),
                "parameters": operation.get("parameters", {})
            })
            
            # Add job ID to result
            operation["job_id"] = job_id
        
        return {
            "success": True,
            "operations": result["operations"],
            "operation_ids": result["operation_ids"],
            "message": "Command processed successfully"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process command: {str(e)}"
        ) 