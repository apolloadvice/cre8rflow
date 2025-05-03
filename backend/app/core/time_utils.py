"""
Utility helpers to convert a variety of human-friendly timestamp strings
into float seconds.

Examples handled:
- "00:05" → 5.0
- "0:20"  → 20.0
- "20"    → 20.0
- "1:08"  → 68.0
- "1:08.37" → 68.37
"""
from __future__ import annotations
import re
from typing import Optional

_TIMESTAMP_PAT = re.compile(
    r"""(?P<hours>\d{1,2})?:?(?P<minutes>\d{1,2})?:?(?P<seconds>\d{1,2})(?:\.(?P<dec>\d{1,3}))?"""
)

def to_seconds(ts: str) -> float:
    """
    Convert a timestamp string to seconds.
    
    Args:
        ts: Timestamp string in various formats (e.g., "00:05", "1:08", "1:08.37")
        
    Returns:
        Number of seconds as a float
        
    Raises:
        ValueError: If the timestamp format is unrecognized
    """
    m = _TIMESTAMP_PAT.fullmatch(ts.strip())
    if not m:
        raise ValueError(f"Unrecognised timestamp: {ts!r}")
    
    # Extract components
    hours = int(m["hours"] or 0)
    minutes = int(m["minutes"] or 0)
    seconds = int(m["seconds"])
    decimal = float(f"0.{m['dec']}" if m["dec"] else 0)
    
    # Calculate total seconds
    return hours * 3600 + minutes * 60 + seconds + decimal 