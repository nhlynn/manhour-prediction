"""Preview route blueprint for MHES.

Handles knowledge base data preview and browsing.
"""

from flask import Blueprint, render_template

preview_bp = Blueprint("preview", __name__)


@preview_bp.route("/", methods=["GET"])
def preview_page() -> str:
    """Render the preview page.

    Returns:
        Rendered preview template.
    """
    return render_template("preview.html")


# TODO: Add route for paginated data preview
# TODO: Add route for file-specific preview
# TODO: Add route for search/filter within preview
