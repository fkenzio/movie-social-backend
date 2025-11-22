from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.ranking_service import RankingService

router = APIRouter()


@router.get("/tmdb/top-rated")
async def get_tmdb_top_rated(
    page: int = Query(1, ge=1, le=500),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Ranking de películas mejor calificadas según TMDB
    """
    return await RankingService.get_tmdb_top_rated(page, limit)


@router.get("/users/top-rated")
def get_users_top_rated(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_ratings: int = Query(5, ge=1, description="Mínimo de calificaciones requeridas"),
    db: Session = Depends(get_db)
):
    """
    Ranking de películas mejor calificadas por usuarios de Cineminha
    """
    return RankingService.get_users_top_rated(db, page, limit, min_ratings)


@router.get("/combined")
async def get_combined_ranking(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_ratings: int = Query(3, ge=1),
    db: Session = Depends(get_db)
):
    """
    Ranking combinado: muestra datos de TMDB y usuarios
    """
    return await RankingService.get_combined_ranking(db, page, limit, min_ratings)


@router.get("/trending")
async def get_trending_this_week(
    page: int = Query(1, ge=1)
):
    """
    Películas en tendencia esta semana según TMDB
    """
    return await RankingService.get_trending_this_week(page)


@router.get("/users-stats")
def get_user_stats_ranking(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Ranking de usuarios más activos
    """
    return RankingService.get_user_stats_ranking(db, page, limit)