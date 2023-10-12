from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config import db as config
from models.user import UserCreate, UserLogin, UserResponse
from services import auth_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: AsyncSession = Depends(config.get_db)):
    try:
        db_user = await auth_service.create_user(db, user)
        return {"email": db_user.email, "nickname": db_user.nickname}
    except ValueError:
        raise HTTPException(status_code=400, detail="Email Already Registered")


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(config.get_db)):
    try:
        db_user = await auth_service.authenticate_user(db, user.email, user.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = auth_service.create_access_token({"sub": user.email})  # 이 부분은 비동기가 아님
    return {"email": db_user.email, "nickname": db_user.nickname, "access_token": access_token}
