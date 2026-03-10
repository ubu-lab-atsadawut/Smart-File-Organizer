from __future__ import annotations

from pathlib import Path

from .base import FileClassifier


class ImageClassifier(FileClassifier):
    def __init__(self) -> None:
        self.category = "Images"
        self._extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

    def classify(self, file_path: Path) -> str | None:
        return self.category if file_path.suffix.lower() in self._extensions else None
