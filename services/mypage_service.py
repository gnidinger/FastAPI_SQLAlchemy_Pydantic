from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.user import User
from models.feed import Feed, FeedResponse
from models.comment import Comment, CommentResponse
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

    user_data = user_profile.__dict__
    user_data.pop("password", None)

    return user_data


async def get_user_feeds(
    db: AsyncSession,
    email: str,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "create_dt_desc",
):
    query = select(Feed, User.nickname).join(User, User.email == Feed.author_email)

    condition = User.email == email
    query = query.where(condition)

    if sort_by == "create_dt_desc":
        query = query.order_by(desc(Feed.create_dt))
    elif sort_by == "create_dt_asc":
        query = query.order_by(asc(Feed.create_dt))
    elif sort_by == "update_dt_desc":  # update_dt 내림차순 정렬 조건 추가
        query = query.order_by(desc(Feed.update_dt))
    elif sort_by == "update_dt_asc":  # update_dt 오름차순 정렬 조건 추가
        query = query.order_by(asc(Feed.update_dt))

    total_count_result = await db.execute(select(func.count()).select_from(Feed).where(condition))
    total_count = total_count_result.scalar_one_or_none()
    if total_count is None:
        total_count = 0

    total_count = int(total_count)

    query = query.offset(skip).limit(limit)

    feeds_result = await db.execute(query)
    feeds = feeds_result.all()
    if feeds is None:
        feeds = []

    feed_responses = []

    for feed, nickname in feeds:
        feed_dict = FeedResponse(
            id=feed.id,
            title=feed.title,
            content=feed.content,
            author_email=feed.author_email,
            author_nickname=nickname,
            image_urls=feed.image_urls,
            create_dt=feed.create_dt,
            update_dt=feed.update_dt,
        )
        feed_responses.append(feed_dict.model_dump())

    return total_count, feed_responses


async def get_user_comments(
    db: AsyncSession,
    user_email: str,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "create_dt_desc",
):
    query = select(Comment, User.nickname).join(User, User.email == Comment.author_email)
    condition = User.email == user_email
    query = query.where(condition)

    if sort_by == "create_dt_desc":
        query = query.order_by(desc(Comment.create_dt))
    elif sort_by == "create_dt_asc":
        query = query.order_by(asc(Comment.create_dt))
    elif sort_by == "update_dt_desc":
        query = query.order_by(desc(Comment.update_dt))
    elif sort_by == "update_dt_asc":
        query = query.order_by(asc(Comment.update_dt))

    total_count_result = await db.execute(
        select(func.count()).select_from(Comment).where(condition)
    )
    total_count = total_count_result.scalar_one_or_none()
    if total_count is None:
        total_count = 0

    total_count = int(total_count)

    query = query.offset(skip).limit(limit)

    comments_result = await db.execute(query)
    comments = comments_result.all()
    if comments is None:
        comments = []

    comment_responses = []

    for comment, nickname in comments:
        comment_dict = CommentResponse(
            id=comment.id,
            content=comment.content,
            author_email=comment.author_email,
            author_nickname=nickname,
            feed_id=comment.feed_id,
            create_dt=comment.create_dt,
            update_dt=comment.update_dt,
        )
        comment_responses.append(comment_dict.model_dump())

    return {"total_count": total_count, "comments": comment_responses}


async def get_user_followers(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    # 전체 팔로워 수를 구하는 쿼리
    count_query = (
        select(func.count())
        .select_from(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar_one_or_none()
    if total_count is None:
        total_count = 0

    # 사용자를 팔로우하는 사람들의 목록 가져오기
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    followers = result.scalars().all()

    def extract_profile(user):
        return {
            "email": user.email,
            "nickname": user.nickname,
        }

    return total_count, [extract_profile(user) for user in followers]


async def get_user_followings(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    # 전체 팔로잉 수를 구하는 쿼리
    count_query = (
        select(func.count())
        .select_from(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar_one_or_none()
    if total_count is None:
        total_count = 0

    # 사용자가 팔로우하는 사람들의 목록 가져오기
    query = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    followings = result.scalars().all()

    def extract_profile(user):
        return {
            "email": user.email,
            "nickname": user.nickname,
        }

    return total_count, [extract_profile(user) for user in followings]
