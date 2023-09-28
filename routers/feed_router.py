from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.feed import FeedCreate, FeedResponse
from services import feed_service
from config.db import get_db
from typing import List

router = APIRouter()


@router.post("/create", response_model=FeedResponse)
def create(feed: FeedCreate, db: Session = Depends(get_db)):
    return feed_service.create_feed(db, feed)


@router.get("/list", response_model=List[FeedResponse])
def list_feeds(db: Session = Depends(get_db)):
    return feed_service.get_feeds(db)
