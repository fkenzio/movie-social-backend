from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict
import numpy as np

from ..database import get_db
from ..models import User, Rating
from app.api.deps import get_current_user
from ..services.tmdb_service import TMDBService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationEngine:
    """Motor de recomendaciones usando Filtrado Colaborativo"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_similarity(self, user1_ratings: Dict[int, float], user2_ratings: Dict[int, float]) -> float:
        """Calcula similaridad de coseno entre dos usuarios"""
        # Películas en común
        common_movies = set(user1_ratings.keys()) & set(user2_ratings.keys())

        if len(common_movies) < 3:  # Mínimo 3 películas en común
            return 0.0

        # Vectores de ratings
        vec1 = [user1_ratings[movie] for movie in common_movies]
        vec2 = [user2_ratings[movie] for movie in common_movies]

        # Similaridad de coseno
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = np.sqrt(sum(a ** 2 for a in vec1))
        norm2 = np.sqrt(sum(b ** 2 for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_user_ratings_dict(self, user_id: int) -> Dict[int, float]:
        """Obtiene ratings de un usuario como diccionario {movie_id: rating}"""
        ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
        return {r.movie_tmdb_id: r.rating for r in ratings}

    def find_similar_users(self, user_id: int, top_n: int = 10) -> List[tuple]:
        """Encuentra usuarios similares usando filtrado colaborativo"""
        # Obtener ratings del usuario actual
        current_user_ratings = self.get_user_ratings_dict(user_id)

        print(f"🔍 Usuario {user_id} tiene {len(current_user_ratings)} calificaciones")

        if len(current_user_ratings) < 5:
            print(f"⚠️ Muy pocas calificaciones ({len(current_user_ratings)} < 5)")
            return []

        # Obtener todos los demás usuarios que tienen ratings
        other_users = (
            self.db.query(Rating.user_id)
            .filter(Rating.user_id != user_id)
            .group_by(Rating.user_id)
            .having(func.count(Rating.id) >= 5)
            .all()
        )

        print(f"🔍 Encontrados {len(other_users)} usuarios con 5+ ratings")

        similarities = []

        for (other_user_id,) in other_users:
            other_user_ratings = self.get_user_ratings_dict(other_user_id)
            similarity = self.calculate_similarity(current_user_ratings, other_user_ratings)

            if similarity > 0.3:  # Umbral mínimo de similaridad
                similarities.append((other_user_id, similarity))
                print(f"  ✅ Usuario {other_user_id}: similaridad {similarity:.3f}")

        # Ordenar por similaridad descendente
        similarities.sort(key=lambda x: x[1], reverse=True)

        print(f"🎯 {len(similarities)} usuarios similares encontrados (umbral > 0.3)")

        return similarities[:top_n]

    def get_collaborative_recommendations(
            self,
            user_id: int,
            limit: int = 20
    ) -> List[dict]:
        """Genera recomendaciones usando filtrado colaborativo"""
        # Encontrar usuarios similares
        similar_users = self.find_similar_users(user_id)

        if not similar_users:
            print("⚠️ No hay usuarios similares, retornando lista vacía")
            return []

        print(f"🎬 Generando recomendaciones basadas en {len(similar_users)} usuarios similares")

        # Películas que el usuario ya vio
        user_seen_movies = set(
            self.db.query(Rating.movie_tmdb_id)
            .filter(Rating.user_id == user_id)
            .all()
        )
        user_seen_movies = {m[0] for m in user_seen_movies}

        print(f"🚫 Usuario ya vio {len(user_seen_movies)} películas")

        # Recopilar recomendaciones de usuarios similares
        movie_scores = {}

        for similar_user_id, similarity in similar_users:
            # Ratings del usuario similar (solo películas bien calificadas)
            similar_ratings = (
                self.db.query(Rating)
                .filter(
                    and_(
                        Rating.user_id == similar_user_id,
                        Rating.rating >= 3.5,  # Solo buenas calificaciones
                        Rating.movie_tmdb_id.notin_(user_seen_movies)
                    )
                )
                .all()
            )

            for rating in similar_ratings:
                if rating.movie_tmdb_id not in movie_scores:
                    movie_scores[rating.movie_tmdb_id] = {
                        'total_score': 0,
                        'count': 0,
                        'max_rating': 0
                    }

                # Score ponderado por similaridad
                weighted_score = rating.rating * similarity
                movie_scores[rating.movie_tmdb_id]['total_score'] += weighted_score
                movie_scores[rating.movie_tmdb_id]['count'] += 1
                movie_scores[rating.movie_tmdb_id]['max_rating'] = max(
                    movie_scores[rating.movie_tmdb_id]['max_rating'],
                    rating.rating
                )

        print(f"🎯 {len(movie_scores)} películas candidatas encontradas")

        # Calcular score final y ordenar
        recommendations = []
        for movie_id, scores in movie_scores.items():
            # Score = promedio ponderado
            final_score = scores['total_score'] / scores['count']
            # Normalizar a 0-100
            normalized_score = (final_score / 5.0) * 100

            recommendations.append({
                'movie_tmdb_id': movie_id,
                'score': round(normalized_score, 1),
                'based_on_users': scores['count']
            })

        # Ordenar por score descendente
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        print(f"✅ Retornando {min(len(recommendations), limit)} recomendaciones")

        return recommendations[:limit]


@router.get("/personalized")
async def get_personalized_recommendations(
        limit: int = Query(20, ge=1, le=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene recomendaciones personalizadas usando filtrado colaborativo
    """
    print(f"\n{'=' * 60}")
    print(f"🎯 RECOMENDACIONES PERSONALIZADAS - Usuario {current_user.id}")
    print(f"{'=' * 60}")

    # Verificar que el usuario tenga suficientes ratings
    user_ratings_count = (
        db.query(func.count(Rating.id))
        .filter(Rating.user_id == current_user.id)
        .scalar()
    )

    print(f"📊 Usuario tiene {user_ratings_count} calificaciones")

    if user_ratings_count < 5:
        print(f"⚠️ Insuficientes calificaciones, usando trending como fallback")
        return await get_trending_for_user(limit, db, current_user)

    # Generar recomendaciones
    engine = RecommendationEngine(db)
    recommendations = engine.get_collaborative_recommendations(current_user.id, limit)

    if not recommendations:
        print(f"⚠️ No se generaron recomendaciones colaborativas, usando trending")
        return await get_trending_for_user(limit, db, current_user)

    # Obtener detalles de TMDB (ASYNC)
    results = []
    for rec in recommendations:
        try:
            movie_data = await TMDBService.get_movie_details(rec['movie_tmdb_id'])
            if movie_data and 'id' in movie_data:
                results.append({
                    'movie_tmdb_id': rec['movie_tmdb_id'],
                    'title': movie_data.get('title', ''),
                    'poster_path': movie_data.get('poster_path'),
                    'backdrop_path': movie_data.get('backdrop_path'),
                    'overview': movie_data.get('overview', ''),
                    'release_date': movie_data.get('release_date', ''),
                    'vote_average': movie_data.get('vote_average', 0),
                    'score': rec['score'],
                    'reason': f"Basado en {rec['based_on_users']} usuarios con gustos similares"
                })
        except Exception as e:
            print(f"❌ Error fetching movie {rec['movie_tmdb_id']}: {e}")
            continue

    print(f"✅ Retornando {len(results)} películas al frontend")
    print(f"{'=' * 60}\n")

    # ⚠️ IMPORTANTE: Retornar array directo, no objeto
    return results


