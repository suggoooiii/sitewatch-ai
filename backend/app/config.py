"""Application configuration using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Hugging Face
    huggingface_api_token: str = ""
    primary_model: str = "facebook/detr-resnet-50"
    secondary_model: str = "facebook/detr-resnet-101"
    ppe_model: str = "ikigaiii/yolos-tiny-ppe-detection"

    # Database
    database_url: str = "sqlite+aiosqlite:///./sitewatch.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Upload directory
    upload_dir: str = "./uploads"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
