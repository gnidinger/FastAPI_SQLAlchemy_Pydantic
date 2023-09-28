from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.feed import Feed, FeedCreate, FeedUpdate
from models.user import User


def create_feed(db: Session, feed: FeedCreate, author_email: str):
    feed_dict = feed.model_dump()
    feed_dict["author_email"] = author_email

    db_feed = Feed(**feed_dict)

    author = db.query(User).filter(User.email == author_email).first()
    author_nickname = author.nickname

    db_feed.author_nickname = author_nickname
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed


def update_feed(db: Session, feed_id: int, feed_update: FeedUpdate, email: str):
    db_feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    if db_feed.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    author = db.query(User).filter(User.email == email).first()
    author_nickname = author.nickname

    db_feed.title = feed_update.title
    db_feed.content = feed_update.content
    db_feed.author_nickname = author_nickname

    db.commit()
    db.refresh(db_feed)

    return db_feed


def get_feeds(db: Session):
    return db.query(Feed).all()


def delete_feed(db: Session, feed_id: int, email: str):
    db_feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    if db_feed.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    db.delete(db_feed)
    db.commit()
