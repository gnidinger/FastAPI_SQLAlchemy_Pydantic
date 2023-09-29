from fastapi import FastAPI
from sqlalchemy import create_engine
from models.user import Base as UserBase  # User의 Base 클래스
from models.feed import Base as FeedBase  # Feed의 Base 클래스
from routers import auth_router
from routers import feed_router
import boto3
from config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name="ap-northeast-2",
)

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

UserBase.metadata.create_all(bind=engine)
FeedBase.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(feed_router.router, prefix="/api/feed", tags=["feed"])


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
