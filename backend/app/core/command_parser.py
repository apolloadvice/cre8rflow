import re
from typing import Dict, Any

def parse_command(command: str) -> Dict[str, Any]:
    """
    Parse a natural language command into a structured action.
    
    Args:
        command: The natural language command string
        
    Returns:
        A dictionary containing the parsed action details
        
    Raises:
        ValueError: If the command cannot be parsed
    """
    command = command.lower().strip()
    
    # Volume commands (e.g., "boost volume 300%", "increase volume by 2x")
    volume_match = re.match(r"(?:boost|increase|decrease|set)\s+volume\s+(?:by\s+)?(\d+)(?:%|x)?", command)
    if volume_match:
        factor = float(volume_match.group(1)) / 100 if "%" in command else float(volume_match.group(1))
        return {"type": "volume", "factor": factor}
    
    # Cut commands (e.g., "cut 0:00-0:02", "remove from 0:00 to 0:02")
    cut_match = re.match(r"(?:cut|remove)\s+(?:from\s+)?(\d+:\d+)(?:\s*-\s*|\s+to\s+)(\d+:\d+)", command)
    if cut_match:
        start = _time_to_seconds(cut_match.group(1))
        end = _time_to_seconds(cut_match.group(2))
        return {"type": "cut", "start": start, "end": end}
    
    # Caption commands (e.g., "add caption 'Hello' at 0:00")
    caption_match = re.match(r"add\s+caption\s+['\"](.*?)['\"]\s+at\s+(\d+:\d+)", command)
    if caption_match:
        text = caption_match.group(1)
        start = _time_to_seconds(caption_match.group(2))
        return {"type": "caption", "text": text, "start": start}
    
    raise ValueError(f"Could not parse command: {command}")

def _time_to_seconds(time_str: str) -> float:
    """Convert time string (MM:SS) to seconds."""
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds 