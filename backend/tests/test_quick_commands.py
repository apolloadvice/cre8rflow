"""
End-to-end tests for quick commands
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Video, Effect
from app.core.command_patterns import match_quick
from app.core.command_resolver import resolve_command

client = TestClient(app)

@pytest.mark.asyncio
async def test_quick_command_patterns():
    """Test quick command pattern matching"""
    # Test cut first
    action = match_quick("cut the first 5 seconds")
    assert action == {
        "action": "cut",
        "start_sec": 0.0,
        "end_sec": 5.0,
        "reason": "Cut first 5.0 seconds"
    }
    
    # Test cut last
    action = match_quick("cut the last 3 seconds", video_duration=10.0)
    assert action == {
        "action": "cut",
        "start_sec": 7.0,
        "end_sec": 10.0,
        "reason": "Cut last 3.0 seconds"
    }
    
    # Test cut range
    action = match_quick("cut between 1:30 and 2:00")
    assert action == {
        "action": "cut",
        "start_sec": 90.0,
        "end_sec": 120.0,
        "reason": "Cut from 1:30 to 2:00"
    }
    
    # Test add text
    action = match_quick("add text 'Hello' at 0:30")
    assert action == {
        "action": "caption",
        "text": "Hello",
        "start_sec": 30.0,
        "reason": "Add text 'Hello' at 0:30"
    }

@pytest.mark.asyncio
async def test_command_resolver():
    """Test command resolver with quick commands"""
    # Test quick command
    action = await resolve_command("cut the first 5 seconds", video_duration=10.0)
    assert action == {
        "action": "cut",
        "start_sec": 0.0,
        "end_sec": 5.0,
        "reason": "Cut first 5.0 seconds"
    }
    
    # Test invalid command
    action = await resolve_command("random text", video_duration=10.0)
    assert action is None

@pytest.mark.asyncio
async def test_nlp_edit_route():
    """Test the NLP edit route with quick commands"""
    # Create a test video
    video = await Video.create(
        title="Test Video",
        duration=60.0,
        path="/test/path.mp4"
    )
    
    # Test quick command
    response = client.post(
        f"/nlp/edit?video_id={video.id}",
        json={"command": "cut the first 5 seconds"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["effect"]["action"] == "cut"
    assert data["effect"]["start_sec"] == 0.0
    assert data["effect"]["end_sec"] == 5.0
    
    # Test invalid command
    response = client.post(
        f"/nlp/edit?video_id={video.id}",
        json={"command": "random text"}
    )
    assert response.status_code == 400
    
    # Cleanup
    await video.delete() 