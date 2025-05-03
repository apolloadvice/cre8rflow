## Local Development

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/apolloadvice/cre8rflow.git
   cd cre8rflow
   ```

2. Set up your environment:
   ```bash
   cp .env.example .env
   ```
   Add your real secrets inside `.env`.

3. Build & start everything:
   ```bash
   make dev
   ```

4. Open the app:
   - Frontend → http://localhost:5173
   - API docs → http://localhost:8000/docs

### Project Structure

- `backend/app` is the root package; avoid adding another nested "backend/" layer
- `frontend` contains the React/Vite application
- Both services support hot-reload for development

### Using Cursor/VS Code with Dev Container

1. Install the "Remote - Containers" extension in VS Code/Cursor
2. Open the project in VS Code/Cursor
3. Press F1 and select "Remote-Containers: Reopen in Container"
4. Wait for the container to build and start
5. The development environment will be ready with:
   - Python 3.11 with common tools (ruff, black, pytest)
   - Node.js with npm
   - Ports 8000 and 5173 forwarded automatically

### 🚀 Local Backend Development

For faster backend development without Docker:

1. Set up the development environment:
   ```bash
   cd backend
   cp .env.example .env.dev
   ```

2. Start the FastAPI server with hot-reload:
   ```bash
   make dev-backend
   ```

3. Test the API endpoints:
   ```bash
   curl -X POST http://localhost:8000/nlp/apply \
        -H "Content-Type: application/json" \
        -d '{"command":"cut 0-2s"}'
   ```

4. Run unit tests:
   ```bash
   make test
   ```

### Stopping the Development Environment

To stop the development environment:
```bash
make stop
``` 