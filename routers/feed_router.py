from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from models.feed import FeedCreate, FeedResponse, FeedUpdate, FeedListResponse
from services import feed_service, auth_service
from config.db import get_db
from typing import List
import logging

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post("/create", response_model=FeedResponse)
async def create(
    title: str = Form(...),
    content: str = Form(...),
    images: List[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    feed = FeedCreate(title=title, content=content)

    return await feed_service.create_feed(db, feed, email, images)


@router.get("/read/{feed_id}", response_model=FeedResponse)
async def read_feed(feed_id: int, db: AsyncSession = Depends(get_db)):
    return await feed_service.get_feed_by_id(db, feed_id)


@router.get("/list-by-user", response_model=FeedListResponse)
async def list_feeds_by_user(
    user_id: int = None,
    nickname: str = None,
    email: str = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id_desc",  # 정렬 옵션 추가
    db: AsyncSession = Depends(get_db),
):
    total_count, feed_responses = await feed_service.get_feeds_by_user(
        db, user_id=user_id, nickname=nickname, email=email, skip=skip, limit=limit, sort_by=sort_by
    )
    return FeedListResponse(total_count=total_count, feeds=feed_responses)


@router.get("/list", response_model=List[FeedResponse])
async def list_feeds(db: AsyncSession = Depends(get_db)):
    return await feed_service.get_feeds(db)


@router.patch("/update/{feed_id}", response_model=FeedResponse)
async def update(
    feed_id: int,
    title: str = Form(...),
    content: str = Form(...),
    new_images: List[UploadFile] = File(None),
    target_image_urls: List[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    feed_update = FeedUpdate(title=title, content=content)
    updated_feed = await feed_service.update_feed(
        db, feed_id, feed_update, email, new_images=new_images, target_image_urls=target_image_urls
    )

    return updated_feed


@router.delete("/delete/{feed_id}", response_model=None)
async def delete(
    feed_id: int,
    db: AsyncSession = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    if email is None:
        raise HTTPException(status_code=401, detail="Not Authorized")

    await feed_service.delete_feed(db, feed_id, email)
    return {"message": "Feed Deleted"}
