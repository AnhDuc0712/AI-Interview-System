# Architecture Overview

This repository follows a monorepo approach with:

- `frontend/` for the React + Vite application.
- `backend/` for the FastAPI Python service.
- `docker/` for container definitions.
- `.github/workflows/` for CI/CD automation.

The frontend is organized in a feature-sliced structure, while the backend follows routers -> services -> repositories/AI modules.
