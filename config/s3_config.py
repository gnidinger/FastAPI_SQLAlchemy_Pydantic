import aioboto3
from config import settings


async def get_s3_client():
    session = aioboto3.Session(
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="ap-northeast-2",
    )
    return session.client("s3")
