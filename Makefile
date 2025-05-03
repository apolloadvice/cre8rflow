.PHONY: dev stop dev-backend test

dev:
	docker compose up --build

stop:
	docker compose down --remove-orphans

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && pytest -q

# Add a script to run the backend in dev mode
scripts/dev_backend.sh:
	mkdir -p scripts
	echo '#!/bin/bash\nmake dev-backend' > scripts/dev_backend.sh
	chmod +x scripts/dev_backend.sh 