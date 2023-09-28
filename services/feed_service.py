from sqlalchemy.orm import Session
from models.feed import Feed, FeedCreate


def create_feed(db: Session, feed: FeedCreate):  # FeedCreate 사용
    feed_data = feed.dict()
    db_feed = Feed(**feed_data, author_email=feed_data.get("email"))
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed


def get_feeds(db: Session):
    return db.query(Feed).all()
