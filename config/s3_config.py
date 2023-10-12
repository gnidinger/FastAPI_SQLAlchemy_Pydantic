import aioboto3
from config import settings


async def get_s3_client():
    return aioboto3.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="ap-northeast-2",
    )
