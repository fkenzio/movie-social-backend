from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationStats
from fastapi import HTTPException, status
import asyncio
from collections import defaultdict


class NotificationService:
    # Almacén de clientes SSE conectados
    _connections: dict[int, list] = defaultdict(list)

    @staticmethod
    def create_notification(
            db: Session,
            user_id: int,
            actor_id: int,
            notification_type: NotificationType,
            target_type: str = None,
            target_id: int = None,
            movie_tmdb_id: int = None,
            movie_title: str = None,
            content_preview: str = None
    ) -> Notification:
        """Crear una nueva notificación"""

        # No crear notificación si el actor es el mismo usuario
        if user_id == actor_id:
            return None

        # Verificar si ya existe una notificación similar reciente (últimos 5 minutos)
        # Esto previene spam de notificaciones
        from datetime import datetime, timedelta
        recent_time = datetime.now() - timedelta(minutes=5)

        existing = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.actor_id == actor_id,
                Notification.type == notification_type,
                Notification.target_type == target_type,
                Notification.target_id == target_id,
                Notification.created_at >= recent_time
            )
        ).first()

        if existing:
            return existing

        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            type=notification_type,
            target_type=target_type,
            target_id=target_id,
            movie_tmdb_id=movie_tmdb_id,
            movie_title=movie_title,
            content_preview=content_preview
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Enviar notificación en tiempo real via SSE
        NotificationService._send_realtime_notification(notification)

        return notification

    @staticmethod
    def get_user_notifications(
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 20,
            unread_only: bool = False
    ) -> List[Notification]:
        """Obtener notificaciones del usuario"""

        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

        # Cargar datos del actor
        for notification in notifications:
            notification.actor_data = {
                "id": notification.actor.id,
                "username": notification.actor.username,
                "full_name": notification.actor.full_name
            }

        return notifications

    @staticmethod
    def get_notification_stats(db: Session, user_id: int) -> NotificationStats:
        """Obtener estadísticas de notificaciones"""

        total = db.query(Notification).filter(Notification.user_id == user_id).count()
        unread = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()

        return NotificationStats(total=total, unread=unread)

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
        """Marcar notificación como leída"""

        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )

        notification.is_read = True
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Marcar todas las notificaciones como leídas"""

        count = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({"is_read": True})

        db.commit()
        return count

    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> None:
        """Eliminar notificación"""

        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )

        db.delete(notification)
        db.commit()

    # ========== SSE (Server-Sent Events) ==========

    @staticmethod
    def add_sse_connection(user_id: int, queue: asyncio.Queue):
        """Agregar conexión SSE para un usuario"""
        NotificationService._connections[user_id].append(queue)

    @staticmethod
    def remove_sse_connection(user_id: int, queue: asyncio.Queue):
        """Remover conexión SSE de un usuario"""
        if user_id in NotificationService._connections:
            try:
                NotificationService._connections[user_id].remove(queue)
                if not NotificationService._connections[user_id]:
                    del NotificationService._connections[user_id]
            except ValueError:
                pass

    @staticmethod
    def _send_realtime_notification(notification: Notification):
        """Enviar notificación en tiempo real a clientes conectados"""
        user_id = notification.user_id

        if user_id not in NotificationService._connections:
            return

        # Preparar datos de la notificación
        notification_data = {
            "id": notification.id,
            "type": notification.type.value,
            "actor": {
                "id": notification.actor.id,
                "username": notification.actor.username,
                "full_name": notification.actor.full_name
            },
            "target_type": notification.target_type,
            "target_id": notification.target_id,
            "movie_tmdb_id": notification.movie_tmdb_id,
            "movie_title": notification.movie_title,
            "content_preview": notification.content_preview,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat()
        }

        # Enviar a todas las conexiones del usuario
        for queue in NotificationService._connections[user_id]:
            try:
                queue.put_nowait(notification_data)
            except asyncio.QueueFull:
                pass


# ========== Funciones helper para crear notificaciones específicas ==========

def create_like_notification(
        db: Session,
        target_owner_id: int,
        liker_id: int,
        target_type: str,
        target_id: int,
        movie_tmdb_id: int = None,
        movie_title: str = None
):
    """Crear notificación de like"""
    return NotificationService.create_notification(
        db=db,
        user_id=target_owner_id,
        actor_id=liker_id,
        notification_type=NotificationType.LIKE,
        target_type=target_type,
        target_id=target_id,
        movie_tmdb_id=movie_tmdb_id,
        movie_title=movie_title
    )


def create_comment_notification(
        db: Session,
        target_owner_id: int,
        commenter_id: int,
        target_type: str,
        target_id: int,
        comment_preview: str,
        movie_tmdb_id: int = None,
        movie_title: str = None
):
    """Crear notificación de comentario"""
    return NotificationService.create_notification(
        db=db,
        user_id=target_owner_id,
        actor_id=commenter_id,
        notification_type=NotificationType.COMMENT,
        target_type=target_type,
        target_id=target_id,
        content_preview=comment_preview[:100],  # Primeros 100 caracteres
        movie_tmdb_id=movie_tmdb_id,
        movie_title=movie_title
    )


def create_reply_notification(
        db: Session,
        comment_owner_id: int,
        replier_id: int,
        comment_id: int,
        reply_preview: str,
        movie_tmdb_id: int = None,
        movie_title: str = None
):
    """Crear notificación de respuesta a comentario"""
    return NotificationService.create_notification(
        db=db,
        user_id=comment_owner_id,
        actor_id=replier_id,
        notification_type=NotificationType.REPLY,
        target_type="comment",
        target_id=comment_id,
        content_preview=reply_preview[:100],
        movie_tmdb_id=movie_tmdb_id,
        movie_title=movie_title
    )