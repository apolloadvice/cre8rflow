from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session
from ..core.models import Video
from ..core.transcript_generator import generate_transcripts
from ..db import get_db

router = APIRouter()

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a video and generate transcripts.
    
    Args:
        file: The video file to upload
        db: Database session
        
    Returns:
        The created video object
    """
    # Save the file
    video_path = f"/tmp/{file.filename}"
    with open(video_path, "wb") as f:
        f.write(await file.read())
    
    # Create the video object
    video = Video(
        title=file.filename,
        file_path=video_path,
        file_url=f"/videos/{file.filename}",
        duration=0.0  # Will be updated after processing
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Generate transcripts
    transcripts = generate_transcripts(video)
    for transcript in transcripts:
        db.add(transcript)
    db.commit()
    
    return video.as_dict() 