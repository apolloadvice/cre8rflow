import json
from typing import List, Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from .models import Transcript
from .embedding_cache import get_or_create_embeddings
from .command_patterns import match_quick
from .llm import get_llm_action

# Initialize the local embedding model
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_search(query: str, transcript_rows: List[Transcript], top_k: int = 5) -> List[Tuple[Transcript, float]]:
    """
    Perform semantic search over transcript rows using cosine similarity.
    
    Args:
        query: The search query
        transcript_rows: List of transcript rows to search over
        top_k: Number of top results to return
        
    Returns:
        List of (transcript_row, similarity_score) tuples
    """
    # Encode the query
    query_embedding = MODEL.encode(query, normalize_embeddings=True)
    
    # Calculate similarities
    hits = []
    for row in transcript_rows:
        similarity = query_embedding @ row.embedding  # cosine similarity
        hits.append((row, similarity))
    
    # Return top k results
    return sorted(hits, key=lambda x: x[1], reverse=True)[:top_k]

async def resolve_command(
    text: str,
    video_duration: Optional[float] = None,
    use_llm: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Resolve a command to an action, trying quick commands first.
    
    Args:
        text: The command text to resolve
        video_duration: Optional video duration for commands that need it
        use_llm: Whether to fall back to LLM if no quick command matches
        
    Returns:
        Action dictionary if resolved, None if no match
    """
    # Try quick commands first
    if action := match_quick(text, video_duration):
        return action
        
    # Fall back to LLM if enabled
    if use_llm:
        return await get_llm_action(text)
        
    return None

def resolve(video_id: str, user_command: str) -> Dict[str, Any]:
    """
    Resolve a natural language command into a structured video editing action.
    
    Args:
        video_id: The ID of the video being edited
        user_command: The natural language command from the user
        
    Returns:
        A dictionary containing the structured action
    """
    # 1. Fetch transcript rows and perform semantic search
    transcript_rows = Transcript.get_by_video(video_id)
    top_matches = semantic_search(user_command, transcript_rows)
    context = "\n".join([f"{row.start:.1f}-{row.end:.1f}s: {row.sentence}" 
                        for row, _ in top_matches])
    
    # 2. Call OpenAI with function calling
    llm = OpenAI()
    functions = [
        {
            "name": "video_edit",
            "description": "Generate a video editing command based on natural language input",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["cut", "volume", "zoom", "caption"],
                        "description": "The type of edit to perform"
                    },
                    "start_sec": {
                        "type": "number",
                        "description": "Start time in seconds"
                    },
                    "end_sec": {
                        "type": "number",
                        "description": "End time in seconds"
                    },
                    "factor": {
                        "type": "number",
                        "description": "Multiplier for volume/zoom changes"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text for captions"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Explanation of why this action was chosen"
                    }
                },
                "required": ["action", "reason"]
            }
        }
    ]
    
    messages = [
        {
            "role": "system",
            "content": """You are a video editing command generator. 
            Analyze the user's request and the provided transcript excerpts to determine 
            the appropriate video editing action. Consider the context and timing carefully."""
        },
        {
            "role": "user",
            "content": user_command
        },
        {
            "role": "assistant",
            "content": f"Transcript excerpts:\n{context}"
        }
    ]
    
    # Call the LLM
    response = llm.chat.completions.create(
        model="gpt-4",  # or "o3" based on configuration
        messages=messages,
        functions=functions,
        function_call={"name": "video_edit"}
    )
    
    # Parse and return the action
    return json.loads(response.choices[0].message.function_call.arguments) 