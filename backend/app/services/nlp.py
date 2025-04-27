from typing import Dict, Any, List, Optional, Tuple
import json
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings
from app.db import db


# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

# Initialize sentence transformer model for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


async def process_command(
    project_id: str,
    command_text: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Process a natural language editing command.
    
    Args:
        project_id: ID of the project
        command_text: Natural language command text
        user_id: ID of the user making the request
        
    Returns:
        Dictionary with processing results and operations
    """
    # Fetch project data
    project_data = await fetch_project_data(project_id)
    
    # Resolve references to timestamps in command
    resolved_command, timestamps = await resolve_timestamp_references(
        command_text, 
        project_data
    )
    
    # Call GPT-4o to plan the edit
    operations = await plan_edit_with_gpt(
        resolved_command, 
        project_data, 
        timestamps
    )
    
    # Save operations to database
    operation_ids = await save_operations(operations, project_id, user_id)
    
    return {
        "success": True,
        "operations": operations,
        "operation_ids": operation_ids
    }


async def fetch_project_data(project_id: str) -> Dict[str, Any]:
    """
    Fetch project data including transcript, scenes and audio features.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Dictionary with project data
    """
    async with db.connection() as conn:
        # Fetch project metadata
        project = await conn.fetchrow(
            """
            SELECT * FROM projects WHERE id = $1
            """,
            project_id
        )
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Fetch transcript
        transcript = await conn.fetch(
            """
            SELECT * FROM transcripts 
            WHERE project_id = $1
            ORDER BY start_time
            """,
            project_id
        )
        
        # Fetch scenes
        scenes = await conn.fetch(
            """
            SELECT * FROM scenes
            WHERE project_id = $1
            ORDER BY start_time
            """,
            project_id
        )
        
        # Fetch audio features
        audio_features = await conn.fetch(
            """
            SELECT * FROM audio_features
            WHERE project_id = $1
            ORDER BY timestamp
            """,
            project_id
        )
        
        # Fetch current clips
        clips = await conn.fetch(
            """
            SELECT * FROM clips
            WHERE project_id = $1
            ORDER BY sequence_order
            """,
            project_id
        )
    
    return {
        "project": dict(project),
        "transcript": [dict(t) for t in transcript],
        "scenes": [dict(s) for s in scenes],
        "audio_features": [dict(a) for a in audio_features],
        "clips": [dict(c) for c in clips]
    }


async def resolve_timestamp_references(
    command_text: str, 
    project_data: Dict[str, Any]
) -> Tuple[str, Dict[str, float]]:
    """
    Resolve natural language references to timestamps.
    
    Args:
        command_text: Natural language command text
        project_data: Project data including transcript
        
    Returns:
        Tuple of (resolved_command, timestamp_dict)
    """
    # Create embeddings for transcript segments
    transcript = project_data["transcript"]
    sentences = [t["text"] for t in transcript]
    timestamps = [t["start_time"] for t in transcript]
    
    # Create embeddings for all transcript segments
    sentence_embeddings = embedding_model.encode(sentences)
    
    # Extract potential references from command text
    # This is a simplified approach - in production we would use more sophisticated NER
    words = command_text.split()
    potential_references = []
    for i, word in enumerate(words):
        if word.startswith('"') and word.endswith('"'):
            potential_references.append(word.strip('"'))
        elif word.startswith("'") and word.endswith("'"):
            potential_references.append(word.strip("'"))
        elif '"' in command_text:
            # Try to extract quoted phrases
            import re
            matches = re.findall(r'"([^"]*)"', command_text)
            potential_references.extend(matches)
    
    # Remove duplicates
    potential_references = list(set(potential_references))
    
    # Find closest matches and their timestamps
    timestamp_dict = {}
    for ref in potential_references:
        if ref:
            ref_embedding = embedding_model.encode([ref])[0]
            
            # Calculate cosine similarity
            similarities = []
            for sent_emb in sentence_embeddings:
                similarity = np.dot(ref_embedding, sent_emb) / (
                    np.linalg.norm(ref_embedding) * np.linalg.norm(sent_emb)
                )
                similarities.append(similarity)
            
            # Find best match
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            # Only use matches above a threshold
            if best_similarity > 0.6:
                timestamp_dict[ref] = timestamps[best_match_idx]
    
    # Create a resolved command with timestamp markers
    resolved_command = command_text
    for ref, timestamp in timestamp_dict.items():
        resolved_command = resolved_command.replace(
            f'"{ref}"', 
            f'"{ref}" [at {timestamp:.2f}s]'
        )
        resolved_command = resolved_command.replace(
            f"'{ref}'", 
            f"'{ref}' [at {timestamp:.2f}s]"
        )
    
    return resolved_command, timestamp_dict


async def plan_edit_with_gpt(
    command: str, 
    project_data: Dict[str, Any],
    timestamps: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Use GPT-4o to plan edits based on the command.
    
    Args:
        command: Resolved command text
        project_data: Project data
        timestamps: Dictionary mapping references to timestamps
        
    Returns:
        List of edit operations
    """
    # Define function schema for GPT-4o
    functions = [
        {
            "name": "plan_edit",
            "description": "Plan video editing operations based on user command",
            "parameters": {
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "description": "List of editing operations to perform",
                        "items": {
                            "type": "object",
                            "properties": {
                                "operation_type": {
                                    "type": "string",
                                    "enum": ["cut", "trim", "add", "remove", "move", "speed", "transition"],
                                    "description": "Type of operation to perform"
                                },
                                "start_time": {
                                    "type": "number",
                                    "description": "Start time in seconds"
                                },
                                "end_time": {
                                    "type": "number",
                                    "description": "End time in seconds"
                                },
                                "target_index": {
                                    "type": "integer",
                                    "description": "Target position in timeline"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Additional parameters for the operation"
                                }
                            },
                            "required": ["operation_type"]
                        }
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the planned edit"
                    }
                },
                "required": ["operations", "description"]
            }
        }
    ]
    
    # Prepare context for GPT
    clips_context = ""
    if project_data["clips"]:
        clips = project_data["clips"]
        clips_context = "Current clips in timeline:\n"
        for i, clip in enumerate(clips):
            clips_context += f"{i+1}. {clip['start_time']:.2f}s - {clip['end_time']:.2f}s\n"
    
    # Create prompt
    prompt = f"""
You are a video editing assistant. Based on the user's command, plan the appropriate video editing operations.

User command: {command}

{clips_context}

Reference timestamps detected:
{json.dumps(timestamps, indent=2)}

Available video duration: {project_data['project'].get('duration', 0)}s

Respond with a plan for editing operations.
"""
    
    # Call GPT-4o
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        tools=functions,
        tool_choice={"type": "function", "function": {"name": "plan_edit"}}
    )
    
    # Extract function call
    message = response.choices[0].message
    if message.tool_calls and message.tool_calls[0].function.name == "plan_edit":
        function_args = json.loads(message.tool_calls[0].function.arguments)
        return function_args["operations"]
    
    # Fallback
    return []


async def save_operations(
    operations: List[Dict[str, Any]],
    project_id: str,
    user_id: str
) -> List[str]:
    """
    Save edit operations to database.
    
    Args:
        operations: List of edit operations
        project_id: ID of the project
        user_id: ID of the user
        
    Returns:
        List of operation IDs
    """
    operation_ids = []
    
    async with db.connection() as conn:
        # Begin transaction
        async with conn.transaction():
            for op in operations:
                # Insert operation and get ID
                op_id = await conn.fetchval(
                    """
                    INSERT INTO clips (
                        project_id, 
                        user_id,
                        operation_type,
                        start_time,
                        end_time,
                        target_index,
                        parameters,
                        status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id
                    """,
                    project_id,
                    user_id,
                    op.get("operation_type"),
                    op.get("start_time"),
                    op.get("end_time"),
                    op.get("target_index"),
                    json.dumps(op.get("parameters", {})),
                    "pending"
                )
                
                operation_ids.append(str(op_id))
    
    return operation_ids


async def create_embedding(text: str) -> List[float]:
    """
    Create embedding for a text string.
    
    Args:
        text: Input text
        
    Returns:
        Vector embedding
    """
    return embedding_model.encode(text).tolist() 