from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingUpdate, MovieRatingStats


class RatingService:

    @staticmethod
    def create_or_update_rating(db: Session, user_id: int, rating_data: RatingCreate) -> Rating:
        """Crear o actualizar calificación"""

        # Validar que el rating sea múltiplo de 0.5
        if (rating_data.rating * 2) % 1 != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La calificación debe ser múltiplo de 0.5 (1, 1.5, 2, 2.5, etc.)"
            )

        # Buscar si ya existe un rating
        existing_rating = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_tmdb_id == rating_data.movie_tmdb_id
        ).first()

        if existing_rating:
            # Actualizar rating existente
            existing_rating.rating = rating_data.rating
            db.commit()
            db.refresh(existing_rating)
            return existing_rating
        else:
            # Crear nuevo rating
            new_rating = Rating(
                user_id=user_id,
                movie_tmdb_id=rating_data.movie_tmdb_id,
                rating=rating_data.rating
            )
            db.add(new_rating)
            db.commit()
            db.refresh(new_rating)
            return new_rating

    @staticmethod
    def get_user_rating(db: Session, user_id: int, movie_tmdb_id: int) -> Rating | None:
        """Obtener rating de un usuario para una película"""
        return db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_tmdb_id == movie_tmdb_id
        ).first()

    @staticmethod
    def delete_rating(db: Session, user_id: int, movie_tmdb_id: int) -> bool:
        """Eliminar calificación"""
        rating = db.query(Rating).filter(
            Rating.user_id == user_id,
            Rating.movie_tmdb_id == movie_tmdb_id
        ).first()

        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calificación no encontrada"
            )

        db.delete(rating)
        db.commit()
        return True

    @staticmethod
    def get_movie_stats(db: Session, movie_tmdb_id: int, tmdb_average: float) -> MovieRatingStats:
        """Obtener estadísticas de una película"""

        # Calcular promedio de usuarios
        ratings = db.query(Rating).filter(Rating.movie_tmdb_id == movie_tmdb_id).all()

        total_ratings = len(ratings)
        users_average = 0.0

        if total_ratings > 0:
            users_average = sum(r.rating for r in ratings) / total_ratings

        # Distribución de ratings
        distribution = {
            "5.0": 0, "4.5": 0, "4.0": 0, "3.5": 0, "3.0": 0,
            "2.5": 0, "2.0": 0, "1.5": 0, "1.0": 0
        }

        for rating in ratings:
            key = f"{rating.rating:.1f}"
            if key in distribution:
                distribution[key] += 1

        return MovieRatingStats(
            movie_tmdb_id=movie_tmdb_id,
            tmdb_average=tmdb_average,
            users_average=round(users_average, 1),
            total_ratings=total_ratings,
            rating_distribution=distribution
        )

    @staticmethod
    def get_movie_ratings(db: Session, movie_tmdb_id: int, limit: int = 10):
        """Obtener ratings de una película con usuarios"""
        return db.query(Rating).filter(
            Rating.movie_tmdb_id == movie_tmdb_id
        ).order_by(Rating.created_at.desc()).limit(limit).all()