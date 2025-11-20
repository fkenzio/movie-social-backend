from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingResponse, MovieRatingStats
from app.services.rating_service import RatingService

router = APIRouter()

@router.post("/", response_model=RatingResponse)
def create_or_update_rating(
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear o actualizar calificación"""
    rating = RatingService.create_or_update_rating(db, current_user.id, rating_data)
    return rating

@router.get("/movie/{movie_tmdb_id}/user", response_model=RatingResponse | None)
def get_user_rating(
    movie_tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener rating del usuario actual para una película"""
    rating = RatingService.get_user_rating(db, current_user.id, movie_tmdb_id)
    return rating

@router.get("/movie/{movie_tmdb_id}/stats")
def get_movie_stats(
    movie_tmdb_id: int,
    tmdb_average: float = 0.0,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de calificaciones de una película"""
    return RatingService.get_movie_stats(db, movie_tmdb_id, tmdb_average)

@router.delete("/movie/{movie_tmdb_id}")
def delete_rating(
    movie_tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar calificación"""
    RatingService.delete_rating(db, current_user.id, movie_tmdb_id)
    return {"message": "Calificación eliminada"}

@router.get("/movie/{movie_tmdb_id}/all", response_model=list[RatingResponse])
def get_movie_ratings(
    movie_tmdb_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Obtener todas las calificaciones de una película"""
    return RatingService.get_movie_ratings(db, movie_tmdb_id, limit)