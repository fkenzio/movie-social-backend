from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.feed import FeedResponse
from app.services.feed_service import FeedService

router = APIRouter()


@router.get("/", response_model=FeedResponse)
async def get_global_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener feed global con toda la actividad de la comunidad
    """
    return await FeedService.get_global_feed(db, page, limit, current_user.id)


@router.get("/user/{user_id}", response_model=FeedResponse)
async def get_user_feed(
    user_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener feed de actividad de un usuario específico
    """
    return await FeedService.get_user_feed(db, current_user.id, page, limit, current_user.id)


@router.get("/me", response_model=FeedResponse)
async def get_my_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener mi feed personal
    """
    return await FeedService.get_user_feed(db, current_user.id, page, limit)