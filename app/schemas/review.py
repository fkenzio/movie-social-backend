from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class ReviewCreate(BaseModel):
    movie_tmdb_id: int
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    contains_spoilers: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "movie_tmdb_id": 27205,
                "title": "Una obra maestra del cine",
                "content": "Inception es una película que te hace pensar...",
                "contains_spoilers": False
            }
        }


class ReviewUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    contains_spoilers: Optional[bool] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    movie_tmdb_id: int
    title: Optional[str]
    content: str
    contains_spoilers: bool
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class MovieReviewsStats(BaseModel):
    movie_tmdb_id: int
    total_reviews: int
    has_spoilers: int
    without_spoilers: int