from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException, status
from typing import List, Dict
from app.models.like import Like
from app.models.comment import Comment
from app.schemas.interaction import CommentCreate, CommentUpdate
from app.services.notification_helpers import notify_on_comment


class InteractionService:

    # ==================== LIKES ====================

    @staticmethod
    def toggle_like(db: Session, user_id: int, target_type: str, target_id: int) -> Dict:
        """Toggle like: si existe lo elimina, si no existe lo crea"""

        existing_like = db.query(Like).filter(
            Like.user_id == user_id,
            Like.target_type == target_type,
            Like.target_id == target_id
        ).first()

        if existing_like:
            db.delete(existing_like)
            db.commit()
            return {"liked": False, "message": "Like eliminado"}
        else:
            new_like = Like(
                user_id=user_id,
                target_type=target_type,
                target_id=target_id
            )
            db.add(new_like)
            db.commit()
            return {"liked": True, "message": "Like agregado"}

    @staticmethod
    def get_likes_count(db: Session, target_type: str, target_id: int) -> int:
        """Obtener cantidad de likes"""
        return db.query(Like).filter(
            Like.target_type == target_type,
            Like.target_id == target_id
        ).count()

    @staticmethod
    def user_has_liked(db: Session, user_id: int, target_type: str, target_id: int) -> bool:
        """Verificar si el usuario dio like"""
        return db.query(Like).filter(
            Like.user_id == user_id,
            Like.target_type == target_type,
            Like.target_id == target_id
        ).first() is not None

    # ==================== COMMENTS ====================

    @staticmethod
    def create_comment(db: Session, user_id: int, comment_data: CommentCreate) -> Comment:
        """Crear comentario"""

        # Validar que parent_id exista si se proporciona
        if comment_data.parent_id:
            parent = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comentario padre no encontrado"
                )

            # Asegurar que el parent sea del mismo target
            if parent.target_type != comment_data.target_type or parent.target_id != comment_data.target_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El comentario padre debe ser del mismo objetivo"
                )

        new_comment = Comment(
            user_id=user_id,
            target_type=comment_data.target_type,
            target_id=comment_data.target_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id
        )

        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        notify_on_comment(
            db=db,
            user_id=user_id,
            target_type=comment_data.target_type,
            target_id=comment_data.target_id,
            comment_content=comment_data.content,
            parent_id=comment_data.parent_id
        )
        return new_comment

    @staticmethod
    def get_comments(
            db: Session,
            target_type: str,
            target_id: int,
            current_user_id: int,
            skip: int = 0,
            limit: int = 50
    ) -> List[Dict]:
        """Obtener comentarios con estadísticas"""

        # Solo comentarios de primer nivel (sin parent_id)
        comments = db.query(Comment).filter(
            Comment.target_type == target_type,
            Comment.target_id == target_id,
            Comment.parent_id == None
        ).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

        result = []
        for comment in comments:
            # Contar respuestas
            replies_count = db.query(Comment).filter(
                Comment.parent_id == comment.id
            ).count()

            # Contar likes del comentario
            likes_count = InteractionService.get_likes_count(db, 'comment', comment.id)

            # Verificar si el usuario actual dio like
            user_has_liked = InteractionService.user_has_liked(db, current_user_id, 'comment', comment.id)

            result.append({
                "id": comment.id,
                "user_id": comment.user_id,
                "user": comment.user,
                "target_type": comment.target_type,
                "target_id": comment.target_id,
                "content": comment.content,
                "parent_id": comment.parent_id,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "replies_count": replies_count,
                "likes_count": likes_count,
                "user_has_liked": user_has_liked
            })

        return result

    @staticmethod
    def get_comment_replies(
            db: Session,
            comment_id: int,
            current_user_id: int,
            skip: int = 0,
            limit: int = 20
    ) -> List[Dict]:
        """Obtener respuestas de un comentario"""

        replies = db.query(Comment).filter(
            Comment.parent_id == comment_id
        ).order_by(Comment.created_at.asc()).offset(skip).limit(limit).all()

        result = []
        for reply in replies:
            likes_count = InteractionService.get_likes_count(db, 'comment', reply.id)
            user_has_liked = InteractionService.user_has_liked(db, current_user_id, 'comment', reply.id)

            result.append({
                "id": reply.id,
                "user_id": reply.user_id,
                "user": reply.user,
                "target_type": reply.target_type,
                "target_id": reply.target_id,
                "content": reply.content,
                "parent_id": reply.parent_id,
                "created_at": reply.created_at,
                "updated_at": reply.updated_at,
                "replies_count": 0,
                "likes_count": likes_count,
                "user_has_liked": user_has_liked
            })

        return result

    @staticmethod
    def update_comment(db: Session, comment_id: int, user_id: int, comment_data: CommentUpdate) -> Comment:
        """Actualizar comentario"""

        comment = db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.user_id == user_id
        ).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario no encontrado"
            )

        comment.content = comment_data.content
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
        """Eliminar comentario"""

        comment = db.query(Comment).filter(
            Comment.id == comment_id,
            Comment.user_id == user_id
        ).first()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario no encontrado"
            )

        db.delete(comment)
        db.commit()
        return True

    @staticmethod
    def get_comments_count(db: Session, target_type: str, target_id: int) -> int:
        """Obtener cantidad total de comentarios"""
        return db.query(Comment).filter(
            Comment.target_type == target_type,
            Comment.target_id == target_id
        ).count()

    # ==================== STATS ====================

    @staticmethod
    def get_interaction_stats(
            db: Session,
            user_id: int,
            target_type: str,
            target_id: int
    ) -> Dict:
        """Obtener estadísticas completas de interacción"""

        likes_count = InteractionService.get_likes_count(db, target_type, target_id)
        comments_count = InteractionService.get_comments_count(db, target_type, target_id)
        user_has_liked = InteractionService.user_has_liked(db, user_id, target_type, target_id)

        user_has_commented = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.target_type == target_type,
            Comment.target_id == target_id
        ).first() is not None

        return {
            "likes_count": likes_count,
            "comments_count": comments_count,
            "user_has_liked": user_has_liked,
            "user_has_commented": user_has_commented
        }