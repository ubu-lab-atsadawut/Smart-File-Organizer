from __future__ import annotations

from pathlib import Path

from .base import FileClassifier


class VideoClassifier(FileClassifier):
    def __init__(self) -> None:
        self.category = "Videos"
        self._extensions = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}

    def classify(self, file_path: Path) -> str | None:
        return self.category if file_path.suffix.lower() in self._extensions else None
