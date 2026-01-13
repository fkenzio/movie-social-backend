from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    actor_id: int
    target_type: str | None
    target_id: int | None
    movie_tmdb_id: int | None
    movie_title: str | None
    content_preview: str | None
    is_read: bool
    created_at: str

    # Datos del actor (quien hizo la acción)
    actor: dict = None

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    is_read: bool


class NotificationStats(BaseModel):
    total: int
    unread: int