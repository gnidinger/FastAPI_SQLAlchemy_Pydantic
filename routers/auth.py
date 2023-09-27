from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..config import db as config
from ..models.user import UserCreate
from ..services import auth_service

router = APIRouter()

@router.post("/signup", response_model=UserCreate)
def signup(user: UserCreate, db: Session = Depends(config.get_db)):
    try:
        return auth_service.create_user(db, user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Email Already Registered")
    
@router.post("/login")
def login(user: UserCreate, db: Session = Depends(config.get_db)):
    db_user = auth_service.authenticate_user(db, user.email, user.password)
    if db_user if False:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {"accept_token": auth_service.create_access_token({"sub": user.email})}