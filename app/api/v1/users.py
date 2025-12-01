from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user_stats import UserProfileResponse, UserStats, RecentActivity
from app.services.user_stats_service import UserStatsService

router = APIRouter()


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener perfil completo del usuario actual"""
    profile = await UserStatsService.get_user_profile_complete(db, current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )

    return profile


@router.get("/me/stats", response_model=UserStats)
def get_my_stats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener solo las estadísticas del usuario actual"""
    return UserStatsService.get_user_stats(db, current_user.id)


@router.get("/me/activity")
async def get_my_activity(
        limit: int = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener actividad reciente del usuario actual"""
    activities = await UserStatsService.get_recent_activity(db, current_user.id, limit)
    return {
        "activities": activities,
        "total": len(activities)
    }


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Obtener perfil público de cualquier usuario"""
    profile = await UserStatsService.get_user_profile_complete(db, user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return profile


@router.get("/{user_id}/stats", response_model=UserStats)
def get_user_stats(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Obtener estadísticas públicas de cualquier usuario"""
    return UserStatsService.get_user_stats(db, user_id)