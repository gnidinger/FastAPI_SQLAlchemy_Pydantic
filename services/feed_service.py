from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy import desc, asc, func
from models.feed import Feed, FeedCreate, FeedUpdate, FeedResponse, FeedListResponse
from models.user import User
from config import settings
from typing import List, Optional
import uuid
from config.s3_config import get_s3_client
import pytz
import logging

logging.basicConfig(level=logging.NOTSET)


async def create_feed(
    db: AsyncSession, feed: FeedCreate, author_email: str, images: List[UploadFile] = None
):
    feed_dict = feed.model_dump()
    feed_dict["author_email"] = author_email

    korea = pytz.timezone("Asia/Seoul")
    current_time_in_korea = datetime.now(korea)
    feed_dict["create_dt"] = current_time_in_korea
    feed_dict["update_dt"] = current_time_in_korea

    if images:
        image_urls = await upload_image_to_s3(images)
        feed_dict["image_urls"] = image_urls

    author = await db.execute(select(User).where(User.email == author_email))
    author = author.scalar_one_or_none()

    if author is None:
        raise HTTPException(status_code=404, detail="Author Not Found")

    author_nickname = author.nickname

    db_feed = Feed(**feed_dict)
    db.add(db_feed)
    await db.commit()
    await db.refresh(db_feed)

    return {
        "id": db_feed.id,
        "title": db_feed.title,
        "content": db_feed.content,
        "author_email": db_feed.author_email,
        "author_nickname": author_nickname,
        "image_urls": db_feed.image_urls,
        "create_dt": db_feed.create_dt,
        "update_dt": db_feed.update_dt,
    }


async def get_feed_by_id(db: AsyncSession, feed_id: int):
    feed_data = await db.execute(
        select(Feed, User.nickname)
        .join(User, User.email == Feed.author_email)
        .where(Feed.id == feed_id)
    )
    feed_data = feed_data.first()

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
        "create_dt": feed.create_dt,
        "update_dt": feed.update_dt,
    }


async def get_feeds_by_user(
    db: AsyncSession,
    user_id: int = None,
    nickname: str = None,
    email: str = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "create_dt_desc",
):
    if not user_id and not nickname and not email:
        raise HTTPException(
            status_code=400, detail="Either user_id, nickname, or email must be provided"
        )

    query = select(Feed, User.nickname).join(User, User.email == Feed.author_email)

    condition = None
    if user_id:
        condition = User.id == user_id
    elif nickname:
        condition = User.nickname == nickname
    elif email:
        condition = User.email == email

    query = query.where(condition)

    if sort_by == "id_desc":
        query = query.order_by(desc(Feed.id))
    elif sort_by == "id_asc":
        query = query.order_by(asc(Feed.id))
    elif sort_by == "create_dt_desc":
        query = query.order_by(desc(Feed.create_dt))
    elif sort_by == "create_dt_asc":
        query = query.order_by(asc(Feed.create_dt))

    total_count_result = await db.execute(select(func.count()).select_from(Feed).where(condition))
    total_count = total_count_result.scalar_one_or_none()
    if total_count is None:
        total_count = 0

    print(f"total_count type: {type(total_count)} value: {total_count}")

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


async def get_feeds(db: AsyncSession):
    feeds = await db.execute(
        select(Feed, User.nickname).join(User, User.email == Feed.author_email)
    )
    feeds = feeds.all()

    feed_responses = []

    for feed, nickname in feeds:
        feed_dict = {
            "id": feed.id,
            "title": feed.title,
            "content": feed.content,
            "author_email": feed.author_email,
            "author_nickname": nickname,
            "image_urls": feed.image_urls,
            "create_dt": feed.create_dt,
            "update_dt": feed.update_dt,
        }
        feed_responses.append(feed_dict)

    return feed_responses


async def update_feed(
    db: AsyncSession,
    feed_id: int,
    feed_update: FeedUpdate,
    email: str,
    new_images: Optional[List[UploadFile]] = None,
    target_image_urls: Optional[List[str]] = None,
):
    db_feed = await db.execute(select(Feed).where(Feed.id == feed_id))
    db_feed = db_feed.scalar_one_or_none()

    korea = pytz.timezone("Asia/Seoul")
    current_time_in_korea = datetime.now(korea)
    db_feed.update_dt = current_time_in_korea

    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    if db_feed.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    result = await db.execute(select(User).where(User.email == email))
    author = result.scalar_one_or_none()

    author_nickname = author.nickname

    db_feed.title = feed_update.title
    db_feed.content = feed_update.content

    existing_image_urls = db_feed.image_urls or []

    # Case 1: Both new_images and target_image_urls exist
    if new_images and target_image_urls:
        for url in target_image_urls:
            print(url)
            await delete_image_from_s3(url)
        new_image_urls = await upload_image_to_s3(new_images)
        existing_image_urls = [url for url in existing_image_urls if url not in target_image_urls]
        existing_image_urls = existing_image_urls + new_image_urls

    # Case 2: Only new_images exist
    elif new_images:
        new_image_urls = await upload_image_to_s3(new_images)
        existing_image_urls = existing_image_urls + new_image_urls

    # Case 3: Only target_image_urls exist
    elif target_image_urls:
        for url in target_image_urls:
            await delete_image_from_s3(url)
        existing_image_urls = [url for url in existing_image_urls if url not in target_image_urls]

    db_feed.image_urls = existing_image_urls
    print(db_feed.image_urls)

    await db.commit()
    await db.refresh(db_feed)

    result = {
        "id": db_feed.id,
        "title": db_feed.title,
        "content": db_feed.content,
        "author_email": db_feed.author_email,
        "author_nickname": author_nickname,
        "image_urls": db_feed.image_urls,
        "create_dt": db_feed.create_dt,
        "update_dt": db_feed.update_dt,
    }

    logging.debug(f"Updated feed: {result}")

    return result


async def delete_feed(db: AsyncSession, feed_id: int, email: str):
    result = await db.execute(select(Feed).where(Feed.id == feed_id))
    db_feed = result.scalars().first()

    if db_feed is None:
        raise HTTPException(status_code=404, detail="Feed Not Found")

    if db_feed.author_email != email:
        raise HTTPException(status_code=403, detail="Permission Denied")

    image_urls = db_feed.image_urls

    for image_url in image_urls:
        await delete_image_from_s3(image_url)

    await db.delete(db_feed)
    await db.commit()


async def upload_image_to_s3(images: List[UploadFile]):
    image_urls = []

    async with await get_s3_client() as s3_client:
        for image in images:
            logging.debug(f"Uploading {image.filename}")
            image_name = f"{uuid.uuid4()}.png"

            await s3_client.upload_fileobj(
                image.file,
                settings.S3_BUCKET,
                image_name,
                ExtraArgs={"ContentType": image.content_type},
            )

            image_url = f"https://{settings.S3_BUCKET}.s3.ap-northeast-2.amazonaws.com/{image_name}"
            image_urls.append(image_url)

    return image_urls


async def delete_image_from_s3(image_url: str):
    image_name = image_url.split("/")[-1]
    bucket_name = settings.S3_BUCKET
    logging.debug(f"Deleting from Bucket: {bucket_name}, Key: {image_name}")

    async with await get_s3_client() as s3_client:
        await s3_client.delete_object(Bucket=settings.S3_BUCKET, Key=image_name)
