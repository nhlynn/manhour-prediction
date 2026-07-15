"""Export History service for MHES.

Stores metadata about generated Excel exports (project name, created by,
file location/size, task/hour totals) in a dedicated SQLite database, so
the Export History page can be rendered from a fast metadata lookup
instead of re-scanning and re-reading every Excel file in the exports
folder on every page load.

The actual Excel files are untouched by this module — it only records
*where* a file is and *what* it contains, never moves/copies/deletes it.
No other module should open the export history database directly; go
through this service.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Any

from database.db import ensure_schema, get_connection

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS export_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT,
    created_by TEXT,
    export_date TEXT,
    file_name TEXT NOT NULL,
    file_url TEXT,
    file_path TEXT,
    file_size INTEGER,
    total_tasks INTEGER,
    total_hours REAL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_export_history_created_at ON export_history(created_at);
CREATE INDEX IF NOT EXISTS idx_export_history_file_name ON export_history(file_name);
"""


class ExportHistoryService:
    """Service for reading/writing Export History metadata (SQLite-backed)."""

    def __init__(self, db_path: str) -> None:
        """Initialize the service.

        Args:
            db_path: Path to the export history SQLite database file.
        """
        self.db_path = db_path
        conn = self._conn()
        ensure_schema(conn, _SCHEMA)
        self._ensure_file_path_column(conn)

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    @staticmethod
    def _ensure_file_path_column(conn: sqlite3.Connection) -> None:
        """Add the ``file_path`` column for databases created before it existed.

        ``CREATE TABLE IF NOT EXISTS`` in ``_SCHEMA`` only applies to brand
        new databases, so an existing ``export_history`` table (from
        before this column was introduced) needs an explicit ALTER.
        """
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(export_history)")}
        if "file_path" not in columns:
            conn.execute("ALTER TABLE export_history ADD COLUMN file_path TEXT")
            logger.info("Added file_path column to export_history table.")

    def insert_history(
        self,
        *,
        project_name: str,
        created_by: str,
        export_date: str,
        file_name: str,
        file_url: str,
        file_size: int,
        total_tasks: int,
        total_hours: float,
        file_path: str | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """Insert one export history record.

        Args:
            project_name: Project name entered on Preview.
            created_by: Created By entered on Preview.
            export_date: When the export was generated (ISO datetime string).
            file_name: Name of the generated Excel file (as saved on disk).
            file_url: URL for downloading the file (e.g. from ``url_for``).
            file_size: Size of the generated file, in bytes.
            total_tasks: Total number of tasks across all categories.
            total_hours: Total estimated hours across all tasks.
            file_path: Absolute path to the file in the local exports
                folder, recorded at export time for reference.
            created_at: Record creation timestamp (ISO datetime string).
                Defaults to now; only overridden when migrating existing
                records so their original ordering is preserved.

        Returns:
            The newly created history record.
        """
        conn = self._conn()
        created_at = created_at or datetime.now().isoformat()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO export_history
                    (project_name, created_by, export_date, file_name, file_url,
                     file_path, file_size, total_tasks, total_hours, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_name, created_by, export_date, file_name, file_url,
                    file_path, file_size, total_tasks, total_hours, created_at,
                ),
            )
        record = self.get_history_by_id(cursor.lastrowid)
        logger.info(
            "Export history saved: id=%s file_name=%s project_name=%r",
            cursor.lastrowid, file_name, project_name,
        )
        return record

    def get_history(self) -> list[dict[str, Any]]:
        """Return all export history records, newest first."""
        rows = self._conn().execute(
            "SELECT * FROM export_history ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def get_history_by_id(self, history_id: int) -> dict[str, Any] | None:
        """Return a single export history record by id, or None if not found."""
        row = self._conn().execute(
            "SELECT * FROM export_history WHERE id = ?", (history_id,)
        ).fetchone()
        return dict(row) if row is not None else None

    def delete_history(self, history_id: int) -> bool:
        """Delete a single export history record by id.

        Only removes the metadata row — never touches the Excel file itself.

        Args:
            history_id: Id of the history record to remove.

        Returns:
            True if a record was removed, False if no match was found.
        """
        conn = self._conn()
        with conn:
            cursor = conn.execute("DELETE FROM export_history WHERE id = ?", (history_id,))
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("Deleted export history id=%s", history_id)
        return deleted
