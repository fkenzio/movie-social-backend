from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse


class FeedItem(BaseModel):
    id: str  # Combinación de tipo + id para unicidad
    user_id: int
    user: UserResponse
    activity_type: str  # 'rating', 'review', 'list_created', 'list_movie_added'
    target_id: int  # ⬅️ AGREGAR: ID del objeto real (rating.id, review.id, list.id)

    # Movie info
    movie_tmdb_id: Optional[int] = None
    movie_title: Optional[str] = None
    movie_poster: Optional[str] = None
    movie_backdrop: Optional[str] = None
    movie_rating_tmdb: Optional[float] = None

    # Rating info
    rating: Optional[float] = None

    # Review info
    review_title: Optional[str] = None
    review_content: Optional[str] = None
    review_contains_spoilers: Optional[bool] = None

    # List info
    list_id: Optional[int] = None
    list_name: Optional[str] = None
    list_description: Optional[str] = None

    # Timestamps
    created_at: datetime

    # ⬇️ AGREGAR: Estadísticas de interacción
    likes_count: int = 0
    comments_count: int = 0
    user_has_liked: bool = False
    user_has_commented: bool = False

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    items: list[FeedItem]
    page: int
    total_pages: int
    total_items: int