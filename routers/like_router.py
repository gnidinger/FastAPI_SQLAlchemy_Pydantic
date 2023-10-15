from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_db
from services import auth_service
from services.like_service import toggle_like

router = APIRouter()


@router.patch("/")
async def toggle(
    user_email: str = Depends(auth_service.get_current_user_authorization),
    feed_id: int = None,
    comment_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        await toggle_like(db, user_email, feed_id=feed_id, comment_id=comment_id)
    except HTTPException as e:
        raise e

    return {"message": "Like toggled successfully"}
