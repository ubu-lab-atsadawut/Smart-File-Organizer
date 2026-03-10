from __future__ import annotations

import shutil
from pathlib import Path


class FileMover:
    """Moves files into category folders."""

    def move(self, file_path: Path, destination_root: Path, category: str) -> Path:
        target_folder = self._create_folder(destination_root, category)
        return self.move_to_folder(file_path, target_folder)

    def move_to_folder(self, file_path: Path, destination_folder: Path) -> Path:
        destination_folder.mkdir(parents=True, exist_ok=True)
        target_path = self._ensure_unique_name(destination_folder / file_path.name)
        shutil.move(str(file_path), str(target_path))
        return target_path

    def _create_folder(self, root_folder: Path, category: str) -> Path:
        """Internal helper to ensure category folder exists."""
        target = root_folder / category
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _ensure_unique_name(self, target_path: Path) -> Path:
        if not target_path.exists():
            return target_path

        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        counter = 1

        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
