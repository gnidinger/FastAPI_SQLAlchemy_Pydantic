from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from config.db import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"), index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), index=True, nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), index=True, nullable=True)

    user = relationship("User", back_populates="likes")
    feed = relationship("Feed", back_populates="likes")
    comment = relationship("Comment", back_populates="likes")
