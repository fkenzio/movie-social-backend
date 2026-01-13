from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    LIKE = "like"  # Like en rating/review/list/comment
    COMMENT = "comment"  # Comentario en rating/review/list
    REPLY = "reply"  # Respuesta a tu comentario


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)

    # Usuario que generó la notificación (quien hizo la acción)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Target (objeto sobre el que se hizo la acción)
    target_type = Column(String(50), nullable=True)  # rating, review, list, comment, movie
    target_id = Column(Integer, nullable=True)

    # Metadata adicional (JSON como texto)
    movie_tmdb_id = Column(Integer, nullable=True)
    movie_title = Column(String(255), nullable=True)
    content_preview = Column(Text, nullable=True)  # Preview del comentario/review

    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relaciones
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    actor = relationship("User", foreign_keys=[actor_id])

    def __repr__(self):
        return f"<Notification {self.id} - {self.type} for user {self.user_id}>"