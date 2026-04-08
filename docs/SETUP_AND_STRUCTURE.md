# Setup and project structure

This document describes how to run the backend locally and how the repository is organized.

## Overview

The service is a **FastAPI** application with:

- **Configuration** loaded from environment variables and a `.env` file (`pydantic-settings`)
- **PostgreSQL** accessed via **SQLAlchemy** (`postgresql+psycopg://…`)
- **Database migrations** with **Alembic**
- **JWT** bearer authentication and **RBAC** roles: `admin`, `user`, `auditor`

The ASGI entrypoint is `app.main:app`.

---

## Prerequisites

- Python 3.11+ (3.13 works with the current stack)
- A running **PostgreSQL** instance reachable at the host/port in your `.env`
- (Optional) `alembic` CLI — installed via `requirements.txt` into the project virtualenv

---

## Setup

### 1. Virtual environment and dependencies

```bash
cd /path/to/rag
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Copy the example file and edit values for your machine:

```bash
cp .env.example .env
```

| Variable | Purpose |
|----------|---------|
| `APP_NAME`, `APP_VERSION` | Shown in OpenAPI and root metadata |
| `DEBUG` | When `true`, enables `/docs` and `/redoc` |
| `API_V1_PREFIX` | Prefix for versioned routes (default `/api/v1`) |
| `POSTGRES_*` | Host, port, user, password, database name for SQLAlchemy |
| `JWT_SECRET_KEY` | Secret for signing JWTs — **change in production** |
| `JWT_ALGORITHM` | e.g. `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |

Settings are defined in `app/core/config.py`; the database URL is built as `sqlalchemy_database_uri`.

### 3. Database and migrations

Ensure PostgreSQL is running and the database in `POSTGRES_DB` exists (create it if needed).

Then apply migrations:

```bash
source .venv/bin/activate
alembic upgrade head
```

Alembic reads the same DSN from settings (`alembic/env.py` sets `sqlalchemy.url` from `settings.sqlalchemy_database_uri`).

### 4. Run the API

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

- API root: `GET /`
- Interactive docs (if `DEBUG=true`): `http://127.0.0.1:8000/docs`
- Versioned API base: `{API_V1_PREFIX}` (default `/api/v1`)

---

## File structure

Below is the layout of the application code and migration tooling (excluding `.venv` and other local artifacts).

```
rag/
├── .env.example              # Template for local secrets and config (copy to .env)
├── .gitignore                # Ignores .venv, __pycache__, .env, etc.
├── requirements.txt          # Python dependencies
├── alembic.ini               # Alembic config (script location, default URL placeholder)
├── alembic/
│   ├── env.py                # Alembic runtime: loads models, applies settings DSN
│   ├── script.py.mako        # Template for new revision files
│   └── versions/
│       └── 20260408_0001_create_users_table.py   # Initial migration (users + role enum)
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app factory, mounts v1 router, root route
│   ├── api/
│   │   ├── deps.py           # get_db, JWT auth, require_roles (RBAC)
│   │   └── v1/
│   │       ├── router.py     # Aggregates v1 endpoint modules
│   │       └── endpoints/
│   │           ├── auth.py   # POST .../auth/login
│   │           ├── health.py # GET .../health
│   │           └── users.py  # User CRUD-style routes (RBAC-protected)
│   ├── core/
│   │   ├── config.py         # Settings + .env + computed DB URI
│   │   └── security.py       # Password hashing, JWT creation
│   ├── db/
│   │   ├── base.py           # Re-exports models for Alembic metadata (import side effects)
│   │   └── session.py        # Engine, SessionLocal, get_db dependency
│   ├── models/
│   │   ├── base.py           # SQLAlchemy DeclarativeBase
│   │   └── user.py           # User ORM model + UserRole enum
│   ├── schemas/
│   │   ├── auth.py           # Login request body
│   │   ├── token.py          # Token response
│   │   └── user.py           # User create/read Pydantic models
│   └── services/
│       └── auth_service.py   # Login verification and token issuance helpers
└── docs/
    └── SETUP_AND_STRUCTURE.md  # This file
```

### Layering (how pieces fit together)

| Area | Role |
|------|------|
| `app/main.py` | Creates the FastAPI app, wires `settings`, includes `api/v1` router |
| `app/api/v1/endpoints/*` | HTTP handlers only; depend on `get_db`, auth, and services |
| `app/api/deps.py` | Shared dependencies: DB session, current user from JWT, role checks |
| `app/services/*` | Business rules (e.g. authenticate user, issue token) |
| `app/schemas/*` | Request/response validation separate from ORM |
| `app/models/*` | SQLAlchemy tables and enums |
| `app/db/session.py` | Engine and session lifecycle |
| `app/core/security.py` | Cryptographic helpers (hashing, JWT) |
| `alembic/` | Schema evolution; keep in sync with `app/models` |

---

## API surface (v1)

All paths below are under `API_V1_PREFIX` (default `/api/v1`).

| Method | Path | Auth / roles |
|--------|------|----------------|
| GET | `/health` | Public |
| POST | `/auth/login` | Public (returns JWT) |
| GET | `/users/me` | Authenticated user |
| POST | `/users` | `admin` |
| GET | `/users` | `admin` or `auditor` |

OpenAPI shows the exact payloads; login uses OAuth2-style bearer tokens for protected routes.

---

## RBAC

Roles are stored on the `users` table (`UserRole`: `admin`, `user`, `auditor`). Endpoint protection uses `require_roles(...)` in `app/api/deps.py` so authorization stays centralized and easy to audit.

---

## Operational notes

- **First admin user**: After migrations, create an initial `admin` user in the database (or add a small seed script) before relying on `POST /users`.
- **Production**: Set a strong `JWT_SECRET_KEY`, set `DEBUG=false`, use TLS in front of the app, and restrict database credentials.

For a short quickstart, see also `README.md` in the project root.
