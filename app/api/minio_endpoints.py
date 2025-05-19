import logging
from io import BytesIO
from fastapi import APIRouter
from app.core import settings
from app.startup_tasks import minio_client

logger = logging.getLogger(__name__)  # Use module-level logger

router = APIRouter()


@router.get("/")
def health_check():
    return {"status": "running"}


@router.get("/mqtt-test")
def mqtt_test():
    return {"test": settings.mqtt_host}


@router.get("/minio-test")
def minio_test():
    logger.info(f"Testing minio on {settings.minio_endpoint}")
    test_bytes = BytesIO(b"metadata_bytes1")
    minio_client.put_object(
        settings.minio_bucket,
        "test-path",
        test_bytes,
        length=test_bytes.getbuffer().nbytes,
        content_type="application/json"
    )
    return {"test": "minio-ok"}


@router.get("/minio-test1")
def minio_test():
    logger.info(f"Testing minio on {settings.minio_endpoint}")
    response = minio_client.get_object(
        settings.minio_bucket,
        "test-path",
    )
    return {"test": response.data}
