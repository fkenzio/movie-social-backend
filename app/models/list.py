from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Tabla intermedia para películas en listas
list_movies = Table(
    'list_movies',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('list_id', Integer, ForeignKey('lists.id', ondelete='CASCADE'), nullable=False),
    Column('movie_tmdb_id', Integer, nullable=False),
    Column('added_at', DateTime, server_default=func.now()),
    Column('position', Integer, default=0)
)

# Tabla para colaboradores de listas
list_collaborators = Table(
    'list_collaborators',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('list_id', Integer, ForeignKey('lists.id', ondelete='CASCADE'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('can_edit', Boolean, default=True),
    Column('added_at', DateTime, server_default=func.now())
)


class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    is_collaborative = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", backref="lists")