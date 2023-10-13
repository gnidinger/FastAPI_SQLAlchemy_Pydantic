from fastapi import FastAPI
from sqlalchemy import create_engine
from models.user import Base as UserBase  # User의 Base 클래스
from models.feed import Base as FeedBase  # Feed의 Base 클래스
from models.comment import Base as CommentBase  # Comment의 Base
from models.like import Base as LikeBase  # Like의 Base 클래스
from models.follow import Base as FollowBase  # Follow의 Base 클래스
from routers import auth_router, feed_router, comment_router, like_router, follow_router
from config.cors_config import setup_cors

DATABASE_URL = "postgresql://postgres:rjslrjsl333@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)

UserBase.metadata.create_all(bind=engine)
FeedBase.metadata.create_all(bind=engine)
CommentBase.metadata.create_all(bind=engine)
LikeBase.metadata.create_all(bind=engine)
FollowBase.metadata.create_all(bind=engine)

app = FastAPI()

setup_cors(app)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(feed_router.router, prefix="/api/feed", tags=["feed"])
app.include_router(comment_router.router, prefix="/api/comment", tags=["comment"])
app.include_router(like_router.router, prefix="/api/like", tags=["like"])
app.include_router(follow_router.router, prefix="/api/follow", tags=["follow"])


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
