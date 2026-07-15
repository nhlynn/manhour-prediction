"""Preview route blueprint for MHES.

Handles knowledge base data preview and browsing.
"""

from flask import Blueprint, current_app, jsonify, render_template, request

from scheduler.temp_data_service import TempDataService
from services.remark_html import sanitize_remark_html

preview_bp = Blueprint("preview", __name__)


def _temp_data_service() -> TempDataService:
    return TempDataService(db_path=current_app.config["MHES_DB_PATH"])


@preview_bp.route("/", methods=["GET"])
def preview_page() -> str:
    """Render the preview page.

    Returns:
        Rendered preview template.
    """
    return render_template("preview.html")


@preview_bp.route("/temp", methods=["GET"])
def temp_data_page() -> str:
    """Render the temporary data page.

    Shows Preview data that was stashed on the server when the user
    navigated to the AI Chatbot from the nav menu while Preview had data.

    Returns:
        Rendered temporary data template.
    """
    return render_template("temp_data.html")


@preview_bp.route("/temp/stashes", methods=["GET"])
def list_stashes():
    """Return all stashed Preview snapshots as JSON."""
    return jsonify(_temp_data_service().list_stashes())


@preview_bp.route("/temp/stashes", methods=["POST"])
def create_stash():
    """Stash a Preview snapshot on the server.

    Body: {"categories": [...], "totals": {...}, "projectName": "...",
    "createdBy": "...", "projectRemark": "..."}
    """
    data = request.get_json(silent=True) or {}
    categories = data.get("categories") or []

    if not categories:
        return jsonify({"error": "No categories to stash."}), 400

    stash = _temp_data_service().add_stash(
        categories=categories,
        totals=data.get("totals") or {},
        project_name=data.get("projectName") or "",
        created_by=data.get("createdBy") or "",
        project_remark=sanitize_remark_html(data.get("projectRemark") or ""),
    )
    return jsonify(stash), 201


@preview_bp.route("/temp/stashes/<stash_id>", methods=["DELETE"])
def delete_stash(stash_id: str):
    """Remove a single stash by id."""
    removed = _temp_data_service().remove_stash(stash_id)
    if not removed:
        return jsonify({"error": "Stash not found."}), 404
    return jsonify({"ok": True})


# TODO: Add route for paginated data preview
# TODO: Add route for file-specific preview
# TODO: Add route for search/filter within preview
