from __future__ import annotations

from pathlib import Path


class FileScanner:
    """Single responsibility: collect files from a folder."""

    def scan(self, folder_path: str | Path) -> list[Path]:
        folder = Path(folder_path)

        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Invalid folder path: {folder}")

        return [entry for entry in folder.iterdir() if entry.is_file()]
