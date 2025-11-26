from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_tmdb_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    contains_spoilers = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", backref="reviews")

    # Índice compuesto para búsquedas rápidas
    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )