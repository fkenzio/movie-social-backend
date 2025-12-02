from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse


class FeedItem(BaseModel):
    id: str  # Combinación de tipo + id para unicidad
    user_id: int
    user: UserResponse
    activity_type: str  # 'rating', 'review', 'list_created', 'list_movie_added'
    movie_tmdb_id: Optional[int] = None
    movie_title: Optional[str] = None
    movie_poster: Optional[str] = None
    movie_backdrop: Optional[str] = None
    movie_rating_tmdb: Optional[float] = None
    rating: Optional[float] = None  # Para ratings
    review_title: Optional[str] = None  # Para reviews
    review_content: Optional[str] = None  # Para reviews
    review_contains_spoilers: Optional[bool] = None
    list_id: Optional[int] = None
    list_name: Optional[str] = None
    list_description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    items: list[FeedItem]
    page: int
    total_pages: int
    total_items: int