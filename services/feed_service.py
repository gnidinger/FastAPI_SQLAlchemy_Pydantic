from sqlalchemy.orm import Session
from models.feed import Feed, FeedCreate


def create_feed(db: Session, feed: FeedCreate, author_email: str):
    feed_dict = feed.model_dump()
    feed_dict["author_email"] = author_email
    db_feed = Feed(**feed_dict)
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed


def get_feeds(db: Session):
    return db.query(Feed).all()
