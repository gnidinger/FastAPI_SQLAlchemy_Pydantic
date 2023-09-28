from sqlalchemy import Column, String, Integer, ForeignKey
from config.db import Base
from pydantic import BaseModel


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    author_email = Column(String, ForeignKey("users.email"))


class FeedCreate(BaseModel):
    title: str
    content: str


class FeedUpdate(BaseModel):
    title: str
    content: str


class FeedInDB(FeedCreate):
    pass


class FeedResponse(FeedCreate):
    id: int
    author_email: str
    author_nickname: str
