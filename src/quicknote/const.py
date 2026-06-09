"""Application-wide constants for QuickNote.

All file-system paths, UI dimensions, colour tokens, and behavioural
parameters are defined here so they can be imported from a single
location rather than scattered across the codebase.
"""

from pathlib import Path

# File-system paths
APP_FILES_PATH = Path.home() / ".quicknote"
"""Root directory for all user data written by the application."""

SQLITE_DATABASE_PATH = APP_FILES_PATH / "data.db"
"""SQLite database file that stores note records."""

SETTINGS_FILE_PATH = APP_FILES_PATH / "settings.json"
"""JSON file that persists lightweight application settings."""

ASSETS_PATH = Path(__file__).parent / "assets"
"""Directory containing bundled static assets (icons, images)."""

APP_ICON_PATH = ASSETS_PATH / "app_icon.png"
"""Path to the PNG used as the application and system-tray icon."""

ICONS_DIRECTORY_PATH = ASSETS_PATH / "icons"
"""Directory containing SVG icon templates used by :mod:`icon_manager`."""

# Application metadata
APP_NAME = "QuickNote"
"""Human-readable application name shown in the title bar and tray."""

HOTKEY = "ctrl+shift+q"
"""Global hotkey combination that toggles the main window."""

# Window geometry
WINDOW_WIDTH = 400
"""Fixed width of the main window in pixels."""

WINDOW_HEIGHT = 300
"""Fixed height of the main window in pixels."""

# Theme colours  (Catppuccin-inspired dark palette)
ACCENT = "#6C63FF"
"""Purple accent colour used for selections and highlights."""

BG_COLOR = "#1E1E2E"
"""Primary surface colour for the title bar and status bar."""

TEXT_BG = "#2A2A3E"
"""Background colour for the text-editor area."""

TEXT_COLOR = "#CDD6F4"
"""Default foreground colour for body text."""

BORDER_COLOR = "#45475A"
"""Subtle border and divider colour."""

PLACEHOLDER = "#6C7086"
"""Muted colour used for placeholder text and secondary labels."""
