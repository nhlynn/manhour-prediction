"""Export route blueprint for MHES.

Handles data export to Excel format matching the simple_resource template.
"""

import logging
import os
import re

from flask import Blueprint, current_app, jsonify, request, send_file
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

export_bp = Blueprint("export", __name__)


@export_bp.route("/excel", methods=["POST"])
def export_excel():
    """Export preview data to an Excel file in simple_resource folder.

    Expects JSON body with ``projectName`` and ``categories``.
    Returns the generated file as a download.
    """
    data = request.get_json(silent=True) or {}
    project_name = (data.get("projectName") or "").strip()
    categories = data.get("categories", [])

    if not project_name:
        return jsonify({"error": "Project name is required."}), 400

    if not categories:
        return jsonify({"error": "No data to export."}), 400

    # Sanitize filename
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", project_name)
    filename = f"{safe_name}_manhour.xlsx"
    output_folder = os.path.join(current_app.root_path, "exports")
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)

    try:
        _build_workbook(filepath, project_name, categories)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({"error": str(e)}), 500

    return send_file(filepath, as_attachment=True, download_name=filename)


def _build_workbook(filepath: str, project_name: str, categories: list) -> None:
    """Build an Excel workbook matching the reference template format."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Manhour"

    # --- Styles ---
    title_font = Font(bold=True, size=14)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="333333", end_color="333333", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center")
    cat_font = Font(bold=True)
    total_font = Font(bold=True)
    total_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    center_align = Alignment(horizontal="center", vertical="center")
    wrap_align = Alignment(vertical="center", wrap_text=True)

    # Column widths
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 15

    # --- Row 1-2: Title (merged) ---
    ws.merge_cells("A1:D2")
    title_cell = ws["A1"]
    title_cell.value = f"{project_name} Manhour"
    title_cell.font = title_font
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    # --- Row 3: Empty ---

    # --- Row 4: Headers ---
    headers = ["Category", "Task List", "Estimate (Hours)", "Working Day"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # --- Data rows ---
    row = 5
    grand_total = 0

    for cat in categories:
        cat_start_row = row
        cat_name = cat.get("category", "")

        # Each task as a numbered row (no activity detail flattening)
        task_num = 1
        cat_total_hours = 0

        for task in cat.get("tasks", []):
            task_name = task.get("task", "")
            total_hours = task.get("total_hours", 0)

            # Task List column: numbered task name
            ws.cell(row=row, column=2, value=f"{task_num}. {task_name}").alignment = wrap_align
            ws.cell(row=row, column=2).border = thin_border

            # Estimate (Hours) per task
            ws.cell(row=row, column=3, value=total_hours).alignment = center_align
            ws.cell(row=row, column=3).border = thin_border

            # Working Day per task (= hours / 8)
            ws.cell(row=row, column=4, value=f"=C{row}/8").alignment = center_align
            ws.cell(row=row, column=4).border = thin_border

            cat_total_hours += total_hours
            task_num += 1
            row += 1

        cat_end_row = row - 1
        if cat_end_row < cat_start_row:
            continue

        cat_row_count = cat_end_row - cat_start_row + 1

        # Category column (merged)
        if cat_row_count > 1:
            ws.merge_cells(
                start_row=cat_start_row, start_column=1,
                end_row=cat_end_row, end_column=1,
            )
        cat_cell = ws.cell(row=cat_start_row, column=1, value=cat_name)
        cat_cell.font = cat_font
        cat_cell.alignment = Alignment(vertical="center")
        cat_cell.border = thin_border
        for r in range(cat_start_row, cat_end_row + 1):
            ws.cell(row=r, column=1).border = thin_border

        grand_total += cat_total_hours

    # --- Total row ---
    total_row = row
    ws.cell(row=total_row, column=1, value="Total").font = total_font
    for col_idx in range(1, 5):
        cell = ws.cell(row=total_row, column=col_idx)
        cell.fill = total_fill
        cell.border = thin_border
        cell.font = total_font

    ws.cell(row=total_row, column=3, value=grand_total).alignment = center_align
    ws.cell(row=total_row, column=4, value=f"=C{total_row}/8").alignment = center_align

    wb.save(filepath)
