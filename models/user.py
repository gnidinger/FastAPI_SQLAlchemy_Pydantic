from sqlalchemy import Column, String, Integer, Sequence
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

    feeds = relationship("Feed", back_populates="author")
    comments = relationship("Comment", back_populates="author", post_update=True)
    likes = relationship("Like", back_populates="user")


class UserCreate(BaseModel):
    email: str
    password: str
    nickname: str


class UserInDB(UserCreate):
    pass


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
