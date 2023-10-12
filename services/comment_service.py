from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.comment import Comment, CommentCreate, CommentUpdate
from models.user import User
from models.feed import Feed
import logging

logging.basicConfig(level=logging.DEBUG)


async def create_comment(db: AsyncSession, comment: CommentCreate, author_email: str):
    comment_dict = comment.model_dump()
    comment_dict["author_email"] = author_email

    result = await db.execute(select(User).where(User.email == author_email))
    author = result.scalar_one_or_none()

    if author is None:
        raise HTTPException(status_code=404, detail="Author Not Found")

    author_nickname = author.nickname

    feed_result = await db.execute(select(Feed).where(Feed.id == comment.feed_id))
    feed = feed_result.scalar_one_or_none()

    if feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    db_comment = Comment(**comment_dict)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    return {
        "id": db_comment.id,
        "content": db_comment.content,
        "author_email": db_comment.author_email,
        "author_nickname": author_nickname,
        "feed_id": db_comment.feed_id,
    }


async def get_comment_by_feed_id(db: AsyncSession, feed_id: int):
    comments = await db.execute(select(Comment).where(Comment.feed_id == feed_id))
    comments = comments.scalars().all()
    comment_responses = []

    for comment in comments:
        result = await db.execute(select(User).where(User.email == comment.author_email))
        author = result.scalar_one_or_none()

        author_nickname = author.nickname

        comment_responses.append(
            {
                "id": comment.id,
                "content": comment.content,
                "author_email": comment.author_email,
                "author_nickname": author_nickname,
                "feed_id": comment.feed_id,
            }
        )

    return comment_responses


async def update_comment(
    db: AsyncSession, comment_id: int, comment_update: CommentUpdate, email: str
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    db_comment = result.scalar_one_or_none()

    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment Not Found")

    if db_comment.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    db_comment.content = comment_update.content or db_comment.content

    await db.commit()
    await db.refresh(db_comment)

    result = await db.execute(select(User).where(User.email == email))
    author = result.scalar_one_or_none()

    if author is None:
        raise HTTPException(status_code=404, detail="Author Not Found")

    author_nickname = author.nickname

    return {
        "id": db_comment.id,
        "content": db_comment.content,
        "author_email": db_comment.author_email,
        "author_nickname": author_nickname,
        "feed_id": db_comment.feed_id,
    }


async def delete_comment(db: AsyncSession, comment_id: int, email: str):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    db_comment = result.scalar_one_or_none()

    logging.debug(f"Selected Comment: {db_comment}")

    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment Not Found")

    if db_comment.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    await db.delete(db_comment)
    logging.debug("Comment deleted, committing...")
    await db.commit()
    logging.debug("Changes committed.")
