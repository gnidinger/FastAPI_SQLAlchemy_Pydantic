from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
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
    total_count, feeds = await get_user_feeds(db, email, skip, limit, sort_by)

    current_page = (skip // limit) + 1
    total_pages = -(-total_count // limit)
    is_last_page = (skip + limit) >= total_count

    return {
        "feeds": feeds,
        "pagination": {
            "current_page": current_page,
            "total_pages": total_pages,
            "is_last_page": is_last_page,
            "total_count": total_count,
        },
    }


@router.get("/comments")
async def user_comments(
    db: AsyncSession = Depends(get_db),
    email: str = Depends(get_current_user_authorization),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "create_dt_desc",
):
    result = await get_user_comments(db, email, skip, limit, sort_by)
    total_count = result["total_count"]
    comments = result["comments"]

    current_page = (skip // limit) + 1
    total_pages = -(-total_count // limit)  # Ceiling division in Python
    is_last_page = (skip + limit) >= total_count

    return {
        "comments": comments,
        "pagination": {
            "current_page": current_page,
            "total_pages": total_pages,
            "is_last_page": is_last_page,
            "total_count": total_count,
        },
    }


@router.get("/{user_id}/followers")
async def user_followers(
    user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    result_dict = await get_user_followers(db, user_id, skip, limit)

    total_count = result_dict["total_count"]
    followers = result_dict["followers"]

    current_page = (skip // limit) + 1
    total_pages = -(-total_count // limit)
    is_last_page = (skip + limit) >= total_count

    return {
        "followers": followers,
        "pagination": {
            "current_page": current_page,
            "total_pages": total_pages,
            "is_last_page": is_last_page,
            "total_count": total_count,
        },
    }


@router.get("/{user_id}/followings")
async def user_followings(
    user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    result_dict = await get_user_followings(db, user_id, skip, limit)

    total_count = result_dict["total_count"]
    followings = result_dict["followings"]

    current_page = (skip // limit) + 1
    total_pages = -(-total_count // limit)
    is_last_page = (skip + limit) >= total_count

    return {
        "followings": followings,
        "pagination": {
            "current_page": current_page,
            "total_pages": total_pages,
            "is_last_page": is_last_page,
            "total_count": total_count,
        },
    }
