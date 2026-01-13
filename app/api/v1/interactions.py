from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.interaction import (
    LikeCreate,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    InteractionStats
)
from app.services.interaction_service import InteractionService
from app.services.notification_helpers import notify_on_like

router = APIRouter()


# ==================== LIKES ====================

@router.post("/like")
def toggle_like(
        like_data: LikeCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Toggle like en cualquier objeto"""
    result = InteractionService.toggle_like(
        db,
        current_user.id,
        like_data.target_type,
        like_data.target_id
    )

    if result["liked"]:
        notify_on_like(
            db=db,
            user_id=current_user.id,
            target_type=like_data.target_type,
            target_id=like_data.target_id
        )

    return result


@router.get("/stats")
def get_interaction_stats(
        target_type: str,
        target_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> InteractionStats:
    """Obtener estadísticas de interacción"""
    return InteractionService.get_interaction_stats(
        db,
        current_user.id,
        target_type,
        target_id
    )


# ==================== COMMENTS ====================

@router.post("/comments", response_model=CommentResponse)
def create_comment(
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Crear comentario"""
    comment = InteractionService.create_comment(db, current_user.id, comment_data)

    # Agregar estadísticas
    likes_count = InteractionService.get_likes_count(db, 'comment', comment.id)
    user_has_liked = InteractionService.user_has_liked(db, current_user.id, 'comment', comment.id)

    return {
        **comment.__dict__,
        "replies_count": 0,
        "likes_count": likes_count,
        "user_has_liked": user_has_liked
    }


@router.get("/comments", response_model=List[CommentResponse])
def get_comments(
        target_type: str,
        target_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener comentarios de un objeto"""
    return InteractionService.get_comments(
        db,
        target_type,
        target_id,
        current_user.id,
        skip,
        limit
    )


@router.get("/comments/{comment_id}/replies", response_model=List[CommentResponse])
def get_comment_replies(
        comment_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=50),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener respuestas de un comentario"""
    return InteractionService.get_comment_replies(
        db,
        comment_id,
        current_user.id,
        skip,
        limit
    )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
        comment_id: int,
        comment_data: CommentUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Actualizar comentario"""
    comment = InteractionService.update_comment(db, comment_id, current_user.id, comment_data)

    likes_count = InteractionService.get_likes_count(db, 'comment', comment.id)
    user_has_liked = InteractionService.user_has_liked(db, current_user.id, 'comment', comment.id)
    replies_count = InteractionService.get_comments_count(db, 'comment', comment.id)

    return {
        **comment.__dict__,
        "replies_count": replies_count,
        "likes_count": likes_count,
        "user_has_liked": user_has_liked
    }


@router.delete("/comments/{comment_id}")
def delete_comment(
        comment_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Eliminar comentario"""
    InteractionService.delete_comment(db, comment_id, current_user.id)
    return {"message": "Comentario eliminado"}