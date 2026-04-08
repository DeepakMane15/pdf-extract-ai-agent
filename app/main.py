from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url='/docs' if settings.debug else None,
    redoc_url='/redoc' if settings.debug else None,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get('/', tags=['root'])
def root() -> dict[str, str]:
    return {'service': settings.app_name, 'status': 'running'}
