from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.models.user import User
from app.models.rating import Rating
from app.models.review import Review
from app.models.list import List as MovieList
from app.services.tmdb_service import TMDBService


class UserStatsService:

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict:
        """Obtener estadísticas generales del usuario"""

        # Total de ratings
        total_ratings = db.query(Rating).filter(Rating.user_id == user_id).count()

        # Total de reviews
        total_reviews = db.query(Review).filter(Review.user_id == user_id).count()

        # Total de listas
        total_lists = db.query(MovieList).filter(MovieList.user_id == user_id).count()

        # Películas vistas (películas únicas que ha calificado)
        movies_watched = db.query(Rating.movie_tmdb_id) \
            .filter(Rating.user_id == user_id) \
            .distinct() \
            .count()

        # Promedio de calificaciones
        avg_rating = db.query(func.avg(Rating.rating)) \
                         .filter(Rating.user_id == user_id) \
                         .scalar() or 0.0

        # Género favorito (el más calificado)
        favorite_genre = UserStatsService._get_favorite_genre(db, user_id)

        # Año más visto
        most_watched_year = UserStatsService._get_most_watched_year(db, user_id)

        return {
            "total_ratings": total_ratings,
            "total_reviews": total_reviews,
            "total_lists": total_lists,
            "movies_watched": movies_watched,
            "average_rating": round(avg_rating, 1),
            "favorite_genre": favorite_genre,
            "most_watched_year": most_watched_year
        }

    @staticmethod
    def _get_favorite_genre(db: Session, user_id: int) -> Optional[str]:
        """Obtener el género favorito basado en las películas mejor calificadas"""
        try:
            # Obtener las películas mejor calificadas del usuario (4.0+)
            high_rated = db.query(Rating.movie_tmdb_id, Rating.rating) \
                .filter(Rating.user_id == user_id) \
                .filter(Rating.rating >= 4.0) \
                .all()

            if not high_rated:
                return None

            # Contador de géneros
            genre_count = {}

            for movie_id, rating in high_rated:
                # Aquí podrías guardar los géneros en caché o en la BD
                # Por simplicidad, asumimos que ya los tienes
                # En producción, considera guardar géneros en tu BD
                pass

            # Por ahora retornamos None, pero puedes implementar la lógica completa
            return None

        except Exception as e:
            print(f"Error getting favorite genre: {e}")
            return None

    @staticmethod
    def _get_most_watched_year(db: Session, user_id: int) -> Optional[int]:
        """Año más visto (placeholder - necesitaría datos de películas)"""
        return None

    @staticmethod
    async def get_recent_activity(
            db: Session,
            user_id: int,
            limit: int = 20
    ) -> list[Dict]:
        """Obtener actividad reciente del usuario"""
        activities = []

        # Obtener ratings recientes
        ratings = db.query(Rating) \
            .filter(Rating.user_id == user_id) \
            .order_by(desc(Rating.created_at)) \
            .limit(limit) \
            .all()

        for rating in ratings:
            try:
                movie_data = await TMDBService.get_movie_details(rating.movie_tmdb_id)
                activities.append({
                    "id": rating.id,
                    "activity_type": "rating",
                    "movie_tmdb_id": rating.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "rating": rating.rating,
                    "created_at": rating.created_at
                })
            except:
                continue

        # Obtener reviews recientes
        reviews = db.query(Review) \
            .filter(Review.user_id == user_id) \
            .order_by(desc(Review.created_at)) \
            .limit(limit) \
            .all()

        for review in reviews:
            try:
                movie_data = await TMDBService.get_movie_details(review.movie_tmdb_id)
                activities.append({
                    "id": review.id,
                    "activity_type": "review",
                    "movie_tmdb_id": review.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "content": review.content[:100] + "..." if len(review.content) > 100 else review.content,
                    "created_at": review.created_at
                })
            except:
                continue

        # Obtener listas creadas recientemente
        lists = db.query(MovieList) \
            .filter(MovieList.user_id == user_id) \
            .order_by(desc(MovieList.created_at)) \
            .limit(10) \
            .all()

        for lst in lists:
            activities.append({
                "id": lst.id,
                "activity_type": "list_created",
                "list_name": lst.name,
                "created_at": lst.created_at
            })

        # Ordenar todas las actividades por fecha
        activities.sort(key=lambda x: x["created_at"], reverse=True)

        return activities[:limit]

    @staticmethod
    async def get_user_profile_complete(db: Session, user_id: int) -> Dict:
        """Obtener perfil completo del usuario con stats y actividad"""

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        stats = UserStatsService.get_user_stats(db, user_id)
        recent_activity = await UserStatsService.get_recent_activity(db, user_id, 10)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at,
            "stats": stats,
            "recent_activity": recent_activity
        }
