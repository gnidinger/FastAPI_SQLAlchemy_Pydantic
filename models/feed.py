from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from config.db import Base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    author_email = Column(String, ForeignKey("users.email"))
    image_urls = Column(JSON, nullable=True)
    create_dt = Column(DateTime(timezone=True), server_default=func.now())
    update_dt = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="feeds")
    comments = relationship("Comment", back_populates="feed", post_update=True)
    likes = relationship("Like", back_populates="feed")


class FeedCreate(BaseModel):
    title: str
    content: str
    image_urls: Optional[List[str]] = []


class FeedUpdate(BaseModel):
    title: str
    content: str
    image_urls: Optional[List[str]] = []


class FeedInDB(FeedCreate):
    create_dt: datetime
    update_dt: datetime


class FeedResponse(FeedCreate):
    id: int
    author_email: str
    author_nickname: str
    image_urls: Optional[List[str]]
    create_dt: datetime
    update_dt: datetime


class FeedListResponse(BaseModel):
    total_count: int
    feeds: List[FeedResponse]
