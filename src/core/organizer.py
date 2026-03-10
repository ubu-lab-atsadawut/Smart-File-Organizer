from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from ..classifiers.base import FileClassifier
from ..classifiers.custom_classifier import CustomClassifier
from ..classifiers.factory import ClassifierFactory
from .mover import FileMover
from .scanner import FileScanner


@dataclass
class OrganizationResult:
    scanned_count: int
    moved_count: int
    category_counts: dict[str, int]
    errors: list[str]


@dataclass
class ResetResult:
    reset_count: int
    folder_counts: dict[str, int]
    errors: list[str]


class FileOrganizer:
    """Coordinates scanning, classifying, and moving files."""

    def __init__(
        self,
        scanner: FileScanner | None = None,
        mover: FileMover | None = None,
        classifiers: list[FileClassifier] | None = None,
    ) -> None:
        self.scanner = scanner or FileScanner()
        self.mover = mover or FileMover()
        self.classifiers = classifiers or ClassifierFactory.create()

    def get_all_categories(self) -> list[dict[str, any]]:
        """Return a list of dicts with 'name' and 'extensions'."""
        result = []
        for classifier in self.classifiers:
            if classifier.category:
                result.append({
                    "name": classifier.category,
                    "extensions": set(classifier.extensions)
                })
        return result

    def save_categories(self, category_data: list[dict[str, any]]) -> None:
        """Replace all existing categories with new ones, validating duplicates."""
        # 1. Validate for duplicates across all submitted data
        seen_extensions = {}
        for cat in category_data:
            name = cat["name"]
            # Normalize extensions
            incoming = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in cat["extensions"]}
            for ext in incoming:
                if ext in seen_extensions:
                    conflict_cat = seen_extensions[ext]
                    raise ValueError(
                        f"'{ext}' is assigned to both '{conflict_cat}' and '{name}'. "
                        "Extensions must be unique."
                    )
                seen_extensions[ext] = name
            
            # Store normalized back for instance creation
            cat["extensions"] = incoming
            
        # 2. Build new list of classifiers
        new_classifiers = []
        for cat in category_data:
            new_classifiers.append(CustomClassifier(cat["name"], cat["extensions"]))
            
        self.classifiers = new_classifiers

    def scan_files(self, folder_path: str | Path) -> list[Path]:
        return self.scanner.scan(folder_path)

    def scan_summary(self, folder_path: str | Path) -> dict[str, int]:
        files = self.scan_files(folder_path)
        grouped = self._group_by_category(files)
        return {category: len(grouped[category]) for category in grouped}

    def scan_detailed(self, folder_path: str | Path) -> dict[str, list[str]]:
        """Return category → list of filenames."""
        files = self.scan_files(folder_path)
        grouped = self._group_by_category(files)
        return {cat: [f.name for f in paths] for cat, paths in grouped.items()}

    def organize(self, folder_path: str | Path) -> OrganizationResult:
        root = Path(folder_path)
        files = self.scan_files(root)
        grouped = self._group_by_category(files)

        moved_count = 0
        errors: list[str] = []
        for category, file_list in grouped.items():
            for file_path in file_list:
                try:
                    self.mover.move(file_path, root, category)
                    moved_count += 1
                except Exception as exc:
                    errors.append(f"{file_path.name}: {exc}")

        category_counts = {category: len(file_list) for category, file_list in grouped.items()}
        return OrganizationResult(
            scanned_count=len(files),
            moved_count=moved_count,
            category_counts=category_counts,
            errors=errors,
        )

    def reset_files(self, folder_path: str | Path) -> ResetResult:
        root = Path(folder_path)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid folder path: {root}")

        moved_count = 0
        folder_counts: dict[str, int] = {}
        errors: list[str] = []

        for folder_name in self._known_categories():
            category_folder = root / folder_name
            if not category_folder.exists() or not category_folder.is_dir():
                continue

            files = [entry for entry in category_folder.iterdir() if entry.is_file()]
            if not files:
                continue

            folder_counts[folder_name] = len(files)
            for file_path in files:
                try:
                    self.mover.move_to_folder(file_path, root)
                    moved_count += 1
                except Exception as exc:
                    errors.append(f"{file_path.name}: {exc}")

        return ResetResult(reset_count=moved_count, folder_counts=folder_counts, errors=errors)

    def _group_by_category(self, files: list[Path]) -> dict[str, list[Path]]:
        grouped: dict[str, list[Path]] = defaultdict(list)

        for file_path in files:
            category = self._classify(file_path)
            grouped[category].append(file_path)

        return dict(grouped)

    def _classify(self, file_path: Path) -> str:
        for classifier in self.classifiers:
            category = classifier.classify(file_path)
            if category:
                return category
        return "Others"

    def _known_categories(self) -> list[str]:
        categories: list[str] = []

        for classifier in self.classifiers:
            if classifier.category and classifier.category not in categories:
                categories.append(classifier.category)

        if "Others" not in categories:
            categories.append("Others")

        return categories
