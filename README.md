# Company Backend Service

Production-style FastAPI backend starter with PostgreSQL, Alembic, JWT auth, and RBAC.

## Architecture

- `app/api/v1` versioned API routers and endpoints
- `app/core` settings and security helpers
- `app/db` SQLAlchemy engine/session
- `app/models` ORM entities
- `app/schemas` request/response models
- `app/services` business logic layer
- `alembic` migrations

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run API

```bash
uvicorn app.main:app --reload
```

## Migrations

```bash
alembic upgrade head
```

## Auth and RBAC

- `POST /api/v1/auth/login` returns a bearer JWT token
- `POST /api/v1/users` requires role `admin`
- `GET /api/v1/users` requires role `admin` or `auditor`
- `GET /api/v1/users/me` requires authentication

## Seed admin user

After migrations, set `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` in `.env` (see `.env.example`), then:

```bash
python scripts/seed_admin.py
```

Creates an admin if missing; promotes an existing user to admin and updates their password if they were not admin yet; no-op if that email is already an admin.
