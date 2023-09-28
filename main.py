from fastapi import FastAPI
from sqlalchemy import create_engine
from models.user import Base
from routers import auth as auth_router

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
