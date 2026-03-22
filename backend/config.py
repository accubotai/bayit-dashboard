"""Application configuration via environment variables."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings

# Richmond BC bounding box — all API bbox queries must fall within these bounds
RICHMOND_BOUNDS = {
    "min_lng": -123.30,
    "max_lng": -122.90,
    "min_lat": 49.10,
    "max_lat": 49.30,
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://user:password@localhost:5432/richmond_land"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"
    mapbox_access_token: str = ""

    # Supabase connection (used in production)
    supabase_db_host: str = ""
    supabase_db_port: int = 6543
    supabase_db_name: str = "postgres"
    supabase_db_user: str = ""
    supabase_db_password: str = ""
    supabase_direct_url: str = ""

    # Auth
    dashboard_password_hash: str = ""
    dashboard_user: str = "bayit"
    token_secret: str = ""

    # Vercel (injected by platform, not used in app code)
    vercel_token: str = ""
    vercel_org_id: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def db_url(self) -> str:
        """Return the appropriate database URL."""
        if self.supabase_db_host:
            return (
                f"postgresql://{self.supabase_db_user}:{self.supabase_db_password}"
                f"@{self.supabase_db_host}:{self.supabase_db_port}/{self.supabase_db_name}"
            )
        return self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @field_validator("environment", "cors_origins", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Strip whitespace/newlines from env var values."""
        return v.strip() if isinstance(v, str) else v


def validate_bbox(min_lng: float, min_lat: float, max_lng: float, max_lat: float) -> None:
    """Validate that a bounding box falls within Richmond bounds.

    Raises ValueError if out of bounds.
    """
    bounds = RICHMOND_BOUNDS
    if (
        min_lng < bounds["min_lng"]
        or max_lng > bounds["max_lng"]
        or min_lat < bounds["min_lat"]
        or max_lat > bounds["max_lat"]
    ):
        msg = (
            f"Bounding box ({min_lng},{min_lat},{max_lng},{max_lat}) "
            f"outside Richmond bounds: lng [{bounds['min_lng']}, {bounds['max_lng']}], "
            f"lat [{bounds['min_lat']}, {bounds['max_lat']}]"
        )
        raise ValueError(msg)

    if min_lng >= max_lng or min_lat >= max_lat:
        msg = "Invalid bbox: min must be less than max"
        raise ValueError(msg)


settings = Settings()
