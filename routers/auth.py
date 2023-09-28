from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config import db as config
from models.user import UserCreate, UserLogin, UserResponse
from services import auth_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(config.get_db)):
    try:
        db_user = auth_service.create_user(db, user)
        return {"email": db_user.email, "nickname": db_user.nickname}
    except ValueError:
        raise HTTPException(status_code=400, detail="Email Already Registered")


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(config.get_db)):
    try:
        db_user = auth_service.authenticate_user(db, user.email, user.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = auth_service.create_access_token({"sub": user.email})
    return {"email": db_user.email, "nickname": db_user.nickname, "access_token": access_token}
