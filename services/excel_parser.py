"""Excel-to-nested-JSON converter for man-hour knowledge files.

Parses hierarchical Excel files with the structure:
    Category | Task List | Activity Details | Estimate (Hours) | Buffer (Hours)

Produces a nested JSON structure with rich ``text`` fields optimised
for semantic search, matching the format in ``simple_resource/``.
"""

import logging
import re
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text


def _safe_float(val: Any) -> float:
    """Convert a value to float, defaulting to 0.0 for NaN/None."""
    try:
        if pd.isna(val):
            return 0.0
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def excel_to_nested_json(excel_path: str) -> list[dict[str, Any]]:
    """Convert a man-hour Excel file into nested JSON.

    Handles merged cells by forward-filling Category and Task List columns.
    Builds a 3-level hierarchy: Category → Task → Activity.

    Each level has a ``text`` field with full context for embedding.

    Args:
        excel_path: Path to the Excel file.

    Returns:
        List of category-level dictionaries (one per category).
    """
    # Read all sheets
    sheet_dict = pd.read_excel(excel_path, sheet_name=None, engine="openpyxl")

    all_categories: dict[str, dict[str, Any]] = {}

    for sheet_name, df in sheet_dict.items():
        df.columns = df.columns.str.strip()
        df = df.dropna(how="all")
        if df.empty:
            continue

        # Identify columns (flexible matching)
        col_map = _map_columns(df.columns.tolist())
        if not col_map:
            logger.warning(
                f"Sheet '{sheet_name}': could not map columns "
                f"{list(df.columns)}, skipping"
            )
            continue

        cat_col = col_map["category"]
        task_col = col_map["task"]
        detail_col = col_map["detail"]
        est_col = col_map["estimate"]
        buf_col = col_map.get("buffer")

        # Forward-fill Category and Task List for merged cells
        df[cat_col] = df[cat_col].ffill()
        df[task_col] = df[task_col].ffill()

        # Group by Category → Task → Activities
        for _, row in df.iterrows():
            category = str(row[cat_col]).strip() if pd.notna(row[cat_col]) else ""
            task = str(row[task_col]).strip() if pd.notna(row[task_col]) else ""
            detail = str(row[detail_col]).strip() if pd.notna(row[detail_col]) else ""
            estimate = _safe_float(row[est_col])
            buffer_hrs = _safe_float(row[buf_col]) if buf_col else 0.0

            if not category or not detail:
                continue

            cat_slug = _slugify(category)
            task_slug = _slugify(task) if task else "general"

            # Ensure category exists
            if cat_slug not in all_categories:
                all_categories[cat_slug] = {
                    "category": category,
                    "tasks": {},
                }

            cat_data = all_categories[cat_slug]

            # Ensure task exists
            task_key = f"{cat_slug}_{task_slug}"
            if task_key not in cat_data["tasks"]:
                cat_data["tasks"][task_key] = {
                    "task": task,
                    "buffer_hours": buffer_hrs,
                    "activities": [],
                }
            task_data = cat_data["tasks"][task_key]

            # If this row has buffer, it's the task-level buffer
            if buffer_hrs > 0:
                task_data["buffer_hours"] = buffer_hrs

            # Add activity
            activity_slug = _slugify(detail)
            activity_id = f"{cat_slug}_{task_slug}_{activity_slug}"

            task_data["activities"].append({
                "id": activity_id,
                "task_detail": detail,
                "estimate_hours": estimate,
            })

    # Build the final nested structure with text fields
    result = _build_nested_output(all_categories)

    total_texts = sum(
        1  # category text
        + len(cat.get("tasks", []))  # task texts
        + sum(len(t.get("task_details", [])) for t in cat.get("tasks", []))
        for cat in result
    )
    logger.info(
        f"Converted Excel to nested JSON: "
        f"{len(result)} categories, {total_texts} text chunks"
    )
    return result


def _map_columns(columns: list[str]) -> dict[str, str] | None:
    """Map Excel column names to expected roles.

    Uses flexible matching so different header names work.

    Returns:
        Dict mapping role names to actual column names, or None.
    """
    col_lower = {c.lower(): c for c in columns}

    category = None
    task = None
    detail = None
    estimate = None
    buffer_ = None

    for key, original in col_lower.items():
        if "category" in key or "project" in key:
            category = original
        elif "task" in key and "detail" not in key:
            task = original
        elif "detail" in key or "activity" in key:
            detail = original
        elif "estimate" in key or "hour" in key and "buffer" not in key:
            estimate = original
        elif "buffer" in key:
            buffer_ = original

    if not all([category, task, detail, estimate]):
        return None

    result = {
        "category": category,
        "task": task,
        "detail": detail,
        "estimate": estimate,
    }
    if buffer_:
        result["buffer"] = buffer_
    return result


