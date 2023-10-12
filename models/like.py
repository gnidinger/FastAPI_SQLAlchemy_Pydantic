from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Integer, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from config.db import Base


class LikeType(Enum):
    FEED = "feed"
    COMMENT = "comment"


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"), index=True)
    target_id = Column(Integer, index=True)
    like_type = Column(SQLAlchemyEnum(LikeType), index=True)

    user = relationship("User", back_populates="likes")
    feed = relationship("Feed", back_populates="likes")
    comment = relationship("Comment", back_populates="likes")
