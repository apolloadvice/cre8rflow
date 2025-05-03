"""
Minimal models for testing
"""
from typing import Optional, Dict, Any

class Video:
    """Mock Video model for testing"""
    def __init__(self, id: str, title: str, duration: float, path: str):
        self.id = id
        self.title = title
        self.duration = duration
        self.path = path
        
    @classmethod
    async def create(cls, title: str, duration: float, path: str) -> 'Video':
        """Create a new video"""
        return cls(id="test_id", title=title, duration=duration, path=path)
        
    @classmethod
    async def get(cls, video_id: str) -> Optional['Video']:
        """Get a video by ID"""
        if video_id == "test_id":
            return cls(
                id=video_id,
                title="Test Video",
                duration=60.0,
                path="/test/path.mp4"
            )
        return None
        
    async def delete(self):
        """Delete the video"""
        pass

class Effect:
    """Mock Effect model for testing"""
    def __init__(self, action: str, **kwargs):
        self.action = action
        self.kwargs = kwargs
        
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {"action": self.action, **self.kwargs}

class Transcript:
    """Mock Transcript model for testing"""
    def __init__(self, sentence: str, start: float, end: float, embedding: Optional[list] = None):
        self.sentence = sentence
        self.start = start
        self.end = end
        self.embedding = embedding or []
        
    @classmethod
    def get_by_video(cls, video_id: str) -> list['Transcript']:
        """Get transcripts for a video"""
        return [
            cls("This is a test sentence.", 0.0, 5.0),
            cls("Another test sentence.", 5.0, 10.0)
        ] 