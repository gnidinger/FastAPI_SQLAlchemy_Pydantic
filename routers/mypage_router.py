from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.feed import FeedListResponse
from config.db import get_db
from services.mypage_service import (
    get_user_profile,
    get_user_feeds,
    get_user_comments,
    get_user_followers,
    get_user_followings,
)
from services.auth_service import get_current_user_authorization

router = APIRouter()


@router.get("/profile")
async def user_profile(
    db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_authorization)
):
    profile = await get_user_profile(db, email)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found.")
    return profile


@router.get("/feeds")
async def user_feeds(
    db: AsyncSession = Depends(get_db),
    email: str = Depends(get_current_user_authorization),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "create_dt_desc",
):
    total_count, feed_responses = await get_user_feeds(db, email, skip, limit, sort_by)
    return FeedListResponse(total_count=total_count, feeds=feed_responses)


@router.get("/comments")
async def user_comments(
    db: AsyncSession = Depends(get_db), email: str = Depends(get_current_user_authorization)
):
    comments = await get_user_comments(db, email)
    return comments


@router.get("/{user_id}/followers")
async def user_followers(user_id: int, db: AsyncSession = Depends(get_db)):
    followers = await get_user_followers(db, user_id)
    return followers


@router.get("/{user_id}/followings")
async def user_followings(user_id: int, db: AsyncSession = Depends(get_db)):
    followings = await get_user_followings(db, user_id)
    return followings
