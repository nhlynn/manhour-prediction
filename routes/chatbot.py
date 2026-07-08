"""Chatbot route blueprint for MHES.

Handles AI-powered semantic search interactions.
"""

from flask import Blueprint, current_app, jsonify, render_template, request

from services.embedding_service import EmbeddingService
from services.search_service import SearchService

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/", methods=["GET"])
def chatbot_page() -> str:
    """Render the chatbot page."""
    return render_template("chatbot.html")


@chatbot_bp.route("/search", methods=["POST"])
def search():
    """Perform semantic search on the knowledge base."""
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Please enter a search query."}), 400

    emb_svc = EmbeddingService(
        model_name=current_app.config["EMBEDDING_MODEL"],
        embeddings_folder=current_app.config["EMBEDDINGS_FOLDER"],
    )
    search_svc = SearchService(embedding_service=emb_svc)

    top_k = data.get("top_k", 10)
    result = search_svc.semantic_search(query, top_k=top_k)

    return jsonify({"query": query, **result})
