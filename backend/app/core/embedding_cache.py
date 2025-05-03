from typing import Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from .models import Transcript

# Initialize the embedding model
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory cache for embeddings
_embedding_cache: Dict[str, np.ndarray] = {}

def get_or_create_embeddings(text: str) -> np.ndarray:
    """
    Get embeddings from cache or create new ones.
    
    Args:
        text: The text to embed
        
    Returns:
        The embedding vector
    """
    if text in _embedding_cache:
        return _embedding_cache[text]
    
    # Generate new embedding
    embedding = MODEL.encode(text, normalize_embeddings=True)
    _embedding_cache[text] = embedding
    return embedding

def cache_transcript_embeddings(transcript: Transcript) -> None:
    """
    Cache embeddings for a transcript.
    
    Args:
        transcript: The transcript to cache embeddings for
    """
    embedding = get_or_create_embeddings(transcript.sentence)
    transcript.embedding = embedding 