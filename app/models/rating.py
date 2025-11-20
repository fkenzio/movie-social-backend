from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_tmdb_id = Column(Integer, nullable=False, index=True)  # ID de TMDB
    rating = Column(Float, nullable=False)  # 1.0, 1.5, 2.0, 2.5, ..., 5.0
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", backref="ratings")

    # Constraint único: un usuario solo puede calificar una película una vez
    __table_args__ = (
        UniqueConstraint('user_id', 'movie_tmdb_id', name='unique_user_movie_rating'),
    )