"""Application configuration for MHES."""

import os


BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = False
    TESTING: bool = False

    # Folder paths
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    EXPORT_FOLDER: str = os.path.join(BASE_DIR, "exports")
    KB_FOLDER: str = os.path.join(BASE_DIR, "kb_knowledge")
    EMBEDDINGS_FOLDER: str = os.path.join(BASE_DIR, "embeddings")
    LOG_FOLDER: str = os.path.join(BASE_DIR, "logs")
    TEMP_DATA_FOLDER: str = os.path.join(BASE_DIR, "temp_data")

    # Upload settings
    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set[str] = {"xlsx"}

    # AI settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_MODEL: str = "qwen2.5:3b" #"llama3.1:latest" #"qwen2.5:3b"
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    # Temp data cleanup (APScheduler)
    TEMP_DATA_RETENTION_DAYS: int = int(os.environ.get("TEMP_DATA_RETENTION_DAYS", "7"))
    TEMP_DATA_CLEANUP_TIMES: list[str] = [
        t.strip()
        for t in os.environ.get("TEMP_DATA_CLEANUP_TIMES", "10:00,16:00").split(",")
        if t.strip()
    ]
    TEMP_DATA_TIMEZONE: str = os.environ.get("TEMP_DATA_TIMEZONE", "Asia/Yangon")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING: bool = True


config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
