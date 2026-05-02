# Phase 01 Setup - Architecture Notes

Last updated: 2026-05-03

## Container Architecture

### Backend Service
- build from `backend/Dockerfile`
- exposes `8000` in container, mapped to host `8002`
- startup command executes `python run.py`
- source mounted from host `./backend:/app`

### Frontend Service
- based on `node:18-alpine`
- working dir `/app`
- startup command `npm install && npm run dev`
- source mounted from host `./frontend:/app`
- ports mapped to `5174` and `3001`

## Connectivity

- shared bridge network: `jpos-cms-net`
- frontend proxy target: `http://jpos-cms-backend:8000`

## Data Layer Mode

- compose currently injects SQLite `DATABASE_URL`
- code remains Oracle/PostgreSQL aware for future deployment targets
