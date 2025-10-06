# Marketing Reports & Invoices (Flask + Postgres + Vue)

## Overview
A web application for importing CSV/JSON data from multiple sources, generating consolidated reports with spreadsheet-ready tables, and producing PDF invoices. Built with Python Flask, Postgres, SQLAlchemy, and Vue 3.

## Features
- Admin UI (Vue 3) with grouped pages and dark-friendly tables
- Data ingestion (CSV/JSON)
  - Google Data (CSV): Account, Campaign, Cost; weekly/monthly presets
  - Rumble Data (CSV): Campaign, Spend, CPM
  - Binom Rumble Spent (CSV): Name, Leads, Revenue (semicolon + quoted; skips revenue <= 0)
  - Binom Google Spent (CSV): Name, Leads, Revenue (weekly/monthly)
  - Rumble Campaign Data (JSON): Name, CPM, Daily Limit parsing
- Reports
  - Rumble - Binom Report with strict date joins, identity matching, COPY TABLE (TSV + styled HTML)
  - Google Binom Report with strict 1:1 matching, ROI Last mode (Full vs Cohort), COPY SUMMARY
- Invoices
  - Invoice generator and CRUD, line items with live totals
  - Numbering: `INV-YYYY-NNN`
  - PDF generation (WeasyPrint), filename `Allan - {invoice_number}.pdf`

## Tech Stack
- Python, Flask, SQLAlchemy
- Postgres
- Vue 3 (Vite, Pinia, TypeScript)

## Project Status
- Phase 0 (Bootstrap) — completed
  - Flask app factory, CORS, health route (`GET /health`)
  - Blueprints: uploads, reports, invoices (stub endpoints active)
  - SQLAlchemy engine/session setup
  - Alembic configured
  - Docker Compose for Postgres
  - `.env.example` files and `.gitignore`
- Phase 1 (Data Ingestion & Storage) — completed (initial schema)
  - SQLAlchemy models for datasets and invoices
  - Initial Alembic migration created and applied
  - Uploads/list/delete endpoints stubbed (persistence to be implemented next)
 - Phase 2 (Ingestion + Frontend + Google Binom Report) — completed
   - Ingestion persistence:
     - `POST /api/uploads/google` (CSV: Account/Account Name, Campaign, Cost)
     - `POST /api/uploads/binom-google` (CSV; semicolon-delimited; Name, Leads, Revenue; skips revenue <= 0)
     - Batch views: `GET /api/google/batches`, `GET /api/binom-google/batches`
     - Delete: `DELETE /api/google`, `DELETE /api/binom-google` (filter by `date_from`, `date_to`, `report_type`)
   - Reports:
     - `GET /api/reports/google-binom` joining spend vs revenue by normalized campaign/name with summary totals
   - Frontend (Vue 3 + Vite + TS + Router + Pinia):
     - Pages: Google Data, Binom Google Spent Data, Google Binom Report
     - Top nav: “Google and Binom Reports Only” dropdown menu

## Local Development
### Backend
- Prerequisites: Python 3.12+, Docker Desktop (for local Postgres)
- Install:
```bash
# From project root, start Postgres
docker compose up -d

# Create a venv and install deps (run inside backend/)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit DATABASE_URL, SECRET_KEY if needed
alembic upgrade head
flask --app app run --port 5000
```

### Frontend
- Prerequisites: Node 18+
- Install:
```bash
cd frontend
# First time: generate lockfile and install
npm install
cp .env.example .env  # set VITE_API_BASE_URL (e.g., http://localhost:5000)
npm run dev
```

## Environment Variables
### Backend (`backend/.env`)
- `SECRET_KEY=...`
- `DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname`

### Frontend (`frontend/.env`)
- `VITE_API_BASE_URL=http://localhost:5000`

Notes:
- Commit `.env.example`, never commit real `.env`.
- Use strong secrets in production and managed Postgres credentials.

## Database & Migrations
- SQLAlchemy ORM models
- Alembic for migrations

## Quick Smoke Tests
Run while the server is up at http://localhost:5000

```bash
# Health
curl http://localhost:5000/health

# Upload Google CSV (comma CSV with headers: Account, Campaign, Cost)
# Windows PowerShell: use curl.exe and adjust file path
curl.exe -F "file=@google.csv" -F "date_from=2025-09-29" -F "date_to=2025-10-05" -F "report_type=weekly" \
  http://localhost:5000/api/uploads/google

# Upload Binom Google CSV (semicolon; quoted; headers: Name, Leads, Revenue)
curl.exe -F "file=@binom_google.csv" -F "date_from=2025-09-29" -F "date_to=2025-10-05" -F "report_type=weekly" \
  http://localhost:5000/api/uploads/binom-google

# Batches
curl http://localhost:5000/api/google/batches
curl http://localhost:5000/api/binom-google/batches

# Google Binom Report
curl "http://localhost:5000/api/reports/google-binom?report_type=weekly&date_from=2025-09-29&date_to=2025-10-05&roi_last_mode=full"

# (Stub) Rumble Binom Report
curl "http://localhost:5000/api/reports/rumble-binom?report_type=weekly&date_from=2025-09-29&date_to=2025-10-05"

# Invoices (stubs)
curl http://localhost:5000/api/invoices
curl -X POST http://localhost:5000/api/invoices -H "Content-Type: application/json" -d "{}"
```

## Database Inspection
- DBeaver (recommended): connect to `localhost:5432`, database `reports_db`, user `postgres`, password `postgres`, then expand `public` → `Tables`.
- CLI:
```bash
docker exec -it reports_db psql -U postgres -d reports_db -c "\\dt"
```

## Project Structure
```
flask-vue-report-system/
  backend/
    app/__init__.py
    models/
    routes/
    services/
MIT
