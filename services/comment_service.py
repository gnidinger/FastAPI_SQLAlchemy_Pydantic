from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.comment import Comment, CommentCreate, CommentUpdate
from models.user import User
from models.feed import Feed
import logging

logging.basicConfig(level=logging.DEBUG)


def create_comment(db: Session, comment: CommentCreate, author_email: str):
    comment_dict = comment.model_dump()
    comment_dict["author_email"] = author_email

    author = db.query(User).filter(User.email == author_email).first()
    if author is None:
        raise HTTPException(status_code=404, detail="Author Not Found")

    author_nickname = author.nickname

    feed = db.query(Feed).filter(Feed.id == comment.feed_id).first()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    db_comment = Comment(**comment_dict)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return {
        "id": db_comment.id,
        "content": db_comment.content,
        "author_email": db_comment.author_email,
        "author_nickname": author_nickname,
        "feed_id": db_comment.feed_id,
    }


def get_comment_by_feed_id(db: Session, feed_id: int):
    comments = db.query(Comment).filter(Comment.feed_id == feed_id).all()
    return comments


def update_comment(db: Session, comment_id: int, comment_update: CommentUpdate, email: str):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment Not Found")

    if db_comment.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    db_comment.content = comment_update.content or db_comment.content

    db.commit()
    db.refresh(db_comment)

    return db_comment


def delete_comment(db: Session, comment_id: int, email: str):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment Not Found")

    if db_comment.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    db.delete(db_comment)
    db.commit()
