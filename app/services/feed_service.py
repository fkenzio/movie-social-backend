from sqlalchemy.orm import Session
from sqlalchemy import desc, union_all, select
from typing import Dict
from datetime import datetime
from app.models.rating import Rating
from app.models.review import Review
from app.models.list import List as MovieList
from app.services.tmdb_service import TMDBService


class FeedService:

    @staticmethod
    async def get_global_feed(
            db: Session,
            page: int = 1,
            limit: int = 20
    ) -> Dict:
        """
        Obtener feed global con todas las actividades
        Combina ratings, reviews y listas
        """

        all_activities = []

        # 1. Obtener ratings recientes
        ratings = db.query(Rating) \
            .order_by(desc(Rating.created_at)) \
            .limit(limit * 3) \
            .all()

        for rating in ratings:
            try:
                movie_data = await TMDBService.get_movie_details(rating.movie_tmdb_id)
                all_activities.append({
                    "id": f"rating_{rating.id}",
                    "user_id": rating.user_id,
                    "user": rating.user,
                    "activity_type": "rating",
                    "movie_tmdb_id": rating.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "rating": rating.rating,
                    "created_at": rating.created_at
                })
            except Exception as e:
                print(f"Error fetching movie for rating {rating.id}: {e}")
                continue

        # 2. Obtener reviews recientes
        reviews = db.query(Review) \
            .order_by(desc(Review.created_at)) \
            .limit(limit * 3) \
            .all()

        for review in reviews:
            try:
                movie_data = await TMDBService.get_movie_details(review.movie_tmdb_id)
                all_activities.append({
                    "id": f"review_{review.id}",
                    "user_id": review.user_id,
                    "user": review.user,
                    "activity_type": "review",
                    "movie_tmdb_id": review.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "review_title": review.title,
                    "review_content": review.content[:200] + "..." if len(review.content) > 200 else review.content,
                    "review_contains_spoilers": review.contains_spoilers,
                    "created_at": review.created_at
                })
            except Exception as e:
                print(f"Error fetching movie for review {review.id}: {e}")
                continue

        # 3. Obtener listas creadas recientemente
        lists = db.query(MovieList) \
            .order_by(desc(MovieList.created_at)) \
            .limit(limit * 2) \
            .all()

        for lst in lists:
            all_activities.append({
                "id": f"list_{lst.id}",
                "user_id": lst.user_id,
                "user": lst.user,
                "activity_type": "list_created",
                "list_id": lst.id,
                "list_name": lst.name,
                "list_description": lst.description,
                "created_at": lst.created_at
            })

        # Ordenar todas las actividades por fecha
        all_activities.sort(key=lambda x: x["created_at"], reverse=True)

        # Paginación
        start = (page - 1) * limit
        end = start + limit
        paginated_items = all_activities[start:end]

        total_items = len(all_activities)
        total_pages = (total_items + limit - 1) // limit

        return {
            "items": paginated_items,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items
        }

    @staticmethod
    async def get_user_feed(
            db: Session,
            user_id: int,
            page: int = 1,
            limit: int = 20
    ) -> Dict:
        """
        Obtener feed de un usuario específico
        """

        all_activities = []

        # Ratings del usuario
        ratings = db.query(Rating) \
            .filter(Rating.user_id == user_id) \
            .order_by(desc(Rating.created_at)) \
            .limit(limit * 2) \
            .all()

        for rating in ratings:
            try:
                movie_data = await TMDBService.get_movie_details(rating.movie_tmdb_id)
                all_activities.append({
                    "id": f"rating_{rating.id}",
                    "user_id": rating.user_id,
                    "user": rating.user,
                    "activity_type": "rating",
                    "movie_tmdb_id": rating.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "rating": rating.rating,
                    "created_at": rating.created_at
                })
            except:
                continue

        # Reviews del usuario
        reviews = db.query(Review) \
            .filter(Review.user_id == user_id) \
            .order_by(desc(Review.created_at)) \
            .limit(limit * 2) \
            .all()

        for review in reviews:
            try:
                movie_data = await TMDBService.get_movie_details(review.movie_tmdb_id)
                all_activities.append({
                    "id": f"review_{review.id}",
                    "user_id": review.user_id,
                    "user": review.user,
                    "activity_type": "review",
                    "movie_tmdb_id": review.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "review_title": review.title,
                    "review_content": review.content[:200] + "..." if len(review.content) > 200 else review.content,
                    "review_contains_spoilers": review.contains_spoilers,
                    "created_at": review.created_at
                })
            except:
                continue

        # Listas del usuario
        lists = db.query(MovieList) \
            .filter(MovieList.user_id == user_id) \
            .order_by(desc(MovieList.created_at)) \
            .limit(limit) \
            .all()

        for lst in lists:
            all_activities.append({
                "id": f"list_{lst.id}",
                "user_id": lst.user_id,
                "user": lst.user,
                "activity_type": "list_created",
                "list_id": lst.id,
                "list_name": lst.name,
                "list_description": lst.description,
                "created_at": lst.created_at
            })

        # Ordenar por fecha
        all_activities.sort(key=lambda x: x["created_at"], reverse=True)

        # Paginación
        start = (page - 1) * limit
        end = start + limit
        paginated_items = all_activities[start:end]

        total_items = len(all_activities)
        total_pages = (total_items + limit - 1) // limit

        return {
            "items": paginated_items,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items
        }