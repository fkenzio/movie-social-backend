from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserStats(BaseModel):
    total_ratings: int
    total_reviews: int
    total_lists: int
    movies_watched: int
    average_rating: float
    favorite_genre: Optional[str] = None
    most_watched_year: Optional[int] = None


class ActivityItem(BaseModel):
    id: int
    activity_type: str  # 'rating', 'review', 'list_created', 'list_movie_added'
    movie_tmdb_id: Optional[int] = None
    movie_title: Optional[str] = None
    movie_poster: Optional[str] = None
    content: Optional[str] = None  # Para reviews
    rating: Optional[float] = None  # Para ratings
    list_name: Optional[str] = None  # Para listas
    created_at: datetime


class RecentActivity(BaseModel):
    activities: list[ActivityItem]
    total: int


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    stats: UserStats
    recent_activity: list[ActivityItem]

    class Config:
        from_attributes = True
