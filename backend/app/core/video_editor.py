import os
import tempfile
from typing import Dict, Any
from uuid import UUID
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from .models import Video, Effect
from .command_resolver import resolve

def _save_tmp(clip: VideoFileClip, video_id: UUID) -> str:
    """Save the processed clip to a temporary file and return its path."""
    temp_dir = os.path.join(tempfile.gettempdir(), "cre8rflow")
    os.makedirs(temp_dir, exist_ok=True)
    
    output_path = os.path.join(temp_dir, f"{video_id}_processed.mp4")
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    clip.close()
    
    return output_path

def apply_command(video: Video, command: str) -> Video:
    """
    Parse a natural-language command and return a NEW Video object whose
    file contains the rendered change. Also write an Effect row so we
    can undo/redo later.
    
    Args:
        video: The original Video object
        command: The natural language command to process
        
    Returns:
        A new Video object with the processed video file
    """
    # Use the command resolver to parse the command
    action = resolve(str(video.id), command)
    
    # Load the video clip
    clip = VideoFileClip(video.file_path)
    
    # Apply the appropriate transformation based on the command type
    if action["action"] == "cut":
        start, end = action["start_sec"], action["end_sec"]
        processed = concatenate_videoclips([
            clip.subclip(0, start),
            clip.subclip(end)
        ])
    elif action["action"] == "volume":
        processed = clip.volumex(action["factor"])
    elif action["action"] == "zoom":
        # TODO: Implement zoom functionality
        processed = clip  # Placeholder
    elif action["action"] == "caption":
        # TODO: Implement caption functionality
        processed = clip  # Placeholder
    else:
        raise ValueError(f"Unsupported action type: {action['action']}")
    
    # Save the processed video
    out_path = _save_tmp(processed, video.id)
    
    # Create a new video entry
    new_video = Video.create_from_parent(video, out_path)
    
    # Create the effect record
    Effect.create(
        video_id=new_video.id,
        type=action["action"],
        start=action.get("start_sec"),
        end=action.get("end_sec"),
        factor=action.get("factor"),
        text=action.get("text")
    )
    
    return new_video 