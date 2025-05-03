import pytest
from uuid import uuid4
from ..app.core.models import Video, Transcript
from ..app.core.command_resolver import resolve
from ..app.core.video_editor import apply_command

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

@pytest.fixture
def sample_transcripts():
    """Create sample transcripts for testing."""
    return [
        Transcript(
            id=uuid4(),
            video_id=uuid4(),
            sentence="I mentioned my childhood in this part",
            start=25.0,
            end=31.0,
            embedding=[0.1] * 384  # Dummy embedding
        ),
        Transcript(
            id=uuid4(),
            video_id=uuid4(),
            sentence="I'm whispering at the end",
            start=45.0,
            end=50.0,
            embedding=[0.2] * 384  # Dummy embedding
        )
    ]

def test_nlp_cut_command(sample_video, sample_transcripts, monkeypatch):
    """Test NLP cut command."""
    # Mock the transcript fetching
    def mock_get_by_video(video_id):
        return sample_transcripts
    monkeypatch.setattr(Transcript, "get_by_video", mock_get_by_video)
    
    # Test the command
    command = "Cut out the part where I mention my childhood from 0:25 to 0:31"
    action = resolve(str(sample_video.id), command)
    
    assert action["action"] == "cut"
    assert action["start_sec"] == 25.0
    assert action["end_sec"] == 31.0
    assert "childhood" in action["reason"].lower()

def test_nlp_volume_command(sample_video, sample_transcripts, monkeypatch):
    """Test NLP volume command."""
    # Mock the transcript fetching
    def mock_get_by_video(video_id):
        return sample_transcripts
    monkeypatch.setattr(Transcript, "get_by_video", mock_get_by_video)
    
    # Test the command
    command = "Make the volume louder when I whisper at the end"
    action = resolve(str(sample_video.id), command)
    
    assert action["action"] == "volume"
    assert action["start_sec"] == 45.0
    assert action["end_sec"] == 50.0
    assert action["factor"] > 1.0
    assert "whisper" in action["reason"].lower()

def test_apply_nlp_command(sample_video, sample_transcripts, monkeypatch):
    """Test applying an NLP command."""
    # Mock the transcript fetching
    def mock_get_by_video(video_id):
        return sample_transcripts
    monkeypatch.setattr(Transcript, "get_by_video", mock_get_by_video)
    
    # Test the command
    command = "Cut out the part where I mention my childhood"
    new_video = apply_command(sample_video, command)
    
    assert new_video.parent_id == sample_video.id
    assert len(new_video.effects) == 1
    assert new_video.effects[0].type == "cut" 