from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from config.db import Base


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    # 두 필드의 조합이 고유해야 함
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="unique_follow"),)