@router.get("/trending")
async def get_trending_for_user(
        limit: int = Query(20, ge=1, le=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Películas trending que el usuario no ha visto
    """
    print(f"🔥 Obteniendo trending para usuario {current_user.id}")

    # Películas que el usuario ya vio
    user_seen_movies = set(
        m[0] for m in db.query(Rating.movie_tmdb_id)
        .filter(Rating.user_id == current_user.id)
        .all()
    )

    # Obtener trending de TMDB (ASYNC)
    trending = await TMDBService.get_trending_movies()

    # Filtrar las que no ha visto
    results = []
    for movie in trending.get('results', []):
        if movie['id'] not in user_seen_movies and len(results) < limit:
            results.append({
                'movie_tmdb_id': movie['id'],
                'title': movie.get('title', ''),
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview', ''),
                'release_date': movie.get('release_date', ''),
                'vote_average': movie.get('vote_average', 0),
                'score': 100,
                'reason': 'Tendencia de la semana'
            })

    print(f"✅ Retornando {len(results)} películas trending")
    return results


@router.get("/by-genre")
async def get_by_favorite_genre(
        limit: int = Query(20, ge=1, le=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Recomendaciones basadas en películas top rated que el usuario no ha visto
    """
    print(f"🎭 Obteniendo por género para usuario {current_user.id}")

    # Películas que el usuario ya vio
    user_seen_movies = set(
        m[0] for m in db.query(Rating.movie_tmdb_id)
        .filter(Rating.user_id == current_user.id)
        .all()
    )

    # Buscar películas populares (ASYNC)
    top_rated = await TMDBService.get_top_rated_movies()

    results = []
    for movie in top_rated.get('results', []):
        if movie['id'] not in user_seen_movies and len(results) < limit:
            results.append({
                'movie_tmdb_id': movie['id'],
                'title': movie.get('title', ''),
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview', ''),
                'release_date': movie.get('release_date', ''),
                'vote_average': movie.get('vote_average', 0),
                'score': 90,
                'reason': 'Películas mejor calificadas'
            })

    print(f"✅ Retornando {len(results)} películas por género")
    return results


@router.get("/similar/{movie_id}")
async def get_similar_movies(
        movie_id: int,
        limit: int = Query(10, ge=1, le=20),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Películas similares a una película específica (content-based)
    """
    print(f"🎬 Obteniendo similares a película {movie_id}")

    # Obtener detalles de la película para sacar las similares
    movie_details = await TMDBService.get_movie_details(movie_id)

    # Las similares vienen en el append_to_response="similar"
    similar_movies = movie_details.get('similar', {}).get('results', [])

    # Películas que el usuario ya vio
    user_seen_movies = set(
        m[0] for m in db.query(Rating.movie_tmdb_id)
        .filter(Rating.user_id == current_user.id)
        .all()
    )

    results = []
    for movie in similar_movies:
        if movie['id'] not in user_seen_movies and len(results) < limit:
            results.append({
                'movie_tmdb_id': movie['id'],
                'title': movie.get('title', ''),
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview', ''),
                'release_date': movie.get('release_date', ''),
                'vote_average': movie.get('vote_average', 0),
                'score': 85,
                'reason': 'Similar en temática y estilo'
            })

    print(f"✅ Retornando {len(results)} películas similares")
    return results