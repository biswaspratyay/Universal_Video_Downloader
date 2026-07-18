import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List


class DownloadHistoryStore:
    def __init__(self, file_path: str | Path | None = None):
        self.file_path = Path(file_path or Path(__file__).resolve().parent.parent / "config" / "download_history.json")

    def load(self) -> List[dict[str, Any]]:
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, list):
                    return [self._normalize_entry(item) for item in data]
        except (json.JSONDecodeError, OSError):
            return []

        return []

    def save(self, entries: List[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(entries, handle, indent=2)

    def add(self, entry: str | dict[str, Any]) -> List[dict[str, Any]]:
        entries = self.load()
        new_entry = self._normalize_entry(entry)
        new_entry["timestamp"] = datetime.now(timezone.utc).isoformat()

        filtered = [item for item in entries if item.get("title") != new_entry.get("title")]
        filtered.insert(0, new_entry)
        self.save(filtered)
        return filtered

    def clear(self) -> None:
        self.save([])

    @staticmethod
    def _normalize_entry(entry: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(entry, dict):
            normalized = {
                "title": str(entry.get("title", "")),
                "thumbnail_url": entry.get("thumbnail_url"),
            }
            if entry.get("timestamp"):
                normalized["timestamp"] = entry.get("timestamp")
            return normalized

        return {"title": str(entry), "thumbnail_url": None}
