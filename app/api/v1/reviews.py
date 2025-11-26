from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    MovieReviewsStats
)
from app.services.review_service import ReviewService

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una reseña"""
    review = ReviewService.create_review(db, current_user.id, review_data)
    return review


@router.get("/movie/{movie_tmdb_id}", response_model=List[ReviewResponse])
def get_movie_reviews(
    movie_tmdb_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    include_spoilers: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Obtener todas las reseñas de una película"""
    reviews = ReviewService.get_movie_reviews(
        db, movie_tmdb_id, skip, limit, include_spoilers
    )
    return reviews


@router.get("/movie/{movie_tmdb_id}/stats", response_model=MovieReviewsStats)
def get_movie_reviews_stats(
    movie_tmdb_id: int,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de reseñas de una película"""
    return ReviewService.get_movie_reviews_stats(db, movie_tmdb_id)


@router.get("/movie/{movie_tmdb_id}/user", response_model=ReviewResponse | None)
def get_user_review_for_movie(
    movie_tmdb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener la reseña del usuario actual para una película"""
    review = ReviewService.get_user_review_for_movie(
        db, current_user.id, movie_tmdb_id
    )
    return review


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_user_reviews(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obtener todas las reseñas de un usuario"""
    reviews = ReviewService.get_user_reviews(db, user_id, skip, limit)
    return reviews


@router.get("/recent", response_model=List[ReviewResponse])
def get_recent_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obtener las reseñas más recientes"""
    reviews = ReviewService.get_recent_reviews(db, skip, limit)
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una reseña por ID"""
    review = ReviewService.get_review_by_id(db, review_id)
    if not review:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar una reseña"""
    review = ReviewService.update_review(db, review_id, current_user.id, review_data)
    return review


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una reseña"""
    ReviewService.delete_review(db, review_id, current_user.id)
    return {"message": "Reseña eliminada exitosamente"}