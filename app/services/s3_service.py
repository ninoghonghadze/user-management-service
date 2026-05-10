import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logger import logger


async def upload_image_to_s3(
    file_bytes: bytes, filename: str, content_type: str
) -> str:
    # upload file to S3 and return the storage path
    try:
        session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )

        async with session.client("s3") as s3:
            key = f"users/avatars/{filename}"
            await s3.put_object(
                Bucket=settings.aws_bucket_name,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
            logger.info(f"Successfully uploaded {filename} to S3")
            return key
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise
