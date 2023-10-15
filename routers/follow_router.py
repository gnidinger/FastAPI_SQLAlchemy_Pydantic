from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.follow_service import toggle_follow
from models.user import User
from services import auth_service
from config.db import get_db

router = APIRouter()


@router.patch("/{following_id}")
async def toggle_follow_route(
    following_id: int,
    email: str = Depends(auth_service.get_current_user_authorization),
    db: AsyncSession = Depends(get_db),
):
    # 이메일을 이용해 사용자 정보를 가져옴
    result = await db.execute(select(User).filter_by(email=email))
    current_user = result.scalar_one_or_none()

    # 사용자 정보가 없으면 에러 처리
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    current_user_id = current_user.id

    return await toggle_follow(db, current_user_id, following_id)
