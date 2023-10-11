from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.user import User

SECRET_KEY = "ThisIsTheSecretKeyOfFastAPIApplicationWithSQLAlchemyAndPydantic"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter_by(email=email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: User):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email Already Registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password=hashed_password, nickname=user.nickname)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        raise ValueError("Invalid Credentials")
    if not verify_password(password, user.password):
        raise ValueError("Invalid Credentials")
    return user


async def get_current_user_authorization(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid Token")
        return email
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid Token")
