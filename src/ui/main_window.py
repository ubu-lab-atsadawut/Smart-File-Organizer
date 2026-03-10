"""Main application window – modern dark‑themed two‑panel layout."""

from __future__ import annotations

from pathlib import Path
import webbrowser

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..core.organizer import FileOrganizer
from .styles import (
    ACCENT,
    BG_CARD,
    BG_CARD_HOVER,
    BORDER,
    DANGER,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    app_stylesheet,
)
from .widgets import SettingsDialog, LoadingSpinner, ResultPanel
from .worker import (
    OrganizeWorker,
    ResetWorker,
    ScanWorker,
)


# ── Drag & Drop Line Edit ──────────────────────────────────────────


class FolderDropLineEdit(QLineEdit):
    """Read‑only line edit that accepts a single directory drop."""

    folderDropped = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setReadOnly(True)
        self.setPlaceholderText("Drop folder here or click Browse…")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                if Path(urls[0].toLocalFile()).is_dir():
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if len(urls) == 1 and urls[0].isLocalFile():
            dropped = Path(urls[0].toLocalFile())
            if dropped.is_dir():
                self.folderDropped.emit(str(dropped))
                event.acceptProposedAction()
                return
        event.ignore()


# ── Main Window ─────────────────────────────────────────────────────


class MainWindow(QMainWindow):
    """Two‑panel dashboard: left controls, right results."""

    def __init__(self) -> None:
        super().__init__()
        self.organizer = FileOrganizer()
        self._worker = None          # keep reference so it isn't GC'd
        self._has_scanned = False
        self._has_organized = False
        self._build_ui()

    # ────────────────────────────────────────────────────────────────
    # UI construction
    # ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Smart File Organizer")
        
        icon_path = Path(__file__).parent.parent / "assets" / "open-folder.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            
        self.resize(960, 600)
        self.setMinimumSize(760, 480)
        self.setStyleSheet(app_stylesheet())

        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── LEFT PANEL ──────────────────────────────────
        left = QWidget()
        left.setObjectName("LeftPanel")
        left.setFixedWidth(300)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 24, 20, 20)
        left_layout.setSpacing(6)

        # App branding
        title = QLabel("🗂  Smart File Organizer")
        title.setObjectName("AppTitle")
        left_layout.addWidget(title)

        subtitle = QLabel("Scan · Organize · Reset")
        subtitle.setObjectName("AppSubtitle")
        left_layout.addWidget(subtitle)

        left_layout.addSpacing(16)

        # ── Target Directory ──
        sec1 = QLabel("TARGET DIRECTORY")
        sec1.setObjectName("SectionTitle")
        left_layout.addWidget(sec1)

        self.folder_input = FolderDropLineEdit()
        self.folder_input.folderDropped.connect(self._set_folder)
        left_layout.addWidget(self.folder_input)

        browse_btn = QPushButton("📂  Browse Folder")
        browse_btn.setObjectName("PrimaryButton")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_folder)
        left_layout.addWidget(browse_btn)



        left_layout.addSpacing(12)

        # ── Actions ──
        sec2 = QLabel("ACTIONS")
        sec2.setObjectName("SectionTitle")
        left_layout.addWidget(sec2)

        self.scan_btn = self._action_button("🔍  Scan Files", "ActionButton")
        self.scan_btn.clicked.connect(self._on_scan)
        left_layout.addWidget(self.scan_btn)

        self.organize_btn = self._action_button("📦  Organize Files", "ActionButton")
        self.organize_btn.clicked.connect(self._on_organize)
        left_layout.addWidget(self.organize_btn)

        self.reset_btn = self._action_button("🔄  Reset Files", "DangerButton")
        self.reset_btn.clicked.connect(self._on_reset)
        left_layout.addWidget(self.reset_btn)

        # Organize / Reset start disabled
        self.organize_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)

        left_layout.addSpacing(16)

        self.settings_btn = QPushButton("⚙️  Settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet(
            f"background: transparent; color: {TEXT_SECONDARY}; font-weight: 700; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 10px;"
        )
        self.settings_btn.clicked.connect(self._on_settings)
        left_layout.addWidget(self.settings_btn)

        left_layout.addStretch()

        # ── User Profile Footer ───────────────────────────
        profile_widget = QPushButton()
        profile_widget.setMinimumHeight(64)
        profile_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        profile_layout = QHBoxLayout(profile_widget)
        profile_layout.setContentsMargins(8, 8, 8, 8)
        profile_layout.setSpacing(12)
        profile_widget.setStyleSheet(
            f"QPushButton {{"
            f"  background: transparent; border-radius: 8px; text-align: left;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background: {BG_CARD_HOVER};"
            f"}}"
        )
        profile_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        profile_widget.clicked.connect(lambda: webbrowser.open("https://github.com/MyName-Chet"))

        # Avatar circle from github.png
        avatar = QLabel()
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(36, 36)
        avatar.setStyleSheet(f"background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 18px;")
        avatar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Load GitHub icon
        icon_path = Path(__file__).parent.parent / "assets" / "github.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            # Scale to fit nicely in 36x36 (e.g. 24x24)
            pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            avatar.setPixmap(pixmap)
        else:
            avatar.setText("GH")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        
        name_lbl = QLabel("atsadawut__06")
        name_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 700; font-size: 13px; background: transparent;")
        # Pass mouse clicks through label to parent button
        name_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        info_layout.addWidget(name_lbl)
        
        # GitHub Link
        link_lbl = QLabel('MyName-Chet')
        link_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        link_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        info_layout.addWidget(link_lbl)

        profile_layout.addWidget(avatar)
        profile_layout.addLayout(info_layout)
        profile_layout.addStretch()

        left_layout.addWidget(profile_widget)
        left_layout.addSpacing(16)

        # status bar
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")
        left_layout.addWidget(self.status_label)

        # ── RIGHT PANEL ─────────────────────────────────
        right = QWidget()
        right.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(12)

        # header row
        header_row = QHBoxLayout()
        self.result_title = QLabel("Results")
        self.result_title.setObjectName("ResultTitle")
        header_row.addWidget(self.result_title)
        header_row.addStretch()

        self.spinner = LoadingSpinner()
        self.spinner.hide()
        header_row.addWidget(self.spinner)
        right_layout.addLayout(header_row)

        # result area
        self.result_panel = ResultPanel()
        self.result_panel.show_message("Select a folder and click Scan Files to begin.")
        right_layout.addWidget(self.result_panel)



        # ── Attach panels ───────────────────────────────
        root_layout.addWidget(left)
        root_layout.addWidget(right, stretch=1)

    # ── helpers ──

    @staticmethod
    def _action_button(text: str, name: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName(name)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(40)
        return btn

    # ────────────────────────────────────────────────────────────────
    # Folder selection
    # ────────────────────────────────────────────────────────────────

    def _browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self._set_folder(folder)

    def _set_folder(self, folder: str) -> None:
        self.folder_input.setText(folder)
        self.status_label.setText("Folder selected ✓")

    def _require_folder(self) -> Path | None:
        text = self.folder_input.text().strip()
        if not text:
            QMessageBox.warning(self, "No folder", "Please select a target folder first.")
            return None
        p = Path(text)
        if not p.exists() or not p.is_dir():
            QMessageBox.warning(self, "Invalid folder", "The selected folder does not exist.")
            return None
        return p

    # ────────────────────────────────────────────────────────────────
    # Settings (Categories)
    # ────────────────────────────────────────────────────────────────

    def _on_settings(self) -> None:
        current_data = self.organizer.get_all_categories()
        dialog = SettingsDialog(current_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            try:
                self.organizer.save_categories(new_data)
                self.status_label.setText("Categories updated successfully.")
                if self._has_scanned:
                    QMessageBox.information(
                        self, "Settings Saved",
                        "Category settings updated! Please click Scan Files again to reflect changes."
                    )
            except ValueError as e:
                # Structural error like duplicate extension
                QMessageBox.warning(self, "Validation Error", str(e))

    # ────────────────────────────────────────────────────────────────
    # Busy state helpers
    # ────────────────────────────────────────────────────────────────

    def _set_busy(self, status_text: str) -> None:
        self.status_label.setText(status_text)
        self.spinner.start()
        self._set_buttons_enabled(False)

    def _set_idle(self, status_text: str = "Ready") -> None:
        self.status_label.setText(status_text)
        self.spinner.stop()
        self._set_buttons_enabled(True)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        self.scan_btn.setEnabled(enabled)
        self.organize_btn.setEnabled(enabled and self._has_scanned)
        self.reset_btn.setEnabled(enabled and self._has_organized)

    # ────────────────────────────────────────────────────────────────
    # Scan
    # ────────────────────────────────────────────────────────────────

    def _on_scan(self) -> None:
        folder = self._require_folder()
        if folder is None:
            return
        self._set_busy("Scanning files…")
        self.result_title.setText("Scan Results")

        self._worker = ScanWorker(self.organizer, folder)
        self._worker.finished.connect(self._scan_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _scan_done(self, detailed: dict[str, list[str]]) -> None:
        total = sum(len(v) for v in detailed.values())
        self.result_panel.show_cards(detailed)
        self._has_scanned = True
        self._set_idle(f"Scan complete · {total} file{'s' if total != 1 else ''} found · click a card to expand")

    # ────────────────────────────────────────────────────────────────
    # Organize
    # ────────────────────────────────────────────────────────────────

    def _on_organize(self) -> None:
        folder = self._require_folder()
        if folder is None:
            return
        self._run_organize(folder)

    def _run_organize(self, folder: Path) -> None:
        self._set_busy("Organizing files…")
        self.result_title.setText("Organization Results")

        self._worker = OrganizeWorker(self.organizer, folder)
        self._worker.finished.connect(self._organize_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _organize_done(self, result) -> None:
        self._has_organized = True
        self._has_scanned = False
        
        if result.errors:
            msg = f"⚠  Organized {result.moved_count}/{result.scanned_count} files.\nSome files could not be moved."
            self.result_panel.show_message(msg)
            self._append_errors(result.errors)
            self._set_idle(
                f"Done · {result.moved_count}/{result.scanned_count} organized, "
                f"{len(result.errors)} failed"
            )
        else:
            msg = f"✅  Success!\n\nOrganized {result.moved_count} files into categories."
            self.result_panel.show_message(msg)
            self._set_idle(
                f"Done · {result.moved_count}/{result.scanned_count} files organized"
            )

    # ────────────────────────────────────────────────────────────────
    # Reset
    # ────────────────────────────────────────────────────────────────

    def _on_reset(self) -> None:
        folder = self._require_folder()
        if folder is None:
            return
        self._set_busy("Resetting files…")
        self.result_title.setText("Reset Results")

        self._worker = ResetWorker(self.organizer, folder)
        self._worker.finished.connect(self._reset_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _reset_done(self, result) -> None:
        if result.reset_count == 0 and not result.errors:
            self.result_panel.show_message("No files found in category folders to reset.")
            self._set_idle("Reset complete · nothing to move")
            return
            
        if result.errors:
            msg = f"⚠  Reset {result.reset_count} files.\nSome files could not be moved back."
            self.result_panel.show_message(msg)
            self._append_errors(result.errors)
            self._set_idle(
                f"Reset · {result.reset_count} moved back, {len(result.errors)} failed"
            )
        else:
            msg = f"✅  Success!\n\nReset {result.reset_count} files back to the main folder."
            self.result_panel.show_message(msg)
            self._set_idle(f"Reset · {result.reset_count} files moved back")

    # ────────────────────────────────────────────────────────────────
    # Error handling
    # ────────────────────────────────────────────────────────────────

    def _append_errors(self, errors: list[str]) -> None:
        """Append warning labels for skipped files below the result cards."""
        layout = self.result_panel._layout  # noqa: access internal layout
        pos = layout.count() - 1  # before the stretch

        header = QLabel(f"⚠  {len(errors)} file{'s' if len(errors) != 1 else ''} skipped")
        header.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {DANGER}; padding-top: 12px;"
        )
        layout.insertWidget(pos, header)
        pos += 1

        for err in errors:
            lbl = QLabel(f"  · {err}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")
            layout.insertWidget(pos, lbl)
            pos += 1

    def _on_error(self, msg: str) -> None:
        self._set_idle("Error")
        QMessageBox.critical(self, "Operation failed", msg)
