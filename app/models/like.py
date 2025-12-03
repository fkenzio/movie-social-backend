from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_type = Column(String(50), nullable=False)  # 'rating', 'review', 'list', 'comment'
    target_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="likes")

    __table_args__ = (
        UniqueConstraint('user_id', 'target_type', 'target_id', name='unique_user_like'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )