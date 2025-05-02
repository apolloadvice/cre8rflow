import os
from typing import List, Tuple


def generate_vtt(
    total_thumbs: int,
    columns: int,
    thumbnail_width: int,
    thumbnail_height: int,
    fps: float,
    duration: float,
    output_dir: str
) -> str:
    """
    Generate a WebVTT file for thumbnail sprites.
    
    Args:
        total_thumbs: Total number of thumbnails
        columns: Number of thumbnails per row
        thumbnail_width: Width of each thumbnail
        thumbnail_height: Height of each thumbnail
        fps: Frames per second of thumbnails
        duration: Duration of the video in seconds
        output_dir: Directory to save the VTT file
        
    Returns:
        Path to the generated VTT file
    """
    vtt_path = os.path.join(output_dir, "thumbnails.vtt")
    
    with open(vtt_path, "w") as f:
        f.write("WEBVTT\n\n")
        
        for i in range(total_thumbs):
            # Calculate position in sprite grid
            row = i // columns
            col = i % columns
            
            # Calculate times
            start_time = i / fps
            end_time = min((i + 1) / fps, duration)
            
            # Skip if we've reached the end of the video
            if start_time >= duration:
                break
            
            # Calculate x,y position in the sprite
            x = col * thumbnail_width
            y = row * thumbnail_height
            
            # Format timestamps as HH:MM:SS.mmm
            start_formatted = format_timestamp(start_time)
            end_formatted = format_timestamp(end_time)
            
            # Write cue
            f.write(f"{start_formatted} --> {end_formatted}\n")
            f.write(f"sprite.jpg#xywh={x},{y},{thumbnail_width},{thumbnail_height}\n\n")
    
    return vtt_path


def format_timestamp(seconds: float) -> str:
    """
    Format seconds as WebVTT timestamp (HH:MM:SS.mmm).
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def parse_vtt_file(vtt_path: str) -> List[Tuple[float, float, str]]:
    """
    Parse a WebVTT file and extract cue timings and positions.
    
    Args:
        vtt_path: Path to the VTT file
        
    Returns:
        List of tuples with (start_time, end_time, sprite_position)
    """
    cues = []
    
    with open(vtt_path, "r") as f:
        lines = f.readlines()
    
    i = 0
    # Skip header
    while i < len(lines) and not lines[i].strip() == "WEBVTT":
        i += 1
    i += 1
    
    # Parse cues
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Parse timestamp line
        if "-->" in line:
            times = line.split(" --> ")
            start_time = parse_timestamp(times[0])
            end_time = parse_timestamp(times[1])
            
            # Get sprite position from next line
            i += 1
            if i < len(lines):
                sprite_position = lines[i].strip()
                cues.append((start_time, end_time, sprite_position))
        
        i += 1
    
    return cues


def parse_timestamp(timestamp: str) -> float:
    """
    Parse WebVTT timestamp into seconds.
    
    Args:
        timestamp: WebVTT timestamp string (HH:MM:SS.mmm)
        
    Returns:
        Time in seconds
    """
    parts = timestamp.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    
    return hours * 3600 + minutes * 60 + seconds 