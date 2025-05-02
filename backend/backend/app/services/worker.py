import os
import json
import asyncio
from typing import Dict, Any, List, Optional
import redis
from rq import Queue, Worker, Connection
from supabase import create_client, Client

from app.core.config import settings
from app.db import db


# Initialize Redis connection
redis_conn = redis.from_url(settings.redis_url)

# Create RQ queue
queue = Queue(connection=redis_conn)


async def enqueue_task(task_type: str, data: Dict[str, Any]) -> str:
    """
    Enqueue a background task in Redis RQ.
    
    Args:
        task_type: Type of task (e.g., "process_clip")
        data: Data needed for the task
        
    Returns:
        Job ID
    """
    job = queue.enqueue(
        f"app.services.worker.{task_type}",
        data,
        job_timeout=3600  # 1 hour timeout
    )
    
    return job.id


def process_clip(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a video clip - this runs in a background worker.
    
    Args:
        data: Dictionary with clip data including:
              - operation_id: ID of the operation
              - project_id: ID of the project
              - operation_type: Type of operation
              - start_time: Start time in seconds
              - end_time: End time in seconds
              - parameters: Additional parameters
    
    Returns:
        Processing results
    """
    # Convert to async function and run in event loop
    async def _process_clip_async() -> Dict[str, Any]:
        try:
            # Initialize Supabase client
            supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            
            # Get operation details
            operation_id = data["operation_id"]
            project_id = data["project_id"]
            
            # Update status to "processing"
            async with db.connection() as conn:
                await conn.execute(
                    """
                    UPDATE clips
                    SET status = $1
                    WHERE id = $2
                    """,
                    "processing",
                    operation_id
                )
            
            # Get project details including source video
            async with db.connection() as conn:
                project = await conn.fetchrow(
                    """
                    SELECT * FROM projects WHERE id = $1
                    """,
                    project_id
                )
                
                if not project:
                    raise ValueError(f"Project with ID {project_id} not found")
                
                video_id = project["video_id"]
            
            # Process the clip based on operation type
            result = await process_operation(data, video_id, supabase)
            
            # Update status to "completed"
            async with db.connection() as conn:
                await conn.execute(
                    """
                    UPDATE clips
                    SET status = $1, result = $2
                    WHERE id = $3
                    """,
                    "completed",
                    json.dumps(result),
                    operation_id
                )
            
            # Emit realtime event via Supabase
            supabase.table("realtime_events").insert({
                "event": "timeline_update",
                "project_id": project_id,
                "payload": {
                    "operation_id": operation_id,
                    "status": "completed",
                    "result": result
                }
            }).execute()
            
            return {
                "success": True,
                "operation_id": operation_id,
                "result": result
            }
            
        except Exception as e:
            # Update status to "failed"
            async with db.connection() as conn:
                await conn.execute(
                    """
                    UPDATE clips
                    SET status = $1, result = $2
                    WHERE id = $3
                    """,
                    "failed",
                    json.dumps({"error": str(e)}),
                    data.get("operation_id")
                )
            
            # Emit realtime event via Supabase
            supabase = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            
            supabase.table("realtime_events").insert({
                "event": "timeline_update",
                "project_id": data.get("project_id"),
                "payload": {
                    "operation_id": data.get("operation_id"),
                    "status": "failed",
                    "error": str(e)
                }
            }).execute()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    # Run the async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process_clip_async())
    finally:
        loop.close()


async def process_operation(
    data: Dict[str, Any],
    video_id: str,
    supabase: Client
) -> Dict[str, Any]:
    """
    Process a specific operation type.
    
    Args:
        data: Operation data
        video_id: ID of the source video
        supabase: Supabase client
        
    Returns:
        Operation results
    """
    import tempfile
    import os
    import ffmpeg
    
    operation_type = data["operation_type"]
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    parameters = data.get("parameters", {})
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download source video
        video_path = os.path.join(temp_dir, f"{video_id}.mp4")
        
        # Get file from storage
        res = supabase.storage.from_("videos").download(f"{video_id}.mp4")
        
        # Save to temporary file
        with open(video_path, "wb") as f:
            f.write(res)
        
        # Process based on operation type
        output_path = os.path.join(temp_dir, f"output_{video_id}.mp4")
        
        if operation_type == "cut":
            # Cut a section from the video
            (
                ffmpeg
                .input(video_path, ss=start_time, to=end_time)
                .output(output_path, c="copy")
                .run(quiet=True)
            )
        
        elif operation_type == "trim":
            # Trim (remove) a section from the video
            # This requires concatenating two parts
            part1 = os.path.join(temp_dir, "part1.mp4")
            part2 = os.path.join(temp_dir, "part2.mp4")
            
            # Extract part before trim point
            if start_time > 0:
                (
                    ffmpeg
                    .input(video_path, to=start_time)
                    .output(part1, c="copy")
                    .run(quiet=True)
                )
            
            # Extract part after trim point
            (
                ffmpeg
                .input(video_path, ss=end_time)
                .output(part2, c="copy")
                .run(quiet=True)
            )
            
            # Create concat file
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, "w") as f:
                if start_time > 0:
                    f.write(f"file '{part1}'\n")
                f.write(f"file '{part2}'\n")
            
            # Concatenate parts
            (
                ffmpeg
                .input(concat_file, format="concat", safe=0)
                .output(output_path, c="copy")
                .run(quiet=True)
            )
        
        elif operation_type == "speed":
            # Change playback speed
            speed_factor = parameters.get("speed_factor", 1.0)
            
            (
                ffmpeg
                .input(video_path, ss=start_time, to=end_time)
                .filter("setpts", f"{1/speed_factor}*PTS")
                .output(output_path)
                .run(quiet=True)
            )
        
        else:
            # Default to simple copy of the specified segment
            (
                ffmpeg
                .input(video_path, ss=start_time, to=end_time)
                .output(output_path, c="copy")
                .run(quiet=True)
            )
        
        # Upload result to Supabase Storage
        result_path = f"results/{data['operation_id']}.mp4"
        
        with open(output_path, "rb") as f:
            supabase.storage.from_("assets").upload(
                result_path,
                f.read(),
                {"content-type": "video/mp4"}
            )
        
        # Get public URL
        result_url = supabase.storage.from_("assets").get_public_url(result_path)
        
        return {
            "result_url": result_url,
            "duration": end_time - start_time,
            "operation_type": operation_type
        }


def run_worker():
    """Start the RQ worker process."""
    with Connection(redis_conn):
        worker = Worker([queue])
        worker.work() 