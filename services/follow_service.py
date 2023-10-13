from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.follow import Follow
from services import auth_service
from fastapi import HTTPException


async def toggle_follow(db: AsyncSession, follower_id: int, following_id: int):
    if follower_id == following_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    following = await auth_service.get_user_by_id(db, following_id)

    if not following:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    existing_follow = result.scalar_one_or_none()

    if existing_follow:
        await db.delete(existing_follow)
        action = "unfollowed"
    else:
        new_follow = Follow(follower_id=follower_id, following_id=following_id)
        db.add(new_follow)
        action = "followed"

    await db.commit()
    return {"action": action}
