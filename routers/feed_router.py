from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.feed import FeedCreate, FeedResponse
from services import feed_service, auth_service
from config.db import get_db
from typing import List

router = APIRouter()


@router.post("/create", response_model=FeedResponse)
def create(
    feed: FeedCreate,
    db: Session = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    feed_dict = feed.model_dump()
    feed_dict["author_email"] = email
    print("************** DB Feed **************", feed_dict)
    return feed_service.create_feed(db, FeedCreate(**feed_dict), email)


@router.get("/list", response_model=List[FeedResponse])
def list_feeds(db: Session = Depends(get_db)):
    return feed_service.get_feeds(db)
