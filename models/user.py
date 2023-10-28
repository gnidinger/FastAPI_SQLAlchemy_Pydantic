from sqlalchemy import Column, String, Integer, DateTime, func
from datetime import datetime
from sqlalchemy.orm import relationship
from config.db import Base
from pydantic import BaseModel, validator
import re


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String())
    nickname = Column(String())
    create_dt = Column(DateTime(timezone=True), server_default=func.now())

    feeds = relationship("Feed", back_populates="author")
    comments = relationship("Comment", back_populates="author", post_update=True)
    likes = relationship("Like", back_populates="user")


class UserCreate(BaseModel):
    email: str
    password: str
    nickname: str


class UserInDB(UserCreate):
    createDt: datetime


class UserLogin(BaseModel):
    email: str
    password: str

    @validator("email")
    def validate_email(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid Email Format")
        return value


class UserResponse(BaseModel):
    email: str
    nickname: str
    create_dt: datetime
