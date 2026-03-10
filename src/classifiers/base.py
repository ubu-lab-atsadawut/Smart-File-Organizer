from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class FileClassifier(ABC):
    """Base strategy for file classification."""

    category: str = ""
    _extensions: set[str] = set()

    @property
    def extensions(self) -> set[str]:
        """Return the set of file extensions this classifier handles."""
        return self._extensions

    @extensions.setter
    def extensions(self, value: set[str]) -> None:
        self._extensions = value

    @abstractmethod
    def classify(self, file_path: Path) -> str | None:
        """Return category if this classifier supports the file, else None."""
