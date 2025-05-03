"""
Minimal LLM module for testing
"""
from typing import Dict, Any

async def get_llm_action(text: str) -> Dict[str, Any]:
    """
    Mock LLM function for testing
    
    Args:
        text: The command text
        
    Returns:
        A mock action dictionary
    """
    return {
        "action": "caption",
        "text": "Test caption",
        "start_sec": 0.0,
        "reason": "Mock LLM response"
    } 