def _build_nested_output(
    categories: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Build the final nested JSON with summary and text fields."""
    output: list[dict[str, Any]] = []

    for cat_slug, cat_data in categories.items():
        category_name = cat_data["category"]
        tasks_output: list[dict[str, Any]] = []
        cat_total_estimate = 0.0
        cat_total_buffer = 0.0

        for task_key, task_data in cat_data["tasks"].items():
            task_name = task_data["task"]
            task_buffer = task_data["buffer_hours"]
            activities = task_data["activities"]

            task_estimate = sum(a["estimate_hours"] for a in activities)
            task_total = task_estimate + task_buffer

            # Build activity details with text fields
            details_output: list[dict[str, Any]] = []
            for act in activities:
                buffer_note = (
                    f'When this activity is done as PART of the task '
                    f'"{task_name}", buffer is not counted per-activity '
                    f'— use the task-level buffer ({task_buffer}h) instead. '
                    f'When this activity is done STANDALONE (scoped and '
                    f'delivered on its own, separate from the rest of the '
                    f'task), use standalone_buffer_hours (fixed 0.5h) instead.'
                )
                act_text = (
                    f'{category_name} → {task_name} → {act["task_detail"]}. '
                    f'Estimate: {act["estimate_hours"]}h. '
                    f'If done as part of the "{task_name}" task, buffer is '
                    f'not counted per-activity — the task has a {task_buffer}h '
                    f'buffer total. If this activity is scoped and done '
                    f'standalone on its own, use a fixed 0.5h buffer instead.'
                )
                details_output.append({
                    "id": act["id"],
                    "task_detail": act["task_detail"],
                    "estimate_hours": act["estimate_hours"],
                    "buffer_scope": "task-level",
                    "buffer_note": buffer_note,
                    "standalone_buffer_hours": 0.5,
                    "text": act_text,
                })

            task_text = (
                f'{category_name} → {task_name}: '
                f'{len(activities)} activities, '
                f'total estimate {task_estimate}h, '
                f'buffer {task_buffer}h, '
                f'grand total {task_total}h including buffer. '
                f'Buffer applies to the whole task, not to '
                f'individual activities.'
            )

            task_slug = _slugify(task_name)
            tasks_output.append({
                "id": f"{cat_slug}_{task_slug}_summary",
                "task": task_name,
                "estimate_hours": task_estimate,
                "buffer_hours": task_buffer,
                "total_hours": task_total,
                "task_details": details_output,
                "text": task_text,
            })

            cat_total_estimate += task_estimate
            cat_total_buffer += task_buffer

        cat_grand_total = cat_total_estimate + cat_total_buffer
        cat_text = (
            f'{category_name} project overview: '
            f'{len(tasks_output)} tasks, '
            f'total estimate {cat_total_estimate}h, '
            f'total buffer {cat_total_buffer}h, '
            f'grand total {cat_grand_total}h including buffer.'
        )

        output.append({
            "id": f"{cat_slug}_summary",
            "type": "category_summary",
            "category": category_name,
            "task_count": len(tasks_output),
            "total_estimate_hours": cat_total_estimate,
            "total_buffer_hours": cat_total_buffer,
            "grand_total_hours": cat_grand_total,
            "tasks": tasks_output,
            "text": cat_text,
        })

    return output


def extract_texts_from_nested(nested_json: list[dict[str, Any]]) -> list[str]:
    """Extract all ``text`` fields from nested JSON for embedding.

    Collects texts at all three levels: category, task, and activity.

    Args:
        nested_json: The nested JSON structure from ``excel_to_nested_json``.

    Returns:
        List of text strings ready for embedding.
    """
    texts: list[str] = []
    for category in nested_json:
        if category.get("text"):
            texts.append(category["text"])
        for task in category.get("tasks", []):
            if task.get("text"):
                texts.append(task["text"])
            for detail in task.get("task_details", []):
                if detail.get("text"):
                    texts.append(detail["text"])
    return texts
