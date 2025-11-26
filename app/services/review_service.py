from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, MovieReviewsStats


class ReviewService:

    @staticmethod
    def create_review(db: Session, user_id: int, review_data: ReviewCreate) -> Review:
        """Crear una reseña"""

        # Verificar si el usuario ya tiene una review para esta película
        existing_review = db.query(Review).filter(
            Review.user_id == user_id,
            Review.movie_tmdb_id == review_data.movie_tmdb_id
        ).first()

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya tienes una reseña para esta película. Puedes editarla."
            )

        # Crear la review
        new_review = Review(
            user_id=user_id,
            movie_tmdb_id=review_data.movie_tmdb_id,
            title=review_data.title,
            content=review_data.content,
            contains_spoilers=review_data.contains_spoilers
        )

        db.add(new_review)
        db.commit()
        db.refresh(new_review)
        return new_review

    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
        """Obtener una review por ID"""
        return db.query(Review).filter(Review.id == review_id).first()

    @staticmethod
    def get_user_review_for_movie(
            db: Session,
            user_id: int,
            movie_tmdb_id: int
    ) -> Optional[Review]:
        """Obtener la review de un usuario para una película específica"""
        return db.query(Review).filter(
            Review.user_id == user_id,
            Review.movie_tmdb_id == movie_tmdb_id
        ).first()

    @staticmethod
    def get_movie_reviews(
            db: Session,
            movie_tmdb_id: int,
            skip: int = 0,
            limit: int = 10,
            include_spoilers: bool = True
    ) -> List[Review]:
        """Obtener todas las reviews de una película"""

        query = db.query(Review).filter(Review.movie_tmdb_id == movie_tmdb_id)

        # Filtrar spoilers si el usuario no quiere verlos
        if not include_spoilers:
            query = query.filter(Review.contains_spoilers == False)

        return query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_reviews(
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> List[Review]:
        """Obtener todas las reviews de un usuario"""
        return db.query(Review).filter(
            Review.user_id == user_id
        ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def update_review(
            db: Session,
            review_id: int,
            user_id: int,
            review_data: ReviewUpdate
    ) -> Review:
        """Actualizar una review"""

        review = db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reseña no encontrada o no tienes permiso para editarla"
            )

        # Actualizar campos
        if review_data.title is not None:
            review.title = review_data.title
        if review_data.content is not None:
            review.content = review_data.content
        if review_data.contains_spoilers is not None:
            review.contains_spoilers = review_data.contains_spoilers

        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete_review(db: Session, review_id: int, user_id: int) -> bool:
        """Eliminar una review"""

        review = db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reseña no encontrada o no tienes permiso para eliminarla"
            )

        db.delete(review)
        db.commit()
        return True

    @staticmethod
    def get_movie_reviews_stats(db: Session, movie_tmdb_id: int) -> MovieReviewsStats:
        """Obtener estadísticas de reviews de una película"""

        total_reviews = db.query(Review).filter(
            Review.movie_tmdb_id == movie_tmdb_id
        ).count()

        has_spoilers = db.query(Review).filter(
            Review.movie_tmdb_id == movie_tmdb_id,
            Review.contains_spoilers == True
        ).count()

        without_spoilers = total_reviews - has_spoilers

        return MovieReviewsStats(
            movie_tmdb_id=movie_tmdb_id,
            total_reviews=total_reviews,
            has_spoilers=has_spoilers,
            without_spoilers=without_spoilers
        )

    @staticmethod
    def get_recent_reviews(
            db: Session,
            skip: int = 0,
            limit: int = 20
    ) -> List[Review]:
        """Obtener las reviews más recientes de todas las películas"""
        return db.query(Review).order_by(
            desc(Review.created_at)
        ).offset(skip).limit(limit).all()