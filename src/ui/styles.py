"""Centralized dark‑theme stylesheet for Smart File Organizer."""

from __future__ import annotations

# ── colour palette ──────────────────────────────────────────────────
BG_DARK = "#0d1117"
BG_PANEL = "#161b22"
BG_CARD = "#1c2333"
BG_CARD_HOVER = "#242d3d"
BG_INPUT = "#0d1117"
BORDER = "#30363d"
ACCENT = "#58a6ff"
ACCENT_HOVER = "#79c0ff"
ACCENT_PRESSED = "#388bfd"
DANGER = "#f85149"
SUCCESS = "#3fb950"
WARNING = "#d29922"
TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
TEXT_MUTED = "#6e7681"

# ── category colours ────────────────────────────────────────────────
CATEGORY_COLOURS: dict[str, str] = {
    "Images": "#f778ba",
    "Videos": "#bc8cff",
    "Documents": "#58a6ff",
    "Code": "#3fb950",
    "Others": "#d29922",
}

# ── category icons (Unicode) ────────────────────────────────────────
CATEGORY_ICONS: dict[str, str] = {
    "Images": "🖼️",
    "Videos": "🎬",
    "Documents": "📄",
    "Code": "💻",
    "Others": "📦",
}


def app_stylesheet() -> str:
    """Return the full QSS stylesheet for the application."""
    return f"""
    /* ── global ───────────────────────────────────────── */
    * {{
        font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
        color: {TEXT_PRIMARY};
    }}
    QMainWindow, QWidget#CentralWidget {{
        background: {BG_DARK};
    }}

    /* ── left panel ───────────────────────────────────── */
    QWidget#LeftPanel {{
        background: {BG_PANEL};
        border-right: 1px solid {BORDER};
        border-radius: 0px;
    }}

    /* ── right panel ──────────────────────────────────── */
    QWidget#RightPanel {{
        background: {BG_DARK};
    }}

    /* ── section labels ───────────────────────────────── */
    QLabel#SectionTitle {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        color: {TEXT_MUTED};
        padding-top: 8px;
    }}
    QLabel#AppTitle {{
        font-size: 22px;
        font-weight: 800;
        color: {TEXT_PRIMARY};
    }}
    QLabel#AppSubtitle {{
        font-size: 12px;
        color: {TEXT_SECONDARY};
    }}
    QLabel#StatusLabel {{
        font-size: 12px;
        color: {TEXT_SECONDARY};
        padding: 4px 0;
    }}
    QLabel#PathDisplay {{
        font-size: 12px;
        color: {ACCENT};
        padding: 2px 0;
    }}
    QLabel#ResultTitle {{
        font-size: 18px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
    }}
    QLabel#PlaceholderLabel {{
        font-size: 14px;
        color: {TEXT_MUTED};
    }}

    /* ── line edit (folder input) ─────────────────────── */
    QLineEdit {{
        background: {BG_INPUT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: {TEXT_PRIMARY};
    }}
    QLineEdit:focus {{
        border: 1px solid {ACCENT};
    }}

    /* ── primary button ───────────────────────────────── */
    QPushButton#PrimaryButton {{
        background: {ACCENT};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton#PrimaryButton:hover {{
        background: {ACCENT_HOVER};
    }}
    QPushButton#PrimaryButton:pressed {{
        background: {ACCENT_PRESSED};
    }}
    QPushButton#PrimaryButton:disabled {{
        background: {BORDER};
        color: {TEXT_MUTED};
    }}

    /* ── action buttons ───────────────────────────────── */
    QPushButton#ActionButton {{
        background: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 600;
        text-align: left;
    }}
    QPushButton#ActionButton:hover {{
        background: {BG_CARD_HOVER};
        border: 1px solid {ACCENT};
    }}
    QPushButton#ActionButton:pressed {{
        background: {ACCENT_PRESSED};
    }}
    QPushButton#ActionButton:disabled {{
        background: {BG_PANEL};
        color: {TEXT_MUTED};
        border: 1px solid {BORDER};
    }}

    /* ── danger button ────────────────────────────────── */
    QPushButton#DangerButton {{
        background: {BG_CARD};
        color: {DANGER};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 600;
        text-align: left;
    }}
    QPushButton#DangerButton:hover {{
        background: {BG_CARD_HOVER};
        border: 1px solid {DANGER};
    }}
    QPushButton#DangerButton:pressed {{
        background: {DANGER};
        color: #ffffff;
    }}
    QPushButton#DangerButton:disabled {{
        background: {BG_PANEL};
        color: {TEXT_MUTED};
        border: 1px solid {BORDER};
    }}

    /* ── scroll area ──────────────────────────────────── */
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: {BG_DARK};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ── category card ────────────────────────────────── */
    QFrame#CategoryCard {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}
    QFrame#CategoryCard:hover {{
        background: {BG_CARD_HOVER};
        border: 1px solid {TEXT_MUTED};
    }}

    /* ── preview table ────────────────────────────────── */
    QFrame#PreviewCard {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}
    QLabel#PreviewFile {{
        font-size: 12px;
        color: {TEXT_SECONDARY};
    }}
    QLabel#PreviewArrow {{
        font-size: 12px;
        color: {TEXT_MUTED};
    }}
    QLabel#PreviewCategory {{
        font-size: 12px;
        font-weight: 600;
    }}
    """
