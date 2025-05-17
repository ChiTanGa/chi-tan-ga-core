import os
import sys
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)  # Use module-level logger
env_file = os.getenv("APP_ENV_FILE", ".env")  # fallback to .env

# Check if env file exists
if not os.path.exists(env_file):
    logger.error(f"ERROR: Environment file '{env_file}' not found.\n")
    sys.exit(1)


class Settings(BaseSettings):
    # .env file
    fast_api_port: int
    mqtt_port: int
    mqtt_host: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    timescale_host: str
    postgres_password: str

    model_config = SettingsConfigDict(env_file=env_file)


settings = Settings()
