from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional
from app.models.rating import Rating
from app.services.tmdb_service import TMDBService


class RankingService:

    @staticmethod
    async def get_tmdb_top_rated(page: int = 1, limit: int = 20) -> Dict:
        """
        Obtener películas mejor calificadas de TMDB
        """
        tmdb_data = await TMDBService.get_top_rated_movies(page)

        # Transformar datos para el formato de ranking
        rankings = []
        for idx, movie in enumerate(tmdb_data.get('results', []), start=(page - 1) * 20 + 1):
            rankings.append({
                'rank': idx,
                'movie_tmdb_id': movie['id'],
                'title': movie['title'],
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'release_date': movie.get('release_date'),
                'overview': movie.get('overview'),
                'tmdb_rating': round(movie['vote_average'] / 2, 1),  # Convertir a escala 1-5
                'tmdb_votes': movie['vote_count'],
                'genre_ids': movie.get('genre_ids', [])
            })

        return {
            'rankings': rankings,
            'page': tmdb_data.get('page', page),
            'total_pages': tmdb_data.get('total_pages', 1),
            'total_results': tmdb_data.get('total_results', 0),
            'source': 'tmdb'
        }

    @staticmethod
    def get_users_top_rated(
            db: Session,
            page: int = 1,
            limit: int = 20,
            min_ratings: int = 5  # Mínimo de calificaciones para aparecer en ranking
    ) -> Dict:
        """
        Obtener películas mejor calificadas por usuarios de Cineminha
        """
        # Calcular promedio y contar ratings por película
        query = db.query(
            Rating.movie_tmdb_id,
            func.avg(Rating.rating).label('average_rating'),
            func.count(Rating.id).label('total_ratings')
        ).group_by(
            Rating.movie_tmdb_id
        ).having(
            func.count(Rating.id) >= min_ratings  # Filtrar películas con suficientes votos
        ).order_by(
            desc('average_rating'),
            desc('total_ratings')  # En caso de empate, priorizar más votadas
        )

        # Paginación
        offset = (page - 1) * limit
        results = query.offset(offset).limit(limit).all()

        # Contar total de películas que cumplen el criterio
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit

        # Formatear resultados
        rankings = []
        for idx, result in enumerate(results, start=offset + 1):
            rankings.append({
                'rank': idx,
                'movie_tmdb_id': result.movie_tmdb_id,
                'users_average': round(result.average_rating, 1),
                'total_ratings': result.total_ratings
            })

        return {
            'rankings': rankings,
            'page': page,
            'total_pages': total_pages,
            'total_results': total_count,
            'source': 'users',
            'min_ratings_required': min_ratings
        }

    @staticmethod
    async def get_combined_ranking(
            db: Session,
            page: int = 1,
            limit: int = 20,
            min_ratings: int = 3
    ) -> Dict:
        """
        Ranking combinado: Muestra datos tanto de TMDB como de usuarios
        """
        # Obtener ranking de usuarios
        users_ranking = RankingService.get_users_top_rated(
            db, page, limit, min_ratings
        )

        # Obtener IDs de películas
        movie_ids = [r['movie_tmdb_id'] for r in users_ranking['rankings']]

        # Obtener detalles de TMDB para cada película
        rankings_with_details = []
        for ranking in users_ranking['rankings']:
            try:
                # Obtener detalles de TMDB
                movie_details = await TMDBService.get_movie_details(
                    ranking['movie_tmdb_id']
                )

                rankings_with_details.append({
                    'rank': ranking['rank'],
                    'movie_tmdb_id': ranking['movie_tmdb_id'],
                    'title': movie_details.get('title'),
                    'poster_path': movie_details.get('poster_path'),
                    'backdrop_path': movie_details.get('backdrop_path'),
                    'release_date': movie_details.get('release_date'),
                    'overview': movie_details.get('overview'),
                    'genres': movie_details.get('genres', []),
                    'tmdb_rating': round(movie_details.get('vote_average', 0) / 2, 1),
                    'tmdb_votes': movie_details.get('vote_count', 0),
                    'users_average': ranking['users_average'],
                    'total_ratings': ranking['total_ratings']
                })
            except Exception as e:
                print(f"Error fetching movie {ranking['movie_tmdb_id']}: {e}")
                continue

        return {
            'rankings': rankings_with_details,
            'page': users_ranking['page'],
            'total_pages': users_ranking['total_pages'],
            'total_results': users_ranking['total_results'],
            'source': 'combined',
            'min_ratings_required': min_ratings
        }

    @staticmethod
    async def get_trending_this_week(page: int = 1) -> Dict:
        """
        Películas en tendencia esta semana según TMDB
        """
        trending_data = await TMDBService.get_trending_movies('week')

        rankings = []
        for idx, movie in enumerate(trending_data.get('results', [])[:20], start=1):
            rankings.append({
                'rank': idx,
                'movie_tmdb_id': movie['id'],
                'title': movie['title'],
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'release_date': movie.get('release_date'),
                'overview': movie.get('overview'),
                'tmdb_rating': round(movie['vote_average'] / 2, 1),
                'popularity': movie.get('popularity'),
                'genre_ids': movie.get('genre_ids', [])
            })

        return {
            'rankings': rankings,
            'page': page,
            'total_pages': 1,
            'total_results': len(rankings),
            'source': 'trending'
        }

    @staticmethod
    def get_user_stats_ranking(
            db: Session,
            page: int = 1,
            limit: int = 20
    ) -> Dict:
        """
        Ranking de usuarios más activos (por cantidad de ratings)
        """
        from app.models.user import User

        query = db.query(
            User,
            func.count(Rating.id).label('total_ratings'),
            func.avg(Rating.rating).label('average_given')
        ).join(
            Rating, User.id == Rating.user_id
        ).group_by(
            User.id
        ).order_by(
            desc('total_ratings')
        )

        offset = (page - 1) * limit
        results = query.offset(offset).limit(limit).all()

        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit

        rankings = []
        for idx, (user, total_ratings, avg_rating) in enumerate(results, start=offset + 1):
            rankings.append({
                'rank': idx,
                'user_id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'total_ratings': total_ratings,
                'average_rating_given': round(avg_rating, 1) if avg_rating else 0
            })

        return {
            'rankings': rankings,
            'page': page,
            'total_pages': total_pages,
            'total_results': total_count,
            'source': 'users_stats'
        }