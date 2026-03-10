from __future__ import annotations

from pathlib import Path

from .base import FileClassifier


class CustomClassifier(FileClassifier):
    """Dynamic classifier for user-defined categories and extensions."""

    def __init__(self, category_name: str, extensions: set[str]) -> None:
        self.category = category_name
        # Ensure extensions are strictly lowercase and start with a dot
        self._extensions = {
            ext if ext.startswith(".") else f".{ext}"
            for ext in (e.lower() for e in extensions)
        }

    def classify(self, file_path: Path) -> str | None:
        return self.category if file_path.suffix.lower() in self._extensions else None
