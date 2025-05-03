"""
Minimal video processor for testing
"""
from typing import Dict, Any
from app.models import Video, Effect

async def apply_command(video: Video, action: Dict[str, Any]) -> Effect:
    """
    Mock apply command function for testing
    
    Args:
        video: The video to apply the command to
        action: The action to apply
        
    Returns:
        The created effect
    """
    return Effect(**action) 