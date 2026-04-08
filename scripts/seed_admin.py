"""Create or promote an admin user using SEED_* variables from .env / environment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def _connection_help() -> str:
    return (
        f'Could not connect to PostgreSQL at {settings.postgres_host}:{settings.postgres_port} '
        f'(database {settings.postgres_db}).\n'
        '- Ensure the server is running and reachable from this machine.\n'
        '- If you use Docker: start the container; if Postgres is published on the host, '
        'set POSTGRES_HOST=localhost (not the container IP from an old run).\n'
        '- Run migrations after the DB is up: alembic upgrade head'
    )


def main() -> int:
    if not settings.seed_admin_email or not settings.seed_admin_password:
        print(
            'Missing seed configuration. Set SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD in .env.',
            file=sys.stderr,
        )
        return 1

    db = SessionLocal()
    try:
        try:
            email = settings.seed_admin_email.strip().lower()
            user = db.query(User).filter(User.email == email).first()

            if user:
                if user.role != UserRole.admin:
                    user.role = UserRole.admin
                    user.hashed_password = get_password_hash(settings.seed_admin_password)
                    if settings.seed_admin_full_name:
                        user.full_name = settings.seed_admin_full_name
                    db.commit()
                    print(f'Promoted existing user to admin: {email}')
                else:
                    print(f'Admin user already exists: {email}')
                return 0

            new_user = User(
                email=email,
                hashed_password=get_password_hash(settings.seed_admin_password),
                full_name=settings.seed_admin_full_name,
                role=UserRole.admin,
                is_active=True,
            )
            db.add(new_user)
            db.commit()
            print(f'Created admin user: {email}')
            return 0
        except OperationalError:
            print(_connection_help(), file=sys.stderr)
            return 1
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(main())
