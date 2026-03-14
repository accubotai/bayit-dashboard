"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    database_url: str  # Required — must be set via .env or environment
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    mapbox_access_token: str  # Required — must be set via .env or environment

    # Richmond bounding box for input validation
    richmond_min_lng: float = -123.30
    richmond_max_lng: float = -123.00
    richmond_min_lat: float = 49.10
    richmond_max_lat: float = 49.22

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
