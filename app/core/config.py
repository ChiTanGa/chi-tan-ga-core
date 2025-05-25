import os
import sys
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)  # Use module-level logger


def _verify_env_file(_env_file: str):

    # Check if env file exists
    if not os.path.exists(_env_file):
        logger.error(f"ERROR: Environment file '{_env_file}' not found.\n")
        sys.exit(1)
    return _env_file


class Settings(BaseSettings):
    # .env.docker-compose file
    fast_api_port: int
    mqtt_port: int
    mqtt_host: str
    mqtt_topic_root: str
    minio_port: int
    minio_host: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    timescale_host: str
    postgres_password: str

    @property
    def minio_endpoint(self) -> str:
        return f"{self.minio_host}:{self.minio_port}"

    _app_env_file = _verify_env_file(os.getenv("APP_ENV_FILE", ".env"))
    model_config = SettingsConfigDict(env_file=_app_env_file)  # default fallback

    @classmethod
    def from_env_file(cls, env_file: str) -> "Settings":
        verified = _verify_env_file(env_file)

        class ConfiguredSettings(cls):
            model_config = SettingsConfigDict(env_file=verified)

        return ConfiguredSettings()
