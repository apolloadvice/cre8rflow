import whisperx
from typing import List
from .models import Transcript, Video
from .embedding_cache import cache_transcript_embeddings

def generate_transcripts(video: Video) -> List[Transcript]:
    """
    Generate transcripts for a video using WhisperX.
    
    Args:
        video: The video to generate transcripts for
        
    Returns:
        List of Transcript objects
    """
    # Load the model
    model = whisperx.load_model("base", device="cuda")
    
    # Transcribe the video
    result = model.transcribe(video.file_path)
    
    # Align the transcript with the audio
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"],
        device="cuda"
    )
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        video.file_path,
        device="cuda"
    )
    
    # Create transcript objects
    transcripts = []
    for segment in result["segments"]:
        transcript = Transcript(
            video_id=video.id,
            sentence=segment["text"],
            start=segment["start"],
            end=segment["end"],
            embedding=None  # Will be set by cache_transcript_embeddings
        )
        cache_transcript_embeddings(transcript)
        transcripts.append(transcript)
    
    return transcripts 