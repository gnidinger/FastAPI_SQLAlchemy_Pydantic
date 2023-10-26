from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.user import User
from models.feed import Feed
from models.comment import Comment
from models.follow import Follow
import logging

logging.basicConfig(level=logging.DEBUG)


async def get_user_profile(db: AsyncSession, user_email: str):
    # 사용자 프로필 정보 가져오기
    query = select(User).where(User.email == user_email)
    result = await db.execute(query)
    user_profile = result.scalar_one_or_none()

    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found.")

    return user_profile


async def get_user_feeds(db: AsyncSession, user_email: str):
    # 사용자가 작성한 게시물 목록 가져오기
    query = (
        select(Feed)
        .join(User, User.id == Feed.author_id)
        .where(User.email == user_email)
        .order_by(Feed.id.desc())
    )
    result = await db.execute(query)
    user_feeds = result.scalars().all()

    return user_feeds


async def get_user_comments(db: AsyncSession, user_email: str):
    # 사용자가 작성한 코멘트 목록을 가져오기
    query = (
        select(Comment)
        .join(User, User.email == Comment.author_email)
        .where(User.email == user_email)
        .order_by(Comment.id.desc())  # 최신 코멘트부터 표시
    )
    result = await db.execute(query)
    user_comments = result.scalars().all()

    return user_comments


async def get_user_followers(db: AsyncSession, user_id: int):
    # 사용자를 팔로우하는 사람들의 목록 가져오기
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    result = await db.execute(query)
    followers = result.scalars().all()

    return [user.email for user in followers]


async def get_user_followings(db: AsyncSession, user_id: int):
    # 사용자가 팔로우하는 사람들의 목록 가져오기
    query = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    result = await db.execute(query)
    followings = result.scalars().all()

    return [user.email for user in followings]
