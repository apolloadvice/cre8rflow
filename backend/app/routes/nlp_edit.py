"""
NLP edit route that handles both quick commands and complex edits
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.command_resolver import resolve_command
from app.core.video_processor import apply_command
from app.models import Video, Effect

router = APIRouter()

@router.post("/edit")
async def edit_video(video_id: str, command: str) -> Dict[str, Any]:
    """
    Edit a video using either quick commands or NLP
    
    Args:
        video_id: ID of the video to edit
        command: The edit command (quick or natural language)
        
    Returns:
        Dict with success status and effect details
    """
    # Get video and its duration
    video = await Video.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    # Try to resolve the command
    action = await resolve_command(
        command,
        video_duration=video.duration,
        use_llm=True  # Allow falling back to LLM
    )
    
    if not action:
        raise HTTPException(
            status_code=400,
            detail="Could not understand the command"
        )
        
    # Apply the command
    try:
        effect = await apply_command(video, action)
        return {
            "success": True,
            "effect": effect.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply command: {str(e)}"
        ) 