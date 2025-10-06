# Phase Plan – Flask + Postgres + SQLAlchemy + Vue.js

## Phase 0 — Project Bootstrap
- Create repository structure: `backend/` (Flask), `frontend/` (Vue 3), `docs/`
- Choose packaging: `requirements.txt` for backend, `package.json` for frontend
- Configure base settings and environment variables
  - Backend: `.env` (loaded via python-dotenv) with `DATABASE_URL`, `SECRET_KEY`
  - Frontend: `.env` with `VITE_API_BASE_URL`
- Establish coding standards: Ruff + Black + isort, mypy (backend); ESLint + Prettier + TypeScript strict (frontend)
- Initialize Alembic for database migrations

Deliverables:
- Minimal Flask app factory, health endpoint
- SQLAlchemy session setup, Alembic scaffolding
- Vue 3 app scaffold (Vite), base layout, router, Pinia store

## Phase 1 — Data Ingestion & Storage
- Define Postgres schema and SQLAlchemy models for datasets
  - `google_data`, `rumble_data`, `binom_rumble_spent_data`, `binom_google_spent_data`, `rumble_campaign_data`
  - Common fields: `date_from`, `date_to`, `report_type` with composite indexes
  - `uploads` table for audit (filename, checksum, uploaded_at)
- Implement secure CSV/JSON uploads
  - Validate content-type, size, and required columns
  - Normalize headers, handle quoted semicolon CSV
  - Persist rows in a single transaction per upload batch
- Data management endpoints
  - Delete All, Delete by Upload Date, Delete by Date Category

Deliverables:
- POST `/api/uploads/:source` endpoints (google, rumble, binom-rumble, binom-google, rumble-campaign)
- GET grouped list endpoints for latest batches per source
- Alembic migrations created and applied

## Phase 2 — Admin Pages: Google and Binom Reports
- Frontend admin pages (Vue)
  - Google Data: CSV upload, grouped list by date range, per-group delete
  - Binom Google Spent Data: CSV upload, grouped list (weekly/monthly), info modal for export settings
  - Google Binom Report: weekly/monthly table, strict 1:1 matching (ID-only when present, else exact sanitized-name), ROI Last mode toggle (Full vs Cohort), COPY TABLE and COPY SUMMARY
- Backend support
  - Upload endpoints and grouped batch listings for Google and Binom Google sources
  - GET `/api/reports/google-binom` implementing strict matching and ROI Last computation
  - Copy builders (TSV + styled HTML) with formulas and conditional colors

Deliverables:
- Routes and components for the three admin pages above
- GET `/api/:source/batches` + delete endpoints for data management
- GET `/api/reports/google-binom` with ROI Last (Full/Cohort) toggle
- COPY TABLE and COPY SUMMARY actions implemented (TSV + HTML)

## Phase 3 — Admin Pages: Rumble and Binom Reports
- Frontend admin pages (Vue)
  - Rumble Data: CSV upload, grouped list by date range, per-group delete
  - Rumble Campaign Data: JSON upload, robust header normalization, daily limit parsing
  - Binom Rumble Spent Data: CSV (semicolon + quoted), skip revenue <= 0, info modal
  - Rumble - Binom Report: strict joins on `(date_from, date_to, report_type)`, campaign identity resolution (ID-first → sanitized name → base-name → substring contains), COPY TABLE with formulas/formatting
- Backend support
  - Upload endpoints and grouped batch listings for Rumble and Binom Rumble sources
  - GET `/api/reports/rumble-binom` with computed columns (Account, Campaign, Daily Cap, Spend, Revenue, P/L, ROI, Conversions, CPM, Set CPM)
  - Copy builder for TSV + styled HTML

Deliverables:
- Routes and components for the four admin pages above
- GET `/api/:source/batches` + delete endpoints
- GET `/api/reports/rumble-binom`
- COPY TABLE action implemented (TSV + HTML)

## Phase 4 — Admin Pages: Invoices
- Models: `invoices`, `invoice_items`, `invoice_sequences`
- Numbering: transactional sequence per `year` → `INV-YYYY-NNN`
- CRUD endpoints and UI pages
- PDF generation via WeasyPrint (HTML template), filename `Allan - {invoice_number}.pdf`
- Draft email endpoint (optional later)

Deliverables:
- REST CRUD for invoices and items
- GET `/api/invoices/:id/pdf` (stream)
- Frontend Invoice Generator + All Invoices list

## Phase 5 — OAuth & Integrations (Optional for day-one)
- OAuth flow and token storage for Google
- Create Sheet endpoints for both reports with formatting and folder placement
- Create Draft endpoints for both reports (summary HTML) and invoice PDFs

Deliverables:
- OAuth endpoints and status checks
- Sheet/Draft endpoints functioning with proper error handling

## Phase 6 — Hardening & Deployment
- Tests: unit for parsers/matchers, service tests for report joins, API tests
- Observability: structured logs, request IDs, error handling
- Containerization and deployment
  - Dockerfiles for backend and frontend
  - Render Blueprint for web (Flask) and static site (Vue)

Deliverables:
- Passing test suite and coverage summary
- Deployment notes and environment configuration

---

## API Surface (Initial)
- Auth: POST `/api/auth/login`, GET `/api/auth/me` (if needed)
- Uploads: POST `/api/uploads/:source`, GET `/api/:source/batches`, DELETE scoped endpoints
- Reports: GET `/api/reports/rumble-binom`, GET `/api/reports/google-binom`
- Invoices: CRUD `/api/invoices`, GET `/api/invoices/:id/pdf`

## Today’s Execution Order
1) Phase 0 minimal scaffolds (backend health, DB connect, frontend shell)
2) Phase 1 ingestion for at least two sources to unlock reports
3) Phase 2 admin pages: Google and Binom Reports
4) Phase 3 admin pages: Rumble and Binom Reports
5) Phase 4 admin pages: Invoices with numbering and PDF
6) Phase 6 containerize and deploy to Render
