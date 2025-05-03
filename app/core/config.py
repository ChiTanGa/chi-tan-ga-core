import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = os.getenv("APP_ENV_FILE", ".env")  # fallback to .env


class Settings(BaseSettings):
    # .env file
    fast_api_port: int
    mqtt_port: int
    mqtt_host: str
    mqtt_port: int
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    timescale_host: str
    postgres_password: str

    model_config = SettingsConfigDict(env_file=env_file)


settings = Settings()
