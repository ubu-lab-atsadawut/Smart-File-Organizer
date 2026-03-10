from __future__ import annotations

from .base import FileClassifier
from .code_classifier import CodeClassifier
from .document_classifier import DocumentClassifier
from .image_classifier import ImageClassifier
from .video_classifier import VideoClassifier


class ClassifierFactory:
    """Factory responsible for creating classifier strategies."""

    @staticmethod
    def create() -> list[FileClassifier]:
        return [
            ImageClassifier(),
            VideoClassifier(),
            DocumentClassifier(),
            CodeClassifier(),
        ]
