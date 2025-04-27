from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.routers.auth import get_current_user
from app.services.thumbnails import generate_thumbnails


router = APIRouter(
    prefix="/thumbnails",
    tags=["thumbnails"]
)


@router.post("/{video_id}", response_model=Dict[str, Any])
async def create_thumbnails(
    video_id: str = Path(..., description="ID of the video to process"),
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate thumbnail sprite and VTT file for a video.
    
    This endpoint:
    1. Downloads the source video from Supabase Storage
    2. Generates a sprite sheet with thumbnails
    3. Creates a VTT file for the thumbnails
    4. Uploads both files back to Supabase Storage
    5. Returns the URLs and metadata
    
    Args:
        video_id: ID of the video to process
        user_id: ID of the authenticated user
        
    Returns:
        Dictionary with sprite_url, vtt_url, and fps
    
    Raises:
        HTTPException: If video is not found or processing fails
    """
    try:
        result = await generate_thumbnails(video_id)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate thumbnails: {str(e)}"
        ) 