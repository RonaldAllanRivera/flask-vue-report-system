# Changelog
All notable changes to this project will be documented in this file.

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
