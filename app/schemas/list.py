from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse


class ListCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True
    is_collaborative: bool = False


class ListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class MovieInList(BaseModel):
    movie_tmdb_id: int
    added_at: datetime
    position: int


class ListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_public: bool
    is_collaborative: bool
    created_at: datetime
    updated_at: datetime
    movies_count: int = 0
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class ListDetailResponse(ListResponse):
    movies: List[MovieInList] = []