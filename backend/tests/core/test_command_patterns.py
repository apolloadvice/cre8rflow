"""
Tests for quick command pattern matching
"""
import pytest
from app.core.command_patterns import match_quick

@pytest.mark.parametrize("text,expected", [
    ("cut the first 5 seconds", {
        "action": "cut",
        "start_sec": 0.0,
        "end_sec": 5.0,
        "reason": "Cut first 5.0 seconds"
    }),
    ("trim out the first 10 seconds", {
        "action": "cut",
        "start_sec": 0.0,
        "end_sec": 10.0,
        "reason": "Cut first 10.0 seconds"
    }),
    ("cut the last 3 seconds", {
        "action": "cut",
        "start_sec": 7.0,
        "end_sec": 10.0,
        "reason": "Cut last 3.0 seconds"
    }),
    ("cut between 1:30 and 2:00", {
        "action": "cut",
        "start_sec": 90.0,
        "end_sec": 120.0,
        "reason": "Cut from 1:30 to 2:00"
    }),
    ("add text 'Hello' at 0:30", {
        "action": "caption",
        "text": "Hello",
        "start_sec": 30.0,
        "reason": "Add text 'Hello' at 0:30"
    }),
    ("add text \"World\" @ 1:45", {
        "action": "caption",
        "text": "World",
        "start_sec": 105.0,
        "reason": "Add text 'World' at 1:45"
    })
])
def test_match_quick(text: str, expected: dict):
    """Test quick command pattern matching"""
    # For cut last commands, we need video duration
    if "last" in text:
        result = match_quick(text, video_duration=10.0)
    else:
        result = match_quick(text)
        
    assert result == expected

def test_no_match():
    """Test that non-matching text returns None"""
    assert match_quick("random text") is None
    assert match_quick("cut the video") is None
    assert match_quick("add text without timestamp") is None

def test_invalid_timestamp():
    """Test that invalid timestamps return None"""
    assert match_quick("cut between invalid and 2:00") is None
    assert match_quick("add text 'test' at invalid") is None 