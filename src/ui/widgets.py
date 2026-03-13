"""Reusable styled widget components for Smart File Organizer."""

from __future__ import annotations

import math
import os
import hashlib
from collections import defaultdict

from PySide6.QtCore import Qt, QTimer, Signal, QPoint, QRect, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialog,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QLayout,
    QSizePolicy,
)

from .styles import (
    BG_CARD,
    BG_CARD_HOVER,
    BORDER,
    CATEGORY_COLOURS,
    CATEGORY_ICONS,
    DANGER,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


# ── Category Card (expandable) ──────────────────────────────────────


class CategoryCard(QFrame):
    """A result card that expands on click to show individual filenames."""

    def __init__(
        self,
        category: str,
        count: int,
        filenames: list[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("CategoryCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._expanded = False
        self._filenames = filenames or []

        accent = self._get_category_color(category)
        icon = CATEGORY_ICONS.get(category, "📁")

        # root layout
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # ── header row (always visible) ──
        header = QWidget()
        header.setFixedHeight(90)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(14)

        # colour accent bar
        bar = QFrame()
        bar.setFixedSize(4, 54)
        bar.setStyleSheet(f"background: {accent}; border-radius: 2px;")
        header_layout.addWidget(bar)

        # icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px; background: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedWidth(40)
        header_layout.addWidget(icon_label)

        # text column
        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        name_label = QLabel(category)
        name_label.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;"
        )
        text_col.addWidget(name_label)

        subtitle_text = f"{count} file{'s' if count != 1 else ''}"
        if self._filenames:
            subtitle_text += "  ·  click to expand"
        count_label = QLabel(subtitle_text)
        count_label.setStyleSheet(
            f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;"
        )
        text_col.addWidget(count_label)
        self._subtitle = count_label

        header_layout.addLayout(text_col, stretch=1)

        # chevron
        self._chevron = QLabel("▸")
        self._chevron.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._chevron.setFixedWidth(24)
        self._chevron.setStyleSheet(
            f"font-size: 16px; color: {TEXT_MUTED}; background: transparent;"
        )
        if not self._filenames:
            self._chevron.hide()
        header_layout.addWidget(self._chevron)

        # count number (plain text)
        badge = QLabel(str(count))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedWidth(36)
        badge.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {TEXT_SECONDARY}; background: transparent;"
        )
        header_layout.addWidget(badge)

        self._root.addWidget(header)

        # ── file list grouped by extension (hidden until expanded) ──
        self._file_container = QWidget()
        self._file_container.setVisible(False)
        file_layout = QVBoxLayout(self._file_container)
        file_layout.setContentsMargins(56, 0, 16, 14)
        file_layout.setSpacing(2)

        # group filenames by extension
        ext_groups: dict[str, list[str]] = defaultdict(list)
        for fname in self._filenames:
            ext = os.path.splitext(fname)[1].lower() or "(no extension)"
            ext_groups[ext].append(fname)

        # sort groups by count descending
        for ext, names in sorted(ext_groups.items(), key=lambda x: -len(x[1])):
            # extension header
            ext_header = QLabel(
                f"{ext}  —  {len(names)} file{'s' if len(names) != 1 else ''}"
            )
            ext_header.setStyleSheet(
                f"font-size: 12px; font-weight: 700; color: {accent}; "
                f"background: transparent; padding-top: 6px;"
            )
            file_layout.addWidget(ext_header)

            # individual files
            for name in names:
                lbl = QLabel(f"    {name}")
                lbl.setStyleSheet(
                    f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;"
                )
                file_layout.addWidget(lbl)

        self._root.addWidget(self._file_container)

    def mousePressEvent(self, _event) -> None:  # noqa: N802
        if not self._filenames:
            return
        self._expanded = not self._expanded
        self._file_container.setVisible(self._expanded)
        self._chevron.setText("▾" if self._expanded else "▸")
        self._subtitle.setText(
            f"{len(self._filenames)} file{'s' if len(self._filenames) != 1 else ''}"
            + ("  ·  click to collapse" if self._expanded else "  ·  click to expand")
        )

    def _get_category_color(self, category: str) -> str:
        """Return the defined colour or generate a vibrant one based on the name."""
        if category in CATEGORY_COLOURS:
            return CATEGORY_COLOURS[category]

        h = int(hashlib.md5(category.encode("utf-8")).hexdigest(), 16)
        hue = h % 360
        # Use HSV to ensure it is vibrant and visible on dark background
        return QColor.fromHsv(hue, 160, 240).name()


# ── Loading Spinner ─────────────────────────────────────────────────


class LoadingSpinner(QWidget):
    """Animated bouncing‑dots spinner."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(120, 40)
        self._dot_count = 3
        self._dot_radius = 6
        self._spacing = 20
        self._phases: list[float] = [0.0] * self._dot_count
        self._step = 0

        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._advance)

    def start(self) -> None:
        self._step = 0
        self._timer.start()
        self.show()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def _advance(self) -> None:
        self._step += 1
        for i in range(self._dot_count):
            self._phases[i] = math.sin((self._step + i * 8) * 0.12) * 8
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        total_w = (self._dot_count - 1) * self._spacing
        start_x = (self.width() - total_w) / 2
        base_y = self.height() / 2

        for i in range(self._dot_count):
            x = start_x + i * self._spacing
            y = base_y - self._phases[i]
            opacity = 0.5 + 0.5 * ((self._phases[i] + 8) / 16)
            colour = QColor("#58a6ff")
            colour.setAlphaF(min(opacity, 1.0))
            painter.setBrush(colour)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                int(x - self._dot_radius), int(y - self._dot_radius),
                self._dot_radius * 2, self._dot_radius * 2,
            )
        painter.end()


# ── Result Panel ────────────────────────────────────────────────────


class ResultPanel(QScrollArea):
    """Scrollable container for CategoryCard widgets."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setObjectName("ResultContainer")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)
        self._layout.addStretch()
        self.setWidget(self._container)

    # ── public API ──

    def clear(self) -> None:
        """Remove all child widgets."""
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_cards(self, data: dict[str, int | list[str]]) -> None:
        """Display CategoryCard widgets.

        Accepts either:
          - dict[str, int]        → count-only cards (organize/reset results)
          - dict[str, list[str]]  → expandable cards with filenames (scan results)
        """
        self.clear()
        ordered = ["Images", "Videos", "Documents", "Code", "Others"]
        pos = 0

        def _add(cat: str, value: int | list[str]) -> int:
            if isinstance(value, list):
                count = len(value)
                filenames = value
            else:
                count = value
                filenames = None
            if count > 0:
                card = CategoryCard(cat, count, filenames)
                self._layout.insertWidget(pos, card)
                return pos + 1
            return pos

        for cat in ordered:
            if cat in data:
                pos = _add(cat, data[cat])
        for cat, value in data.items():
            if cat not in ordered:
                pos = _add(cat, value)

    def show_message(self, text: str) -> None:
        """Display a single text message."""
        self.clear()
        label = QLabel(text)
        label.setObjectName("PlaceholderLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        self._layout.insertWidget(0, label)


# ── Settings Dialog ─────────────────────────────────────────────────

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, hSpacing=-1, vSpacing=-1):
        super().__init__(parent)
        self._hSpace = hSpacing
        self._vSpace = vSpacing
        self._items = []
        if margin != -1:
            self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._items.append(item)

    def horizontalSpacing(self):
        if self._hSpace >= 0:
            return self._hSpace
        return sum(self.getContentsMargins())

    def verticalSpacing(self):
        if self._vSpace >= 0:
            return self._vSpace
        return sum(self.getContentsMargins())

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self._items:
            spaceX = self.horizontalSpacing()
            spaceY = self.verticalSpacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()


class TagLineEdit(QLineEdit):
    backspace_empty = Signal()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Backspace and not self.text():
            self.backspace_empty.emit()
        super().keyPressEvent(event)


class Tag(QFrame):
    removed = Signal(object)
    
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text
        self.setObjectName("Tag")
        self.setStyleSheet(f"""
            QFrame#Tag {{
                background: {BG_CARD_HOVER};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 4, 2)
        layout.setSpacing(4)
        label = QLabel(text)
        label.setStyleSheet(f"color: {TEXT_PRIMARY}; border: none; background: transparent; font-size: 13px;")
        close_btn = QPushButton("×")
        close_btn.setFixedSize(16, 16)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{ color: {TEXT_MUTED}; border: none; background: transparent; font-weight: bold; font-size: 16px; padding-bottom: 2px; }}
            QPushButton:hover {{ color: {DANGER}; }}
        """)
        close_btn.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(label)
        layout.addWidget(close_btn)


class TagInputFrame(QWidget):
    def __init__(self, extensions: set[str], parent=None):
        super().__init__(parent)
        self.setObjectName("TagInputFrame")
        self.setStyleSheet(f"#TagInputFrame {{ background: transparent; border: 1px solid #222; border-radius: 4px; }}")
        self.setCursor(Qt.CursorShape.IBeamCursor)
        
        self._layout = FlowLayout(self, margin=4, hSpacing=6, vSpacing=6)
        self._input = TagLineEdit()
        self._input.setPlaceholderText("Add ext (e.g. .jpg)...")
        self._input.setStyleSheet(f"background: transparent; border: none; color: {TEXT_PRIMARY}; font-size: 13px; min-width: 140px;")
        self._input.returnPressed.connect(self._commit_text)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.backspace_empty.connect(self._on_backspace_empty)
        
        self._tags = []
        for ext in sorted(extensions):
            if ext:
                self.add_tag(ext)
                
        self._layout.addWidget(self._input)
        
    def mousePressEvent(self, event):
        self._input.setFocus()
        
    def _on_text_changed(self, text: str):
        if text.endswith(' ') or text.endswith(','):
            self._commit_text()
            
    def _commit_text(self):
        text = self._input.text().replace(',', ' ').strip()
        if text:
            current_exts = {tag.text for tag in self._tags}
            parts = [p.strip() for p in text.split() if p.strip()]
            for p in parts:
                if not p.startswith('.'):
                    p = '.' + p
                if p not in current_exts:
                    self.add_tag(p)
                    current_exts.add(p)
        self._input.clear()

    def _on_backspace_empty(self):
        if self._tags:
            tag = self._tags[-1]
            # put extension back (without dot) to make fixing typos easy
            self._input.setText(tag.text.lstrip('.'))
            self.remove_tag(tag)

    def add_tag(self, text: str):
        tag = Tag(text)
        tag.removed.connect(self.remove_tag)
        self._tags.append(tag)
        self._layout.removeWidget(self._input)
        self._layout.addWidget(tag)
        self._layout.addWidget(self._input)

    def remove_tag(self, tag: Tag):
        if tag in self._tags:
            self._tags.remove(tag)
        self._layout.removeWidget(tag)
        tag.deleteLater()

    def get_extensions(self) -> set[str]:
        self._commit_text()
        return {tag.text for tag in self._tags}


class SettingsRow(QFrame):
    """A row containing Name, Extensions, and Delete button."""
    delete_requested = Signal(object)

    def __init__(self, name: str, extensions: set[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsRow")
        self.setStyleSheet(
            f"QFrame#SettingsRow {{ background: #111; border: 1px solid {BORDER}; border-radius: 4px; }}"
        )
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Category Name")
        self.name_input.setStyleSheet(f"background: transparent; border: none; color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
        self.name_input.setMinimumWidth(120)
        self.name_input.setMaximumWidth(150)
        
        self.ext_input = TagInputFrame(extensions)
        
        self.del_btn = QPushButton("🗑")
        self.del_btn.setFixedSize(32, 32)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet(
            f"background: transparent; color: {DANGER}; border: none; font-size: 16px;"
        )
        self.del_btn.clicked.connect(lambda: self.delete_requested.emit(self))
        
        layout.addWidget(self.name_input, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.ext_input, 1)
        layout.addWidget(self.del_btn, 0, Qt.AlignmentFlag.AlignTop)

    def get_data(self) -> tuple[str, set[str]]:
        name = self.name_input.text().strip()
        extensions = self.ext_input.get_extensions()
        return name, extensions


class SettingsDialog(QDialog):
    """Dialog to manage all categories and extensions."""

    def __init__(self, categories_data: list[dict[str, any]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings - Categories")
        self.setFixedSize(500, 400)
        self.setObjectName("SettingsDialog")

        self.setStyleSheet(f"background: {BG_CARD}; color: {TEXT_PRIMARY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Manage Categories")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY};")
        layout.addWidget(title)
        
        headers = QHBoxLayout()
        h_name = QLabel("Name")
        h_name.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        h_ext = QLabel("Extensions")
        h_ext.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        headers.addWidget(h_name, 1)
        headers.addWidget(h_ext, 2)
        headers.addSpacing(32) # space for delete button
        layout.addLayout(headers)

        # Scroll area for rows
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(8)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.rows_container)
        
        layout.addWidget(self.scroll)
        
        self.rows: list[SettingsRow] = []

        # Populate rows
        for cat in categories_data:
            self.add_row(cat["name"], cat["extensions"])

        # Add New button
        add_btn = QPushButton("➕ Add Category")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"background: transparent; color: {CATEGORY_COLOURS.get('Code', '#ccc')}; border: 1px dashed {BORDER}; border-radius: 4px; padding: 8px;")
        add_btn.clicked.connect(lambda: self.add_row("", set()))
        layout.addWidget(add_btn)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"background: transparent; color: {TEXT_SECONDARY}; border: none; padding: 8px 16px;")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save & Apply")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"background: #58a6ff; color: #fff; font-weight: 700; border: none; border-radius: 4px; padding: 8px 16px;")
        save_btn.clicked.connect(self.accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def add_row(self, name: str, extensions: set[str]) -> None:
        row = SettingsRow(name, extensions, self.rows_container)
        row.delete_requested.connect(self.remove_row)
        self.rows_layout.addWidget(row)
        self.rows.append(row)

    def remove_row(self, row: SettingsRow) -> None:
        self.rows_layout.removeWidget(row)
        row.deleteLater()
        if row in self.rows:
            self.rows.remove(row)

    def get_data(self) -> list[dict[str, any]]:
        """Return the list of data dicts for organizer."""
        data = []
        for row in self.rows:
            name, exts = row.get_data()
            if not name or not exts:
                continue # Skip empty rows
            data.append({"name": name, "extensions": exts})
        return data
