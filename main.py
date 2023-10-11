from fastapi import FastAPI
from sqlalchemy import create_engine
from models.user import Base as UserBase  # User의 Base 클래스
from models.feed import Base as FeedBase  # Feed의 Base 클래스
from models.comment import Base as CommentBase  # Comment의 Base
from routers import auth_router, feed_router, comment_router

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

UserBase.metadata.create_all(bind=engine)
FeedBase.metadata.create_all(bind=engine)
CommentBase.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(feed_router.router, prefix="/api/feed", tags=["feed"])
app.include_router(comment_router.router, prefix="/api/comment", tags=["comment"])


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
