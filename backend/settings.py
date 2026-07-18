"""Application settings persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SettingsManager:
    """Persist simple application settings to disk."""

    def __init__(self, file_path: str | Path | None = None):
        self.file_path = Path(file_path or Path(__file__).resolve().parent.parent / "config" / "settings.json")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = {}
        self.load()

    def load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            self._data = {}
            return self._data

        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                self._data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            self._data = {}

        return self._data

    def save(self) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(self._data, handle, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def remove(self, key: str) -> None:
        self._data.pop(key, None)
