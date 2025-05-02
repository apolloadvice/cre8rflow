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
   # 1. Copy environment template and fill in your secrets
   cp .env.example .env

   # 2. Build & start the whole stack
   make dev

   # 3. Visit the app
   open http://localhost:5173
   ```

3. The development environment will be ready with:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/docs

### Using Cursor/VS Code with Dev Container

1. Install the "Remote - Containers" extension in VS Code/Cursor
2. Open the project in VS Code/Cursor
3. Press F1 and select "Remote-Containers: Reopen in Container"
4. Wait for the container to build and start
5. The development environment will be ready with:
   - Python 3.11 with common tools (ruff, black, pytest)
   - Node.js with npm
   - Ports 8000 and 5173 forwarded automatically

### Stopping the Development Environment

To stop the development environment:
```bash
make stop
``` 