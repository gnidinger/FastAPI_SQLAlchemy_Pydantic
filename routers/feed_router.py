from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.feed import FeedCreate, FeedResponse, FeedUpdate
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
    db_feed = feed_service.create_feed(db, FeedCreate(**feed_dict), email)

    return {
        "id": db_feed.id,
        "title": db_feed.title,
        "content": db_feed.content,
        "author_email": db_feed.author_email,
        "author_nickname": db_feed.author_nickname,
    }


@router.patch("/update/{feed_id}", response_model=FeedResponse)
def update(
    feed_id: int,
    feed: FeedUpdate,
    db: Session = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    return feed_service.update_feed(db, feed_id, feed, email)


@router.get("/list", response_model=List[FeedResponse])
def list_feeds(db: Session = Depends(get_db)):
    return feed_service.get_feeds(db)


@router.delete("/delete/{feed_id}", response_model=None)
def delete(
    feed_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not Authorized")

    feed_service.delete_feed(db, feed_id, email)
