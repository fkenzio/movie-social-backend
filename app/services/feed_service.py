from sqlalchemy.orm import Session
from sqlalchemy import desc, union_all, select
from typing import Dict
from datetime import datetime
from app.models.rating import Rating
from app.models.review import Review
from app.models.list import List as MovieList
from app.services.tmdb_service import TMDBService
from app.services.interaction_service import InteractionService  # ⬅️ AGREGAR IMPORT


class FeedService:

    @staticmethod
    async def get_global_feed(
            db: Session,
            page: int = 1,
            limit: int = 20,
            current_user_id: int = None  # ⬅️ AGREGAR PARÁMETRO
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

                # ⬇️ AGREGAR ESTADÍSTICAS DE INTERACCIÓN
                stats = InteractionService.get_interaction_stats(
                    db, current_user_id, 'rating', rating.id
                ) if current_user_id else {
                    "likes_count": InteractionService.get_likes_count(db, 'rating', rating.id),
                    "comments_count": InteractionService.get_comments_count(db, 'rating', rating.id),
                    "user_has_liked": False,
                    "user_has_commented": False
                }

                all_activities.append({
                    "id": f"rating_{rating.id}",
                    "user_id": rating.user_id,
                    "user": rating.user,
                    "activity_type": "rating",
                    "target_id": rating.id,  # ⬅️ AGREGAR
                    "movie_tmdb_id": rating.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "rating": rating.rating,
                    "created_at": rating.created_at,
                    # ⬇️ AGREGAR ESTADÍSTICAS
                    "likes_count": stats["likes_count"],
                    "comments_count": stats["comments_count"],
                    "user_has_liked": stats["user_has_liked"],
                    "user_has_commented": stats["user_has_commented"]
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

                # ⬇️ AGREGAR ESTADÍSTICAS DE INTERACCIÓN
                stats = InteractionService.get_interaction_stats(
                    db, current_user_id, 'review', review.id
                ) if current_user_id else {
                    "likes_count": InteractionService.get_likes_count(db, 'review', review.id),
                    "comments_count": InteractionService.get_comments_count(db, 'review', review.id),
                    "user_has_liked": False,
                    "user_has_commented": False
                }

                all_activities.append({
                    "id": f"review_{review.id}",
                    "user_id": review.user_id,
                    "user": review.user,
                    "activity_type": "review",
                    "target_id": review.id,  # ⬅️ AGREGAR
                    "movie_tmdb_id": review.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "review_title": review.title,
                    "review_content": review.content[:200] + "..." if len(review.content) > 200 else review.content,
                    "review_contains_spoilers": review.contains_spoilers,
                    "created_at": review.created_at,
                    # ⬇️ AGREGAR ESTADÍSTICAS
                    "likes_count": stats["likes_count"],
                    "comments_count": stats["comments_count"],
                    "user_has_liked": stats["user_has_liked"],
                    "user_has_commented": stats["user_has_commented"]
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
            # ⬇️ AGREGAR ESTADÍSTICAS DE INTERACCIÓN
            stats = InteractionService.get_interaction_stats(
                db, current_user_id, 'list', lst.id
            ) if current_user_id else {
                "likes_count": InteractionService.get_likes_count(db, 'list', lst.id),
                "comments_count": InteractionService.get_comments_count(db, 'list', lst.id),
                "user_has_liked": False,
                "user_has_commented": False
            }

            all_activities.append({
                "id": f"list_{lst.id}",
                "user_id": lst.user_id,
                "user": lst.user,
                "activity_type": "list_created",
                "target_id": lst.id,  # ⬅️ AGREGAR
                "list_id": lst.id,
                "list_name": lst.name,
                "list_description": lst.description,
                "created_at": lst.created_at,
                # ⬇️ AGREGAR ESTADÍSTICAS
                "likes_count": stats["likes_count"],
                "comments_count": stats["comments_count"],
                "user_has_liked": stats["user_has_liked"],
                "user_has_commented": stats["user_has_commented"]
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
            limit: int = 20,
            current_user_id: int = None  # ⬅️ AGREGAR PARÁMETRO
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

                # ⬇️ AGREGAR ESTADÍSTICAS DE INTERACCIÓN
                stats = InteractionService.get_interaction_stats(
                    db, current_user_id or user_id, 'rating', rating.id
                )

                all_activities.append({
                    "id": f"rating_{rating.id}",
                    "user_id": rating.user_id,
                    "user": rating.user,
                    "activity_type": "rating",
                    "target_id": rating.id,
                    "movie_tmdb_id": rating.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "rating": rating.rating,
                    "created_at": rating.created_at,
                    "likes_count": stats["likes_count"],
                    "comments_count": stats["comments_count"],
                    "user_has_liked": stats["user_has_liked"],
                    "user_has_commented": stats["user_has_commented"]
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

                # ⬇️ AGREGAR ESTADÍSTICAS DE INTERACCIÓN
                stats = InteractionService.get_interaction_stats(
                    db, current_user_id or user_id, 'review', review.id
                )

                all_activities.append({
                    "id": f"review_{review.id}",
                    "user_id": review.user_id,
                    "user": review.user,
                    "activity_type": "review",
                    "target_id": review.id,
                    "movie_tmdb_id": review.movie_tmdb_id,
                    "movie_title": movie_data.get("title"),
                    "movie_poster": movie_data.get("poster_path"),
                    "movie_backdrop": movie_data.get("backdrop_path"),
                    "movie_rating_tmdb": movie_data.get("vote_average", 0) / 2,
                    "review_title": review.title,
                    "review_content": review.content[:200] + "..." if len(review.content) > 200 else review.content,
                    "review_contains_spoilers": review.contains_spoilers,
                    "created_at": review.created_at,
                    "likes_count": stats["likes_count"],
                    "comments_count": stats["comments_count"],
                    "user_has_liked": stats["user_has_liked"],
                    "user_has_commented": stats["user_has_commented"]
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
            # ⬇️ AGREGAR ESTADÍSTICAS DE INTERACCIÓN
            stats = InteractionService.get_interaction_stats(
                db, current_user_id or user_id, 'list', lst.id
            )

            all_activities.append({
                "id": f"list_{lst.id}",
                "user_id": lst.user_id,
                "user": lst.user,
                "activity_type": "list_created",
                "target_id": lst.id,
                "list_id": lst.id,
                "list_name": lst.name,
                "list_description": lst.description,
                "created_at": lst.created_at,
                "likes_count": stats["likes_count"],
                "comments_count": stats["comments_count"],
                "user_has_liked": stats["user_has_liked"],
                "user_has_commented": stats["user_has_commented"]
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