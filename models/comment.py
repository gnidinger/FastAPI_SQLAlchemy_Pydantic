from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base
from pydantic import BaseModel
from typing import Optional


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    author_email = Column(String, ForeignKey("users.email"))
    feed_id = Column(Integer, ForeignKey("feeds.id"))

    author = relationship("User", back_populates="comments")
    feed = relationship("Feed", back_populates="comments")
    likes = relationship("Like", back_populates="comment")


class CommentCreate(BaseModel):
    content: str
    feed_id: int


class CommentUpdate(BaseModel):
    content: Optional[str]


class CommentInDB(CommentCreate):
    pass


class CommentResponse(CommentCreate):
    id: int
    author_email: str
    author_nickname: str
