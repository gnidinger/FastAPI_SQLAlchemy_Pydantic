from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.feed import FeedCreate, FeedResponse, FeedUpdate
from services import feed_service, auth_service
from config.db import get_db
from typing import List
import logging

# logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post("/create", response_model=FeedResponse)
def create(
    title: str = Form(...),
    content: str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    if images:
        image_urls = feed_service.upload_image_to_s3(images)
    else:
        image_urls = []

    feed = FeedCreate(title=title, content=content, image_urls=image_urls)

    return feed_service.create_feed(db, feed, email)


@router.get("/read/{feed_id}", response_model=FeedResponse)
def read_feed(feed_id: int, db: Session = Depends(get_db)):
    return feed_service.get_feed_by_id(db, feed_id)


@router.get("/list", response_model=List[FeedResponse])
def list_feeds(db: Session = Depends(get_db)):
    return feed_service.get_feeds(db)


@router.patch("/update/{feed_id}", response_model=FeedResponse)
def update(
    feed_id: int,
    title: str = Form(...),
    content: str = Form(...),
    new_images: List[UploadFile] = File(None),
    target_image_urls: List[str] = Form(None),
    db: Session = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    feed_update = FeedUpdate(title=title, content=content)
    updated_feed = feed_service.update_feed(
        db, feed_id, feed_update, email, new_images=new_images, target_image_urls=target_image_urls
    )

    return updated_feed


@router.delete("/delete/{feed_id}", response_model=None)
def delete(
    feed_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not Authorized")

    feed_service.delete_feed(db, feed_id, email)
