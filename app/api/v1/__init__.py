from fastapi import APIRouter
from app.api.v1 import auth, users, movies

api_router = APIRouter()

# Registrar todas las rutas
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])