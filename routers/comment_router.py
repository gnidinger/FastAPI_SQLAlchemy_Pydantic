from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.comment import CommentCreate, CommentUpdate, CommentResponse
from services import comment_service, auth_service
from config.db import get_db
from typing import List

router = APIRouter()


@router.post("/create", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    return await comment_service.create_comment(db, comment, email)


@router.get("/feed/{feed_id}", response_model=List[CommentResponse])
async def get_comments_by_feed_id(
    feed_id: int,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "create_dt_desc",  # default 정렬 옵션을 작성일 내림차순으로 설정
    db: AsyncSession = Depends(get_db),
):
    comments = await comment_service.get_comment_by_feed_id(db, feed_id, skip, limit, sort_by)
    return comments


@router.patch("/update/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    return await comment_service.update_comment(db, comment_id, comment, email)


@router.delete("/delete/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    email: str = Depends(auth_service.get_current_user_authorization),
):
    await comment_service.delete_comment(db, comment_id, email)
    return {"message": "Comment Deleted"}
