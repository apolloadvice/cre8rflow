import os
import tempfile
import ffmpeg
from typing import Tuple, Dict, Any

async def create_thumbnail_sprite(
    video_path: str, 
    output_dir: str,
    columns: int = 10,
    fps: float = 1.0
) -> Tuple[str, float]:
    """
    Creates a sprite sheet of thumbnails from a video.
    
    Args:
        video_path: Path to the source video
        output_dir: Directory to save the sprite
        columns: Number of thumbnails per row
        fps: Frames per second for thumbnails
        
    Returns:
        Tuple of (sprite_path, actual_fps)
    """
    # Get video information
    probe = ffmpeg.probe(video_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = float(probe['format']['duration'])
    
    # Calculate thumbnail count and actual fps
    total_thumbs = min(300, int(duration * fps))  # Cap at 300 thumbnails
    actual_fps = total_thumbs / duration
    
    # Calculate sprite dimensions
    rows = (total_thumbs + columns - 1) // columns
    
    sprite_path = os.path.join(output_dir, "sprite.jpg")
    
    # Create sprite using ffmpeg
    (
        ffmpeg
        .input(video_path, r=actual_fps)
        .filter('scale', 160, 90)
        .filter('tile', columns, rows)
        .output(sprite_path)
        .overwrite_output()
        .run(quiet=True)
    )
    
    return sprite_path, actual_fps


async def extract_frame(
    video_path: str,
    timestamp: float,
    output_path: str,
    width: int = 640,
    height: int = 360
) -> str:
    """
    Extract a single frame from a video at a specific timestamp.
    
    Args:
        video_path: Path to the source video
        timestamp: Time in seconds to extract frame
        output_path: Path to save the frame
        width: Width of the output frame
        height: Height of the output frame
        
    Returns:
        Path to the extracted frame
    """
    (
        ffmpeg
        .input(video_path, ss=timestamp)
        .filter('scale', width, height)
        .output(output_path, vframes=1)
        .overwrite_output()
        .run(quiet=True)
    )
    
    return output_path


async def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get detailed information about a video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with video metadata
    """
    probe = ffmpeg.probe(video_path)
    
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    
    info = {
        'duration': float(probe['format']['duration']),
        'width': int(video_stream['width']),
        'height': int(video_stream['height']),
        'fps': eval(video_stream.get('r_frame_rate', '30/1')),
        'format': probe['format']['format_name'],
        'codec': video_stream['codec_name']
    }
    
    return info 