from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationUpdate, NotificationStats
from app.services.notification_service import NotificationService
from app.utils.security import decode_token
from app.models.user import User
from fastapi import Query
import asyncio
import json

router = APIRouter()


# ========== ENDPOINTS REST ==========

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener notificaciones del usuario"""
    notifications = NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )

    # Formatear respuesta con datos del actor
    result = []
    for notif in notifications:
        notif_dict = {
            "id": notif.id,
            "user_id": notif.user_id,
            "type": notif.type.value,
            "actor_id": notif.actor_id,
            "target_type": notif.target_type,
            "target_id": notif.target_id,
            "movie_tmdb_id": notif.movie_tmdb_id,
            "movie_title": notif.movie_title,
            "content_preview": notif.content_preview,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat(),
            "actor": {
                "id": notif.actor.id,
                "username": notif.actor.username,
                "full_name": notif.actor.full_name,
                "email": notif.actor.email
            }
        }
        result.append(notif_dict)

    return result


@router.get("/stats", response_model=NotificationStats)
def get_notification_stats(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Obtener estadísticas de notificaciones"""
    return NotificationService.get_notification_stats(db=db, user_id=current_user.id)


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
        notification_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Marcar notificación como leída"""
    notification = NotificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    return {"message": "Notificación marcada como leída"}


@router.post("/read-all")
def mark_all_as_read(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Marcar todas las notificaciones como leídas"""
    count = NotificationService.mark_all_as_read(db=db, user_id=current_user.id)
    return {"message": f"{count} notificaciones marcadas como leídas"}


@router.delete("/{notification_id}")
def delete_notification(
        notification_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Eliminar notificación"""
    NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    return {"message": "Notificación eliminada"}


# ========== SERVER-SENT EVENTS (SSE) ==========

@router.get("/stream")
async def notification_stream(
        request: Request,
        token: str = Query(..., description="JWT token for authentication"),  # ← Token como query param
        db: Session = Depends(get_db)
):
    """
    Endpoint SSE para notificaciones en tiempo real.

    NOTA: EventSource no soporta headers personalizados, por eso el token
    se envía como query parameter.
    """

    # Validar token manualmente
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    async def event_generator():
        queue = asyncio.Queue()
        NotificationService.add_sse_connection(user.id, queue)

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    notification = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(notification)}\n\n"
                except asyncio.TimeoutError:
                    yield f": heartbeat\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            NotificationService.remove_sse_connection(user.id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )