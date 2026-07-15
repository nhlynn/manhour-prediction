"""Raw SQL data access for the ``temp_stashes`` table.

No business logic lives here — that belongs in
``scheduler.temp_data_service.TempDataService``. This module only knows
how to turn rows into dicts and back.
"""

import logging
import sqlite3
from typing import Any

from database.db import ensure_schema, get_connection

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS temp_stashes (
    id TEXT PRIMARY KEY,
    stash_type TEXT NOT NULL DEFAULT 'preview',
    project_name TEXT,
    created_by TEXT,
    project_remark TEXT,
    json_data TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_temp_stashes_expires_at ON temp_stashes(expires_at);
CREATE INDEX IF NOT EXISTS idx_temp_stashes_stash_type ON temp_stashes(stash_type);
"""


class TempRepository:
    """Repository for CRUD access to the ``temp_stashes`` table."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        ensure_schema(self._conn(), _SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    def insert(self, record: dict[str, Any]) -> None:
        """Insert a new stash row.

        Args:
            record: Must contain id, stash_type, project_name, created_by,
                project_remark, json_data, created_at, expires_at.
        """
        conn = self._conn()
        with conn:
            conn.execute(
                """
                INSERT INTO temp_stashes
                    (id, stash_type, project_name, created_by, project_remark,
                     json_data, created_at, expires_at)
                VALUES (:id, :stash_type, :project_name, :created_by, :project_remark,
                        :json_data, :created_at, :expires_at)
                """,
                record,
            )
        logger.debug("Inserted temp stash id=%s", record.get("id"))

    def get_by_id(self, stash_id: str) -> sqlite3.Row | None:
        """Return a single stash row by id, or None if not found."""
        return self._conn().execute(
            "SELECT * FROM temp_stashes WHERE id = ?", (stash_id,)
        ).fetchone()

    def exists(self, stash_id: str) -> bool:
        """Return whether a stash with this id exists."""
        return self.get_by_id(stash_id) is not None

    def list_all(self, stash_type: str | None = None) -> list[sqlite3.Row]:
        """Return all stashes, oldest first, optionally filtered by type."""
        if stash_type is None:
            return self._conn().execute(
                "SELECT * FROM temp_stashes ORDER BY created_at ASC"
            ).fetchall()
        return self._conn().execute(
            "SELECT * FROM temp_stashes WHERE stash_type = ? ORDER BY created_at ASC",
            (stash_type,),
        ).fetchall()

    def delete(self, stash_id: str) -> bool:
        """Delete a stash by id. Returns True if a row was removed."""
        conn = self._conn()
        with conn:
            cursor = conn.execute("DELETE FROM temp_stashes WHERE id = ?", (stash_id,))
        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug("Deleted temp stash id=%s", stash_id)
        return deleted

    def delete_older_than(self, cutoff_iso: str) -> list[sqlite3.Row]:
        """Delete stashes with created_at before cutoff_iso, returning the deleted rows."""
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM temp_stashes WHERE created_at < ? ORDER BY created_at ASC",
            (cutoff_iso,),
        ).fetchall()
        if rows:
            with conn:
                conn.execute("DELETE FROM temp_stashes WHERE created_at < ?", (cutoff_iso,))
        return rows

    def clear_expired(self, now_iso: str) -> list[sqlite3.Row]:
        """Delete stashes whose expires_at has passed, returning the deleted rows."""
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM temp_stashes WHERE expires_at IS NOT NULL AND expires_at < ?",
            (now_iso,),
        ).fetchall()
        if rows:
            with conn:
                conn.execute(
                    "DELETE FROM temp_stashes WHERE expires_at IS NOT NULL AND expires_at < ?",
                    (now_iso,),
                )
        return rows

    def count(self) -> int:
        """Return the total number of stash rows."""
        row = self._conn().execute("SELECT COUNT(*) AS c FROM temp_stashes").fetchone()
        return row["c"]
