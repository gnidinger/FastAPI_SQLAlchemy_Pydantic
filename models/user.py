from sqlalchemy import Column, String
from config.db import Base
from pydantic import BaseModel, validator
import re


class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password = Column(String())
    nickname = Column(String())


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
