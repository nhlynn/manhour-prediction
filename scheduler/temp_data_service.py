"""Temporary data service for MHES.

Stores Preview stashes (created when starting a new AI Chatbot session
with Preview data pending) as a JSON file on the server, so they survive
closing the browser. Shared by everyone using the app (no per-user
scoping, since MHES has no login system).
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Any


class TempDataService:
    """Service for reading/writing server-side Preview stashes."""

    def __init__(self, temp_data_folder: str) -> None:
        """Initialize the service.

        Args:
            temp_data_folder: Folder where the stash file is stored.
        """
        self.temp_data_folder = temp_data_folder
        self.stashes_path = os.path.join(temp_data_folder, "stashes.json")

    def list_stashes(self) -> list[dict[str, Any]]:
        """Return all stashed Preview snapshots, oldest first."""
        if not os.path.isfile(self.stashes_path):
            return []
        with open(self.stashes_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def add_stash(
        self,
        categories: list[dict[str, Any]],
        totals: dict[str, Any],
        project_name: str,
        created_by: str = "",
        project_remark: str = "",
    ) -> dict[str, Any]:
        """Append a new stash and persist it.

        Args:
            categories: Category → Task → Activity structure from Preview.
            totals: Preview totals at the time of stashing.
            project_name: Project name entered on Preview, if any.
            created_by: Created By entered on Preview, if any.
            project_remark: Project Remark HTML entered on Preview, if any.

        Returns:
            The newly created stash record.
        """
        stashes = self.list_stashes()
        stash = {
            "id": uuid.uuid4().hex,
            "stashedAt": datetime.now().isoformat(),
            "projectName": project_name or "",
            "createdBy": created_by or "",
            "projectRemark": project_remark or "",
            "categories": categories,
            "totals": totals or {},
        }
        stashes.append(stash)
        self._save(stashes)
        return stash

    def remove_stash(self, stash_id: str) -> bool:
        """Remove a stash by id.

        Args:
            stash_id: Id of the stash to remove.

        Returns:
            True if a stash was removed, False if no match was found.
        """
        stashes = self.list_stashes()
        remaining = [s for s in stashes if s.get("id") != stash_id]
        if len(remaining) == len(stashes):
            return False
        self._save(remaining)
        return True

    def remove_older_than(self, days: int) -> list[dict[str, Any]]:
        """Remove stashes older than the given number of days.

        Compares against ``stashedAt``, which is recorded via
        ``datetime.now()`` (naive, server-local time), so this uses the
        same naive local-time basis for the cutoff.

        Args:
            days: Age threshold in days; stashes older than this are removed.

        Returns:
            The list of removed stash records (for logging purposes).
        """
        stashes = self.list_stashes()
        cutoff = datetime.now() - timedelta(days=days)

        kept: list[dict[str, Any]] = []
        removed: list[dict[str, Any]] = []
        for stash in stashes:
            stashed_at = stash.get("stashedAt", "")
            try:
                is_old = datetime.fromisoformat(stashed_at) < cutoff
            except (TypeError, ValueError):
                # Malformed/missing timestamp — keep it rather than guess.
                is_old = False

            (removed if is_old else kept).append(stash)

        if removed:
            self._save(kept)
        return removed

    def _save(self, stashes: list[dict[str, Any]]) -> None:
        os.makedirs(self.temp_data_folder, exist_ok=True)
        with open(self.stashes_path, "w", encoding="utf-8") as f:
            json.dump(stashes, f, indent=2, ensure_ascii=False)
