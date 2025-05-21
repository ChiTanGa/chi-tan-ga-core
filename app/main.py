import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api import backup_router
from app.core import setup_logging
from app.core import Settings
from app.startup_tasks import start_mqtt_listener, start_minio_client, exit_mqtt_listener

# Set up own logging (separated from uvicorn)
setup_logging()
logger = logging.getLogger(__name__)  # Use module-level logger

settings = Settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    minio_client = start_minio_client(settings=settings)
    start_mqtt_listener(settings=settings, minio_client=minio_client)
    yield
    exit_mqtt_listener()


app = FastAPI(lifespan=lifespan)

app.include_router(backup_router, prefix="/backup")

# Add other services like this:
# app.include_router(items.router, prefix="/items")
# app.include_router(auth.router, prefix="/auth")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn fast api backend.. ")
    uvicorn.run(app, host="0.0.0.0", port=settings.fast_api_port)
