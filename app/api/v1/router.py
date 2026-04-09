from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, pdf, search, users

api_router = APIRouter()
api_router.include_router(health.router, prefix='/health', tags=['health'])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(pdf.router, prefix='/pdf', tags=['pdf'])
api_router.include_router(search.router, prefix='', tags=['search'])
