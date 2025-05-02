from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket
from sqlmodel import Session
from ..core.video_editor import apply_command
from ..core.models import Video, CommandRequest
from ..db import get_db

router = APIRouter()

@router.post("/{video_id}/commands")
async def run_command(
    video_id: UUID,
    req: CommandRequest,
    db: Session = Depends(get_db)
):
    """
    Process a video editing command and return the updated video.
    
    Args:
        video_id: The ID of the video to process
        req: The command request containing the natural language command
        db: Database session
        
    Returns:
        The updated video object
    """
    video = Video.get(db, video_id)
    new_video = apply_command(video, req.command)
    
    # Broadcast the update to connected clients
    await _broadcast("video-updated", {
        "video_id": str(new_video.id),
        "url": new_video.file_url
    })
    
    return {"video": new_video.as_dict()}

@router.post("/{video_id}/nlp-edit")
async def nlp_edit(
    video_id: UUID,
    req: CommandRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts free-form text → resolves → executes → returns updated video.
    
    Args:
        video_id: The ID of the video to edit
        req: The command request containing the natural language command
        db: Database session
        
    Returns:
        The updated video and the action that was taken
    """
    video = Video.get(db, video_id)
    new_video = apply_command(video, req.command)
    
    # Broadcast the update to connected clients
    await _broadcast("video-updated", {
        "video_id": str(new_video.id),
        "url": new_video.file_url
    })
    
    return {
        "video": new_video.as_dict(),
        "action": new_video.effects[-1].as_dict()  # Get the most recent effect
    }

async def _broadcast(event: str, data: dict):
    """Broadcast an event to all connected WebSocket clients."""
    # TODO: Implement WebSocket broadcasting
    # This will depend on your WebSocket setup
    pass 