import os
import tempfile
import shutil
from typing import Dict, Any, Tuple
import asyncio
from supabase import create_client, Client

from app.core.config import settings
from app.utils.ffmpeg_helpers import create_thumbnail_sprite, get_video_info
from app.utils.vtt_generator import generate_vtt
from app.db import db


async def generate_thumbnails(video_id: str) -> Dict[str, Any]:
    """
    Generate thumbnail sprite and VTT file for a video.
    
    Args:
        video_id: ID of the video in Supabase Storage
        
    Returns:
        Dictionary with sprite_url, vtt_url, and fps
    """
    # Initialize Supabase client
    supabase: Client = create_client(
        settings.supabase_url, 
        settings.supabase_key
    )
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download video from Supabase Storage
        video_path = os.path.join(temp_dir, f"{video_id}.mp4")
        
        # Get file from storage
        res = supabase.storage.from_("videos").download(f"{video_id}.mp4")
        
        # Save to temporary file
        with open(video_path, "wb") as f:
            f.write(res)
        
        # Get video information
        video_info = await get_video_info(video_path)
        
        # Generate thumbnail sprite
        sprite_path, actual_fps = await create_thumbnail_sprite(
            video_path=video_path,
            output_dir=temp_dir,
            columns=10,
            fps=1.0  # 1 thumbnail per second
        )
        
        # Calculate total thumbnails based on actual fps and duration
        total_thumbs = min(300, int(video_info["duration"] * actual_fps))
        
        # Generate VTT file
        vtt_path = generate_vtt(
            total_thumbs=total_thumbs,
            columns=10,
            thumbnail_width=160,
            thumbnail_height=90,
            fps=actual_fps,
            duration=video_info["duration"],
            output_dir=temp_dir
        )
        
        # Upload sprite and VTT to Supabase Storage
        sprite_storage_path = f"thumbnails/{video_id}/sprite.jpg"
        vtt_storage_path = f"thumbnails/{video_id}/thumbnails.vtt"
        
        with open(sprite_path, "rb") as f:
            supabase.storage.from_("assets").upload(
                sprite_storage_path,
                f.read(),
                {"content-type": "image/jpeg"}
            )
        
        with open(vtt_path, "rb") as f:
            supabase.storage.from_("assets").upload(
                vtt_storage_path,
                f.read(),
                {"content-type": "text/vtt"}
            )
        
        # Generate public URLs
        sprite_url = supabase.storage.from_("assets").get_public_url(sprite_storage_path)
        vtt_url = supabase.storage.from_("assets").get_public_url(vtt_storage_path)
        
        # Insert record into database
        async with db.connection() as conn:
            await conn.execute(
                """
                INSERT INTO video_thumbnails (video_id, sprite_url, vtt_url, fps)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (video_id) DO UPDATE
                SET sprite_url = $2, vtt_url = $3, fps = $4
                """,
                video_id, sprite_url, vtt_url, actual_fps
            )
        
        # Return information
        return {
            "sprite_url": sprite_url,
            "vtt_url": vtt_url,
            "fps": actual_fps
        } 