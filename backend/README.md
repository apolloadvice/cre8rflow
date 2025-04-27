# Cre8rFlow - NLP Video Editor Backend

A production-grade FastAPI backend for Cre8rFlow that processes natural language commands to edit videos.

## Features

- **Thumbnail Generation**: Create thumbnail sprites and VTT files from videos.
- **Natural Language Processing**: Process editing commands using GPT-4o.
- **Background Processing**: Handle heavy tasks with Redis queues.
- **Supabase Integration**: Authentication and storage with Supabase.

## Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- FFmpeg
- Supabase account
- OpenAI API key

### Environment Variables

Copy the `.env.sample` file to `.env` and fill in your credentials:

```bash
cp .env.sample .env
```

Make sure to update:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_JWT_SECRET`: Your Supabase JWT secret

### Running Locally (without Docker)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

3. Start the Redis worker in another terminal:

```bash
python -c "from app.services.worker import run_worker; run_worker()"
```

### Running with Docker

1. Build and start the services:

```bash
docker-compose up -d
```

For local development with a Postgres database:

```bash
docker-compose --profile local up -d
```

2. Access the API at http://localhost:8000

## API Endpoints

- `/health`: Health check endpoint
- `/thumbnails/{video_id}`: Generate thumbnails for a video
- `/command`: Process a natural language editing command

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy app
``` 