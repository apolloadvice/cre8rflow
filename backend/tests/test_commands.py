import pytest
from uuid import uuid4
from ..app.core.models import Video, Effect
from ..app.core.video_editor import apply_command
from ..app.core.command_parser import parse_command
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def sample_video(tmp_path):
    """Create a sample video for testing."""
    # Create a temporary video file
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"fake video data")  # This is just a placeholder
    
    return Video(
        id=uuid4(),
        title="Test Video",
        file_path=str(video_path),
        file_url="http://example.com/test.mp4",
        duration=10.0
    )

def test_parse_volume_command():
    """Test parsing volume commands."""
    # Test percentage
    action = parse_command("boost volume 300%")
    assert action["type"] == "volume"
    assert action["factor"] == 3.0
    
    # Test multiplier
    action = parse_command("increase volume by 2x")
    assert action["type"] == "volume"
    assert action["factor"] == 2.0

def test_parse_cut_command():
    """Test parsing cut commands."""
    action = parse_command("cut 0:00-0:02")
    assert action["type"] == "cut"
    assert action["start"] == 0
    assert action["end"] == 2
    
    action = parse_command("remove from 0:00 to 0:02")
    assert action["type"] == "cut"
    assert action["start"] == 0
    assert action["end"] == 2

def test_parse_caption_command():
    """Test parsing caption commands."""
    action = parse_command('add caption "Hello World" at 0:00')
    assert action["type"] == "caption"
    assert action["text"] == "Hello World"
    assert action["start"] == 0

def test_apply_cut_command(sample_video):
    """Test applying a cut command."""
    new_video = apply_command(sample_video, "cut 0:00-0:02")
    assert new_video.duration == pytest.approx(8.0, abs=0.1)  # 10s - 2s
    assert new_video.parent_id == sample_video.id

def test_apply_volume_command(sample_video):
    """Test applying a volume command."""
    new_video = apply_command(sample_video, "boost volume 200%")
    assert new_video.parent_id == sample_video.id
    # Note: We can't easily verify the volume change without playing the video 

client = TestClient(app)

def test_apply_command():
    """Test the /nlp/apply endpoint."""
    payload = {"command": "cut 0-2s"}
    r = client.post("/nlp/apply", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "Command applied" 