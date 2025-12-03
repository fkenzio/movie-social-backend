from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse


class LikeCreate(BaseModel):
    target_type: str = Field(..., pattern="^(rating|review|list|comment)$")
    target_id: int


class CommentCreate(BaseModel):
    target_type: str = Field(..., pattern="^(rating|review|list)$")
    target_id: int
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    user_id: int
    target_type: str
    target_id: int
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None
    replies_count: int = 0
    likes_count: int = 0
    user_has_liked: bool = False

    class Config:
        from_attributes = True


class CommentWithRepliesResponse(CommentResponse):
    replies: List[CommentResponse] = []


class InteractionStats(BaseModel):
    likes_count: int
    comments_count: int
    user_has_liked: bool
    user_has_commented: bool