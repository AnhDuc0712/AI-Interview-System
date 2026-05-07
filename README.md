# AI Interview System

A scalable monorepo foundation for an AI-powered interview platform.

## Overview
This repository contains starter infrastructure for:
- Frontend: React + Vite + TypeScript + TailwindCSS + Clerk + React Query + Zustand
- Backend: FastAPI + Python + MongoDB Atlas + Motor + CORS + Async architecture
- Infrastructure: Docker Compose + Devcontainer + GitHub Actions CI

## Local development
1. Copy `.env.example` to `.env` in the repository root.
2. Fill in `MONGODB_URI`, Clerk environment values, and `VITE_API_BASE_URL`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:4173

### Backend
```bash
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```
Open http://localhost:8000

## Docker
From the repository root:
```bash
docker compose -f docker/docker-compose.yml up --build
```

## Health checks
- Frontend: http://localhost:4173
- Backend: http://localhost:8000/health
- API health: http://localhost:8000/api/v1/health

## Architecture
- `frontend/` contains the React app with feature-sliced structure.
- `backend/` contains a FastAPI app with routers, services, repositories, and database wiring.
- `docker/` contains container definitions and compose orchestration.
- `.devcontainer/` provides a VS Code development container.

## Notes
- AI business logic is intentionally not implemented yet.
- MongoDB Atlas connection is prepared using environment configuration.
- Clerk authentication is initialized on the frontend with placeholder values.
