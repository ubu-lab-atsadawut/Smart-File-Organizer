"""Background QThread workers for non‑blocking GUI operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QThread, Signal

from ..core.organizer import FileOrganizer, OrganizationResult, ResetResult


class ScanWorker(QThread):
    """Run scan_detailed in the background and emit the result dict."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, organizer: FileOrganizer, folder: Path) -> None:
        super().__init__()
        self._organizer = organizer
        self._folder = folder

    def run(self) -> None:
        try:
            result = self._organizer.scan_detailed(self._folder)
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))


class PreviewWorker(QThread):
    """Build a preview list of (filename, category) in the background."""

    finished = Signal(list)
    error = Signal(str)

    def __init__(self, organizer: FileOrganizer, folder: Path) -> None:
        super().__init__()
        self._organizer = organizer
        self._folder = folder

    def run(self) -> None:
        try:
            files = self._organizer.scan_files(self._folder)
            previews: list[tuple[str, str]] = []
            for fp in files:
                category = self._organizer._classify(fp)
                previews.append((fp.name, category))
            self.finished.emit(previews)
        except Exception as exc:
            self.error.emit(str(exc))


class OrganizeWorker(QThread):
    """Run organize in the background and emit the OrganizationResult."""

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, organizer: FileOrganizer, folder: Path) -> None:
        super().__init__()
        self._organizer = organizer
        self._folder = folder

    def run(self) -> None:
        try:
            result = self._organizer.organize(self._folder)
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))


class ResetWorker(QThread):
    """Run reset_files in the background and emit the ResetResult."""

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, organizer: FileOrganizer, folder: Path) -> None:
        super().__init__()
        self._organizer = organizer
        self._folder = folder

    def run(self) -> None:
        try:
            result = self._organizer.reset_files(self._folder)
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))
