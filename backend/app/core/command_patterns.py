"""
Regex-based quick commands. If any pattern matches we return an action
dict identical to the LLM function-calling schema so downstream code
(`apply_command`) stays unchanged.
"""
import re
from typing import Optional, Dict, Any
from .time_utils import to_seconds

# Pattern → lambda that returns action dict
CUT_FIRST = re.compile(r"(cut|trim) (out )?the first (?P<secs>\d+(?:\.\d+)?) ?seconds?", re.I)
CUT_LAST = re.compile(r"(cut|trim) (out )?the last (?P<secs>\d+(?:\.\d+)?) ?seconds?", re.I)
CUT_RANGE = re.compile(
    r"(cut|trim) (between|from)? ?(?P<start>[0-9:\.]+)\s*(?:-|to)\s*(?P<end>[0-9:\.]+)", re.I
)
ADD_TEXT = re.compile(
    r"add text ['\"](?P<text>.+?)['\"] (at|@) (?P<ts>[0-9:\.]+)", re.I
)

def match_quick(text: str, video_duration: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """
    Try to match a quick command pattern and return the corresponding action.
    
    Args:
        text: The command text to match
        video_duration: Optional video duration for commands that need it
        
    Returns:
        Action dictionary if a pattern matches, None otherwise
    """
    if m := CUT_FIRST.search(text):
        secs = float(m["secs"])
        return {
            "action": "cut",
            "start_sec": 0.0,
            "end_sec": secs,
            "reason": f"Cut first {secs} seconds"
        }
    
    if m := CUT_LAST.search(text):
        secs = float(m["secs"])
        if video_duration is None:
            return None
        return {
            "action": "cut",
            "start_sec": video_duration - secs,
            "end_sec": video_duration,
            "reason": f"Cut last {secs} seconds"
        }
    
    if m := CUT_RANGE.search(text):
        return {
            "action": "cut",
            "start_sec": to_seconds(m["start"]),
            "end_sec": to_seconds(m["end"]),
            "reason": f"Cut from {m['start']} to {m['end']}"
        }
    
    if m := ADD_TEXT.search(text):
        return {
            "action": "caption",
            "text": m["text"],
            "start_sec": to_seconds(m["ts"]),
            "reason": f"Add text '{m['text']}' at {m['ts']}"
        }
    
    return None 