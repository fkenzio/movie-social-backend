from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class RatingCreate(BaseModel):
    movie_tmdb_id: int
    rating: float = Field(ge=1.0, le=5.0)  # Entre 1.0 y 5.0

    # Validar que sea múltiplo de 0.5
    class Config:
        json_schema_extra = {
            "example": {
                "movie_tmdb_id": 27205,
                "rating": 4.5
            }
        }


class RatingUpdate(BaseModel):
    rating: float = Field(ge=1.0, le=5.0)


class RatingResponse(BaseModel):
    id: int
    user_id: int
    movie_tmdb_id: int
    rating: float
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class MovieRatingStats(BaseModel):
    movie_tmdb_id: int
    tmdb_average: float  # Promedio de TMDB (0-10)
    users_average: float  # Promedio de usuarios Cineminha (1-5)
    total_ratings: int
    rating_distribution: dict  # Distribución de ratings