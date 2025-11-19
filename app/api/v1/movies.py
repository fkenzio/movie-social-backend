from fastapi import APIRouter, Query
from typing import Optional
from app.services.tmdb_service import TMDBService

router = APIRouter()

@router.get("/search")
async def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1)
):
    """Buscar películas"""
    results = await TMDBService.search_movies(query, page)
    return results

@router.get("/details/{movie_id}")
async def get_movie_details(movie_id: int):
    """Obtener detalles de una película"""
    movie = await TMDBService.get_movie_details(movie_id)
    return movie

@router.get("/popular")
async def get_popular_movies(page: int = Query(1, ge=1)):
    """Obtener películas populares"""
    results = await TMDBService.get_popular_movies(page)
    return results

@router.get("/trending")
async def get_trending_movies(time_window: str = Query("week", regex="^(day|week)$")):
    """Obtener películas en tendencia"""
    results = await TMDBService.get_trending_movies(time_window)
    return results

@router.get("/top-rated")
async def get_top_rated_movies(page: int = Query(1, ge=1)):
    """Obtener películas mejor calificadas"""
    results = await TMDBService.get_top_rated_movies(page)
    return results

@router.get("/now-playing")
async def get_now_playing(page: int = Query(1, ge=1)):
    """Obtener películas en cartelera"""
    results = await TMDBService.get_now_playing(page)
    return results