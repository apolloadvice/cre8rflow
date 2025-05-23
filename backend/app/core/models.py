from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, ConfigDict
import numpy as np
from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

class VideoBase(SQLModel):
    title: str
    file_path: str
    file_url: str
    duration: float

class Video(VideoBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transcripts: List["Transcript"] = Relationship(back_populates="video")
    effects: List["Effect"] = Relationship(back_populates="video")

    @classmethod
    def create_from_parent(cls, parent: "Video", new_file_path: str) -> "Video":
        """Create a new video from a parent video with a new file path."""
        return cls(
            title=parent.title,
            file_path=new_file_path,
            file_url=parent.file_url,  # This should be updated with the new URL
            duration=parent.duration,
            parent_id=parent.id
        )

class Transcript(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    video_id: UUID = Field(foreign_key="video.id")
    sentence: str
    start_time: float
    end_time: float
    embedding: List[float] = Field(sa_column=Column(ARRAY(Float)))
    video: Video = Relationship(back_populates="transcripts")

    @classmethod
    def get_by_video(cls, video_id: UUID) -> List["Transcript"]:
        """Get all transcripts for a video."""
        # This will be implemented in the database layer
        pass

class EffectBase(SQLModel):
    type: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    factor: Optional[float] = None
    text: Optional[str] = None

class Effect(EffectBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    video_id: UUID = Field(foreign_key="video.id")
    video: Video = Relationship(back_populates="effects")

class CommandRequest(BaseModel):
    command: str 