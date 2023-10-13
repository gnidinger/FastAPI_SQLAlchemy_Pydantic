from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.like import Like
import logging

logging.basicConfig(level=logging.DEBUG)


async def toggle_like(
    db: AsyncSession, user_email: str, feed_id: int = None, comment_id: int = None
):
    # feed_id와 comment_id 둘 다 없거나 둘 다 있을 경우 에러
    if (feed_id is None and comment_id is None) or (feed_id is not None and comment_id is not None):
        raise HTTPException(
            status_code=400, detail="Either feed_id or comment_id must be provided."
        )

    # 이미 좋아요가 있는지 찾기
    query = select(Like).where(
        (Like.user_email == user_email)
        & (Like.feed_id == feed_id)
        & (Like.comment_id == comment_id)
    )
    result = await db.execute(query)
    existing_like = result.scalar_one_or_none()

    # 좋아요가 이미 있다면 삭제, 없다면 추가
    if existing_like:
        await db.delete(existing_like)
    else:
        new_like = Like(user_email=user_email, feed_id=feed_id, comment_id=comment_id)
        db.add(new_like)

    await db.commit()
