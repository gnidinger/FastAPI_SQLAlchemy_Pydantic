from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import join
from models.feed import Feed, FeedCreate, FeedUpdate
from models.user import User
from config import settings
from typing import List, Optional
import uuid
from config.s3_config import s3_client
import logging

logging.basicConfig(level=logging.NOTSET)


async def create_feed(
    db: Session, feed: FeedCreate, author_email: str, images: List[UploadFile] = None
):
    feed_dict = feed.model_dump()
    feed_dict["author_email"] = author_email

    if images:
        image_urls = upload_image_to_s3(images)
        feed_dict["image_urls"] = image_urls

    author = db.query(User).filter(User.email == author_email).first()
    if author is None:
        raise HTTPException(status_code=404, detail="Author Not Found")

    author_nickname = author.nickname

    db_feed = Feed(**feed_dict)
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    return {
        "id": db_feed.id,
        "title": db_feed.title,
        "content": db_feed.content,
        "author_email": db_feed.author_email,
        "author_nickname": author_nickname,
        "image_urls": db_feed.image_urls,
    }


async def get_feed_by_id(db: Session, feed_id: int):
    feed_data = (
        db.query(Feed, User.nickname)
        .join(User, User.email == Feed.author_email)
        .filter(Feed.id == feed_id)
        .first()
    )

    if feed_data is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    feed, nickname = feed_data

    return {
        "id": feed.id,
        "title": feed.title,
        "content": feed.content,
        "author_email": feed.author_email,
        "author_nickname": nickname,
        "image_urls": feed.image_urls,
    }


async def get_feeds(db: Session):
    feeds = db.query(Feed, User.nickname).join(User, User.email == Feed.author_email).all()
    feed_responses = []

    for feed, nickname in feeds:
        feed_dict = {
            "id": feed.id,
            "title": feed.title,
            "content": feed.content,
            "author_email": feed.author_email,
            "author_nickname": nickname,
            "image_urls": feed.image_urls,
        }
        feed_responses.append(feed_dict)

    return feed_responses


async def update_feed(
    db: Session,
    feed_id: int,
    feed_update: FeedUpdate,
    email: str,
    new_images: Optional[List[UploadFile]] = None,
    target_image_urls: Optional[List[str]] = None,
):
    db_feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    if db_feed.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    author = db.query(User).filter(User.email == email).first()
    author_nickname = author.nickname

    db_feed.title = feed_update.title
    db_feed.content = feed_update.content

    existing_image_urls = db_feed.image_urls or []

    # Case 1: Both new_images and target_image_urls exist
    if new_images and target_image_urls:
        for url in target_image_urls:
            print(url)
            delete_image_from_s3(url)
        new_image_urls = upload_image_to_s3(new_images)
        existing_image_urls = [url for url in existing_image_urls if url not in target_image_urls]
        existing_image_urls = existing_image_urls + new_image_urls

    # Case 2: Only new_images exist
    elif new_images:
        new_image_urls = upload_image_to_s3(new_images)
        existing_image_urls = existing_image_urls + new_image_urls

    # Case 3: Only target_image_urls exist
    elif target_image_urls:
        for url in target_image_urls:
            delete_image_from_s3(url)
        existing_image_urls = [url for url in existing_image_urls if url not in target_image_urls]

    db_feed.image_urls = existing_image_urls
    print(db_feed.image_urls)

    db.commit()
    db.refresh(db_feed)

    result = {
        "id": db_feed.id,
        "title": db_feed.title,
        "content": db_feed.content,
        "author_email": db_feed.author_email,
        "author_nickname": author_nickname,
        "image_urls": db_feed.image_urls,
    }

    logging.debug(f"Updated feed: {result}")

    return result


async def delete_feed(db: Session, feed_id: int, email: str):
    db_feed = db.query(Feed).filter(Feed.id == feed_id).first()

    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    if db_feed.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    image_urls = db_feed.image_urls

    for image_url in image_urls:
        delete_image_from_s3(image_url)

    db.delete(db_feed)
    db.commit()


def upload_image_to_s3(images: List[UploadFile]):
    image_urls = []
    for image in images:
        logging.debug(f"Uploading {image.filename}")
        image_name = f"{uuid.uuid4()}.png"
        s3_client.upload_fileobj(
            image.file,
            settings.S3_BUCKET,
            image_name,
            ExtraArgs={"ContentType": image.content_type},
        )
        image_url = f"https://{settings.S3_BUCKET}.s3.ap-northeast-2.amazonaws.com/{image_name}"
        image_urls.append(image_url)

    return image_urls


def delete_image_from_s3(image_url: str):
    image_name = image_url.split("/")[-1]
    bucket_name = settings.S3_BUCKET

    logging.debug(f"Deleting from Bucket: {bucket_name}, Key: {image_name}")

    s3_client.delete_object(Bucket=settings.S3_BUCKET, Key=image_name)
