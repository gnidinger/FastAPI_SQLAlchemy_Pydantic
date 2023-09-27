from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, validator
import re

Base = declarative_base()


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
