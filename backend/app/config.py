"""Application configuration settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings

from app.constants import ParserType, OCRBackend


class Settings(BaseSettings):
    """Application settings loaded from environment variables with defaults."""

    # Application settings
    APP_NAME: str = "Smart Resume Form Populator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # File settings
    MAX_FILE_SIZE_MB: int = 10
    MAX_PAGES: int = 5
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # Parser settings
    DEFAULT_PARSER: ParserType = ParserType.TEXT
    DEFAULT_OCR_BACKEND: OCRBackend = OCRBackend.TESSERACT

    # Extraction settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.5

    # LLM extraction settings (Ollama)
    LLM_MODEL_NAME: str = "gemma3:4b"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_TIMEOUT: int = 30
    LLM_TEMPERATURE: float = 0.1

    # Logging settings
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings from environment variables.
    Cached for performance.
    """
    return Settings()
