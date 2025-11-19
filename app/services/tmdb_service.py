import httpx
from typing import Optional, List, Dict
from app.config import settings


class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

    @staticmethod
    async def search_movies(query: str, page: int = 1) -> Dict:
        """Buscar películas por nombre"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDBService.BASE_URL}/search/movie",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "query": query,
                    "page": page,
                    "language": "es-MX"
                }
            )
            return response.json()

    @staticmethod
    async def get_movie_details(movie_id: int) -> Dict:
        """Obtener detalles de una película"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDBService.BASE_URL}/movie/{movie_id}",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "es-MX",
                    "append_to_response": "credits,videos,similar"
                }
            )
            return response.json()

    @staticmethod
    async def get_popular_movies(page: int = 1) -> Dict:
        """Obtener películas populares"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDBService.BASE_URL}/movie/popular",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "page": page,
                    "language": "es-MX"
                }
            )
            return response.json()

    @staticmethod
    async def get_trending_movies(time_window: str = "week") -> Dict:
        """Obtener películas en tendencia"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDBService.BASE_URL}/trending/movie/{time_window}",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "es-MX"
                }
            )
            return response.json()

    @staticmethod
    async def get_top_rated_movies(page: int = 1) -> Dict:
        """Obtener películas mejor calificadas"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDBService.BASE_URL}/movie/top_rated",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "page": page,
                    "language": "es-MX"
                }
            )
            return response.json()

    @staticmethod
    async def get_now_playing(page: int = 1) -> Dict:
        """Obtener películas en cartelera"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TMDBService.BASE_URL}/movie/now_playing",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "page": page,
                    "language": "es-MX",
                    "region": "MX"
                }
            )
            return response.json()

    @staticmethod
    def get_image_url(path: str, size: str = "w500") -> str:
        """Construir URL de imagen"""
        if not path:
            return ""
        return f"{TMDBService.IMAGE_BASE_URL}/{size}{path}"