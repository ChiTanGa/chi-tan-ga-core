from minio import Minio
import logging
from app.core.config import Settings

logger = logging.getLogger(__name__)  # Use module-level logger

_minio_client = None


def start_minio_client(settings: Settings):
    global _minio_client
    logger.info(f"Connecting to S3 Minio client: {settings.minio_endpoint}...")
    # Lazy init or test connection
    # MinIO client
    _minio_client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False
    )

    # Ensure bucket exists
    if not _minio_client.bucket_exists(settings.minio_bucket):
        _minio_client.make_bucket(settings.minio_bucket)

    logger.info("Successfully connected to S3 Minio client")
