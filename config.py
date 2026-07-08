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

    # Upload settings
    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set[str] = {"xlsx"}

    # AI settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


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
