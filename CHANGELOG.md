# Changelog
All notable changes to this project will be documented in this file.

## [0.3.1] - 2025-10-06
### Added
- Frontend client-side validation for uploads:
  - Google Data: block JSON and wrong CSV schema; show inserted count.
  - Binom Google: validate semicolon CSV with Name/Revenue; show inserted count.
- Downloadable sample CSV for Google at `/samples/google_sample.csv` and button on `/google`.
- Favicon link to reduce 404 favicon requests.

### Changed
- UI: standardized control heights across inputs/selects/buttons/file inputs (`h-10 text-sm`).
- README: recent changes, sample data, troubleshooting, and API behavior sections.

### Fixed
- Backend ingestion robustness:
  - Skip leading title/date lines before header in Google weekly exports.
  - Accept header variants and currency-formatted numbers.
  - Return HTTP 400 with `status: "no_rows"` when no rows inserted.
- Batch counts: label SQL `count(*)` as `row_count` to avoid `Row.count()` collision; API returns correct `count`.

## [0.3.0] - 2025-10-06
### Added
- Phase 2: Ingestion + Frontend + Google Binom Report
  - Backend ingestion persistence:
    - `POST /api/uploads/google` (CSV parser)
    - `POST /api/uploads/binom-google` (semicolon CSV; skips revenue <= 0)
    - Batch listings: `GET /api/google/batches`, `GET /api/binom-google/batches`
    - Delete endpoints for both sources
  - Google Binom report endpoint `GET /api/reports/google-binom` with spend/revenue join and summary
  - Frontend scaffold (Vite + Vue 3 + TS + Router + Pinia) with pages for Google, Binom Google, and Report
  - Top menu consolidated to “Google and Binom Reports Only” with dropdown

## [0.2.0] - 2025-10-06
### Added
- Phase 0 Bootstrap completed:
  - Flask app factory with CORS and `GET /health`
  - Blueprints: uploads, reports, invoices (stub endpoints)
  - SQLAlchemy engine/session configuration
  - Alembic configured
  - Docker Compose for Postgres (`db` service)
  - `.env.example` files and `.gitignore`
- Phase 1 Initial Schema completed:
  - Models for datasets (`google_data`, `rumble_data`, `binom_rumble_spent_data`, `binom_google_spent_data`, `rumble_campaign_data`) and invoices
  - Alembic migration creating all core tables
  - Stubs for uploads/list/delete endpoints

## [0.1.0] - 2025-10-06
### Added
- Project scaffolding plan (PLAN.md) with phase breakdown
- Documentation for local development and environment variables (README.md)
- Deployment plan outline for Render (DEPLOYMENT_PLAN.md)
- Initial feature set mirroring reporting and invoices:
  - CSV/JSON ingestion endpoints (design)
  - Reports: Rumble - Binom, Google Binom (design)
  - Invoices: CRUD, INV-YYYY-NNN numbering, PDF generation (design)
