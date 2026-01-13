from sqlalchemy.orm import Session
from app.services.notification_service import (
    create_like_notification,
    create_comment_notification,
    create_reply_notification
)
from app.models.rating import Rating
from app.models.review import Review
from app.models.list import List
from app.models.comment import Comment


def notify_on_like(
        db: Session,
        user_id: int,  # Usuario que da el like
        target_type: str,  # rating, review, list, comment
        target_id: int
):
    """
    Crear notificación cuando alguien da like a algo.
    Llamar esta función en el servicio de likes después de crear el like.
    """
    try:
        # Obtener el dueño del objeto y datos adicionales
        owner_id = None
        movie_tmdb_id = None
        movie_title = None

        if target_type == "rating":
            rating = db.query(Rating).filter(Rating.id == target_id).first()
            if rating:
                owner_id = rating.user_id
                movie_tmdb_id = rating.movie_tmdb_id

        elif target_type == "review":
            review = db.query(Review).filter(Review.id == target_id).first()
            if review:
                owner_id = review.user_id
                movie_tmdb_id = review.movie_tmdb_id

        elif target_type == "list":
            lst = db.query(List).filter(List.id == target_id).first()
            if lst:
                owner_id = lst.user_id

        elif target_type == "comment":
            comment = db.query(Comment).filter(Comment.id == target_id).first()
            if comment:
                owner_id = comment.user_id

        if owner_id and owner_id != user_id:
            create_like_notification(
                db=db,
                target_owner_id=owner_id,
                liker_id=user_id,
                target_type=target_type,
                target_id=target_id,
                movie_tmdb_id=movie_tmdb_id,
                movie_title=movie_title
            )
    except Exception as e:
        print(f"Error creating like notification: {e}")


def notify_on_comment(
        db: Session,
        user_id: int,  # Usuario que comenta
        target_type: str,  # rating, review, list
        target_id: int,
        comment_content: str,
        parent_id: int = None  # Si es una respuesta a otro comentario
):
    """
    Crear notificación cuando alguien comenta algo.
    Si parent_id existe, es una respuesta a un comentario.
    Llamar esta función en el servicio de comments después de crear el comentario.
    """
    try:
        # Si es una respuesta a un comentario
        if parent_id:
            parent_comment = db.query(Comment).filter(Comment.id == parent_id).first()
            if parent_comment and parent_comment.user_id != user_id:
                create_reply_notification(
                    db=db,
                    comment_owner_id=parent_comment.user_id,
                    replier_id=user_id,
                    comment_id=parent_id,
                    reply_preview=comment_content
                )
        else:
            # Es un comentario nuevo en un objeto
            owner_id = None
            movie_tmdb_id = None
            movie_title = None

            if target_type == "rating":
                rating = db.query(Rating).filter(Rating.id == target_id).first()
                if rating:
                    owner_id = rating.user_id
                    movie_tmdb_id = rating.movie_tmdb_id

            elif target_type == "review":
                review = db.query(Review).filter(Review.id == target_id).first()
                if review:
                    owner_id = review.user_id
                    movie_tmdb_id = review.movie_tmdb_id

            elif target_type == "list":
                lst = db.query(List).filter(List.id == target_id).first()
                if lst:
                    owner_id = lst.user_id

            if owner_id and owner_id != user_id:
                create_comment_notification(
                    db=db,
                    target_owner_id=owner_id,
                    commenter_id=user_id,
                    target_type=target_type,
                    target_id=target_id,
                    comment_preview=comment_content,
                    movie_tmdb_id=movie_tmdb_id,
                    movie_title=movie_title
                )
    except Exception as e:
        print(f"Error creating comment notification: {e}")