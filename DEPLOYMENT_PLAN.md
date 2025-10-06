# Deployment Plan (Render)

This plan targets deploying a Flask API (Postgres-backed) and a Vue SPA to Render.

## Services
- Web Service: Flask API
  - Runtime: Docker (recommended) or native Python
  - Env: `DATABASE_URL`, `SECRET_KEY`
  - Health: `/health`
- Static Site: Vue build output
  - Build: `npm ci && npm run build`
  - Publish: `dist`

## Environment
- Postgres: Use Render Managed Postgres or external (set `DATABASE_URL`)
- Secrets: Configure in Render Dashboard

## Docker (API)
Example Dockerfile (to be added alongside backend source):
```Dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app
EXPOSE 5000
CMD ["python", "-m", "flask", "--app", "backend.app", "run", "--host", "0.0.0.0", "--port", "5000"]
```

## Render Blueprint (optional)
Use a `render.yaml` to define services:
```yaml
services:
  - type: web
    name: reports-api
    runtime: docker
    plan: free
    envVars:
      - key: DATABASE_URL
        fromDatabase: reports-db
      - key: SECRET_KEY
        sync: false
  - type: static
    name: reports-frontend
    buildCommand: npm ci && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_BASE_URL
        value: https://reports-api.onrender.com
databases:
  - name: reports-db
    plan: free
```

## Deployment Steps
1. Prepare repository with backend and frontend directories
2. Add Dockerfile for API and optionally `render.yaml`
3. Push to GitHub
4. In Render:
   - New > Blueprint (if using `render.yaml`) or create services manually
   - Set env vars:
     - API: `DATABASE_URL`, `SECRET_KEY`
     - Frontend: `VITE_API_BASE_URL`
   - Provision managed Postgres
5. First deploy:
   - API: runs migrations (Alembic) via a predeploy command or on startup
   - Frontend: builds and serves static files

## Post-Deployment Checklist
- API `/health` returns 200
- Database migrations applied
- Frontend can load reports pages
- CORS and HTTPS verified
- Error logs are clean
