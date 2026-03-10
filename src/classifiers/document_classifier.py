from __future__ import annotations

from pathlib import Path

from .base import FileClassifier


class DocumentClassifier(FileClassifier):
    def __init__(self) -> None:
        self.category = "Documents"
        self._extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".rtf",
            ".odt",
            ".xls",
            ".xlsx",
            ".csv",
            ".ppt",
            ".pptx",
        }

    def classify(self, file_path: Path) -> str | None:
        return self.category if file_path.suffix.lower() in self._extensions else None
