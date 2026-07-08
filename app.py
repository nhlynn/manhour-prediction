"""MHES - Man Hour Estimation System.

Flask application entry point.
"""

import os
import logging
from flask import Flask, render_template

from config import Config, config_by_name
from utils.logger import setup_logging


def create_app(config_name: str = "development") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration environment name.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, Config))

    # Ensure required folders exist
    _ensure_folders(app)

    # Setup logging
    setup_logging(app.config.get("LOG_FOLDER", "logs"))

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Inject missing-embeddings count into all templates
    @app.context_processor
    def inject_missing_embeddings() -> dict:
        from services.excel_service import ExcelService
        from services.embedding_service import EmbeddingService

        try:
            excel_svc = ExcelService(kb_folder=app.config["KB_FOLDER"])
            emb_svc = EmbeddingService(
                model_name=app.config["EMBEDDING_MODEL"],
                embeddings_folder=app.config["EMBEDDINGS_FOLDER"],
            )
            kb_files = excel_svc.list_knowledge_files()
            count = sum(
                1 for f in kb_files if not emb_svc.has_index(f["filename"])
            )
        except Exception:
            count = 0
        return {"missing_embeddings_count": count}

    # Register dashboard route
    @app.route("/dashboard")
    def dashboard() -> str:
        """Render the dashboard page."""
        from services.excel_service import ExcelService
        from services.embedding_service import EmbeddingService

        excel_svc = ExcelService(kb_folder=app.config["KB_FOLDER"])
        emb_svc = EmbeddingService(
            model_name=app.config["EMBEDDING_MODEL"],
            embeddings_folder=app.config["EMBEDDINGS_FOLDER"],
        )
        kb_files = excel_svc.list_knowledge_files()
        kb_count = len(kb_files)
        embedded_count = sum(
            1 for f in kb_files if emb_svc.has_index(f["filename"])
        )
        return render_template(
            "dashboard.html",
            kb_count=kb_count,
            embedded_count=embedded_count,
        )

    # Default route — show chatbot
    @app.route("/")
    def index() -> str:
        """Render the chatbot page as the default landing page."""
        return render_template("chatbot.html")

    app.logger.info("MHES application initialized successfully.")
    return app


def _ensure_folders(app: Flask) -> None:
    """Create required folders if they do not exist.

    Args:
        app: Flask application instance.
    """
    folders = [
        app.config.get("UPLOAD_FOLDER", "uploads"),
        app.config.get("EXPORT_FOLDER", "exports"),
        app.config.get("KB_FOLDER", "kb_knowledge"),
        app.config.get("EMBEDDINGS_FOLDER", "embeddings"),
        app.config.get("LOG_FOLDER", "logs"),
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def _register_blueprints(app: Flask) -> None:
    """Register all Flask blueprints.

    Args:
        app: Flask application instance.
    """
    from routes.upload import upload_bp
    from routes.chatbot import chatbot_bp
    from routes.preview import preview_bp
    from routes.export import export_bp

    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    app.register_blueprint(preview_bp, url_prefix="/preview")
    app.register_blueprint(export_bp, url_prefix="/export")


def _register_error_handlers(app: Flask) -> None:
    """Register error handlers for common HTTP errors.

    Args:
        app: Flask application instance.
    """

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[str, int]:
        """Handle 404 errors."""
        app.logger.warning(f"Page not found: {error}")
        return render_template("base.html", error="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[str, int]:
        """Handle 500 errors."""
        app.logger.error(f"Internal server error: {error}")
        return render_template("base.html", error="Internal server error"), 500


if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "development")
    application = create_app(env)
    application.run(host="0.0.0.0", port=5000, debug=(env == "development"))
