from __future__ import annotations

from pathlib import Path

from .base import FileClassifier


class CodeClassifier(FileClassifier):
    def __init__(self) -> None:
        self.category = "Code"
        self._extensions = {
            ".py",
            ".js",
            ".ts",
            ".html",
            ".css",
            ".scss",
            ".java",
            ".c",
            ".cpp",
            ".cs",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
        }

    def classify(self, file_path: Path) -> str | None:
        return self.category if file_path.suffix.lower() in self._extensions else None
