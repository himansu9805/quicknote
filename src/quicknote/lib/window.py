"""Main application window for QuickNote.

Defines :class:`QuickNoteWindow`, the single frameless, always-on-top
editor window.  It owns the system-tray icon, the auto-save timer, and
all note-management actions exposed through the hamburger menu.
"""

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from quicknote import const
from quicknote.lib import models
from quicknote.lib.app_settings import AppSettings
from quicknote.lib.database import Database
from quicknote.lib.icon_manager import Icons, get_icon
from quicknote.lib.signals import HotkeySignals


class QuickNoteWindow(QMainWindow):
    """Frameless floating note editor with system-tray integration.

    The window is always on top and uses a frameless hint so it can be
    styled and dragged freely.  Notes are persisted automatically every
    three seconds via an internal ``QTimer``.

    Args:
        signals (HotkeySignals): Shared signal bus used to receive the
            global hotkey toggle event from the background listener
            thread.

    Attributes:
        database (Database): Database connection used for all note CRUD
            operations.
        app_settings (AppSettings): In-memory settings wrapper that
            tracks which note is currently active.
        signals (HotkeySignals): The signal bus passed in at construction.
        dragging (bool): ``True`` while the user is dragging the window.
        drag_pos (QPoint): Cursor-to-window-origin offset recorded when a
            drag gesture begins.
        menu_btn (QPushButton): Hamburger button that opens the action
            menu.
        btn_hide (QPushButton): Close button that hides the window to
            the tray.
        editor (QTextEdit): Main text-editing widget.
        lbl_char_count (QLabel): Status-bar label showing character count.
        lbl_saved (QLabel): Status-bar label showing save state.
        tray (QSystemTrayIcon): System-tray icon for background presence.
    """

    def __init__(self, signals: HotkeySignals) -> None:
        """Initialise the window, tray, signals, styles, and auto-save timer.

        Args:
            signals (HotkeySignals): Shared signal bus for the global
                hotkey toggle event.
        """
        super().__init__()

        self.database = Database()
        self.app_settings = AppSettings()

        self.signals = signals
        self.dragging = False
        self.drag_pos = QPoint()
        self._build_ui()
        self._build_tray()
        self._connect_signals()
        self._apply_styles()
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start(3000)

    def _build_ui(self) -> None:
        """Construct and arrange all child widgets.

        Builds three vertical regions: a title bar (hamburger button,
        app name, hotkey hint, hide button), the text editor, and a
        status bar (character count, save indicator).
        """
        self.setWindowTitle(const.APP_NAME)
        self.setFixedSize(const.WINDOW_WIDTH, const.WINDOW_HEIGHT)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Title bar
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(38)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(14, 0, 8, 0)

        menu_icon = get_icon(icon=Icons.HAMBURGER, color=const.TEXT_COLOR)
        self.menu_btn = QPushButton("")
        self.menu_btn.setIcon(menu_icon)
        self.menu_btn.setIconSize(QSize(20, 20))
        self.menu_btn.setObjectName("hideButton")
        self.menu_btn.setFixedSize(24, 24)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        lbl = QLabel(const.APP_NAME)
        lbl.setObjectName("titleLabel")

        hint = QLabel(f"{const.HOTKEY} to toggle")
        hint.setObjectName("hintLabel")

        self.btn_hide = QPushButton("")
        self.btn_hide.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        )
        self.btn_hide.setObjectName("hideButton")
        self.btn_hide.setFixedSize(24, 24)
        self.btn_hide.setCursor(Qt.CursorShape.PointingHandCursor)

        tb_layout.addWidget(self.menu_btn)
        tb_layout.addWidget(lbl)
        tb_layout.addWidget(hint)
        tb_layout.addStretch()
        tb_layout.addWidget(self.btn_hide)

        # Text area
        self.editor = QTextEdit()
        self.editor.setObjectName("editor")
        self.editor.setPlaceholderText("Type your notes here... (auto-saved)")
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor.setText(self._load_note())

        # Status bar
        status_bar = QWidget()
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(26)
        sb_layout = QHBoxLayout(status_bar)
        sb_layout.setContentsMargins(10, 0, 14, 0)

        self.lbl_char_count = QLabel("0 characters")
        self.lbl_char_count.setObjectName("char_count_label")
        self.lbl_saved = QLabel("saved ✓")
        self.lbl_saved.setObjectName("savedLabel")

        sb_layout.addWidget(self.lbl_char_count)
        sb_layout.addStretch()
        sb_layout.addWidget(self.lbl_saved)

        root.addWidget(title_bar)
        root.addWidget(self.editor)
        root.addWidget(status_bar)

        self._update_char_count()

    def _build_tray(self) -> None:
        """Create the system-tray icon and its context menu."""
        icon = QIcon(str(const.APP_ICON_PATH))
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip(f"{const.APP_NAME} - {const.HOTKEY.upper()} to toggle")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background:#2A2A3E; color:#CDD6F4;
                border:1px solid #45475A; border-radius:6px; padding:4px;
            }
            QMenu::item { padding:6px 20px; border-radius:4px; }
            QMenu::item:selected { background:#6C63FF; }
        """)
        act_show = menu.addAction("Show / Hide")
        act_clear = menu.addAction("Clear notes")
        menu.addSeparator()
        act_quit = menu.addAction("Quit")

        act_show.triggered.connect(self._toggle_visibility)
        act_clear.triggered.connect(self._clear_notes)
        act_quit.triggered.connect(self._quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _connect_signals(self) -> None:
        """Wire all button clicks, signals, and keyboard shortcuts to slots."""
        self.btn_hide.clicked.connect(self._hide)
        self.menu_btn.clicked.connect(self._show_menu)
        self.signals.triggered.connect(self._toggle_visibility)
        self.editor.textChanged.connect(self._on_text_changed)

        QShortcut(QKeySequence("Escape"), self).activated.connect(self._hide)

    def _apply_styles(self) -> None:
        """Apply the application-wide dark-theme stylesheet."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: transparent;
            }}
            QWidget#centralwidget, QWidget {{
                background: transparent;
            }}
            /* Title bar */
            QWidget#titleBar {{
                background: {const.BG_COLOR};
                border-bottom: 1px solid {const.BORDER_COLOR};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            QLabel#dot {{
                color: {const.ACCENT};
                font-size: 10px;
                margin-right: 2px;
            }}
            QLabel#titleLabel {{
                color: {const.TEXT_COLOR};
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
            }}
            QLabel#hintLabel {{
                color: {const.PLACEHOLDER};
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
            QPushButton#closeBtn {{
                background: transparent;
                color: {const.PLACEHOLDER};
                border: none;
                font-size: 13px;
                border-radius: 12px;
            }}
            QPushButton#closeBtn:hover {{
                background: #FF5555;
                color: white;
            }}
            /* Editor */
            QTextEdit#editor {{
                background: {const.TEXT_BG};
                color: {const.TEXT_COLOR};
                border: none;
                font-family: 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                padding: 12px 14px;
                selection-background-color: {const.ACCENT};
            }}
            QScrollBar:vertical {{
                background: {const.TEXT_BG};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {const.BORDER_COLOR};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            /* Status bar */
            QWidget#statusBar {{
                background: {const.BG_COLOR};
                border-top: 1px solid {const.BORDER_COLOR};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
            QLabel#statusLabel {{
                color: {const.PLACEHOLDER};
                font-family: 'Segoe UI';
                font-size: 10px;
            }}
        """)

    # Visibility helpers
    def _show_centered(self) -> None:
        """Move the window to the centre of the primary screen and show it."""
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - const.WINDOW_WIDTH) // 2
        y = (screen.height() - const.WINDOW_HEIGHT) // 2
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
        self.editor.setFocus()

    def _hide(self) -> None:
        """Auto-save the current note and hide the window to the tray."""
        self._auto_save()
        self.hide()

    def _toggle_visibility(self) -> None:
        """Show the window if hidden; hide it if currently visible."""
        if self.isVisible():
            self._hide()
        else:
            self._show_centered()

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Toggle window visibility on a single left-click of the tray icon.

        Args:
            reason (QSystemTrayIcon.ActivationReason): The interaction
                type reported by Qt.  Only ``Trigger`` (single click) is
                handled; other reasons are ignored.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_visibility()

    # Editor state
    def _on_text_changed(self) -> None:
        """Update the character counter and mark the note as unsaved."""
        self._update_char_count()
        self.lbl_saved.setText("unsaved...")
        self.lbl_saved.setStyleSheet(f"color: {const.PLACEHOLDER};")

    def _update_char_count(self) -> None:
        """Refresh the character-count label from the current editor text."""
        text = self.editor.toPlainText()
        count = len(text)
        self.lbl_char_count.setText(f"{count} character{'s' if count != 1 else ''}")

    def _auto_save(self) -> None:
        """Persist the current editor content and mark the note as saved."""
        self._save_note()
        self.lbl_saved.setText("saved ✓")
        self.lbl_saved.setStyleSheet("color: #A6E3A1;")

    def _clear_notes(self) -> None:
        """Clear the editor and immediately save the (now empty) note."""
        self.editor.clear()
        self._auto_save()

    def _quit(self) -> None:
        """Save the current note, remove the tray icon, and exit the app."""
        self._auto_save()
        self.tray.hide()
        QApplication.quit()

    # Mouse drag (frameless window movement)
    def mousePressEvent(self, event) -> None:
        """Begin tracking a window-drag gesture on left-button press.

        Args:
            event: The Qt mouse-press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event) -> None:
        """Move the window while a left-button drag is in progress.

        Args:
            event: The Qt mouse-move event.
        """
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        """End the window-drag gesture on mouse button release.

        Args:
            event: The Qt mouse-release event.
        """
        self.dragging = False

    # Hamburger menu
    def _show_menu(self) -> None:
        """Build and display the hamburger action menu below the menu button.

        Menu items:

        * **+ New Note** — saves the current note and opens a blank one.
        * **Older Notes** — submenu listing all other saved notes.
        * **Delete This Note** — deletes the active note and clears the editor.
        * **Exit** — saves and quits the application.
        """
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {const.BG_COLOR};
                color: {const.TEXT_COLOR};
                border: 1px solid {const.BORDER_COLOR};
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QMenu::item {{
                padding: 7px 18px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background: {const.ACCENT};
                color: #FFFFFF;
            }}
            QMenu::item:disabled {{
                color: {const.PLACEHOLDER};
            }}
            QMenu::separator {{
                height: 1px;
                background: {const.BORDER_COLOR};
                margin: 3px 6px;
            }}
            QMenu::right-arrow {{
                image: none;
                width: 6px;
            }}
        """)

        act_new = menu.addAction("+ New Note")
        act_new.triggered.connect(self._new_note)

        older_menu = menu.addMenu("Older Notes")
        older_menu.setStyleSheet(menu.styleSheet())
        self._populate_older_notes_menu(older_menu)

        menu.addSeparator()

        act_delete = menu.addAction("Delete This Note")
        act_delete.triggered.connect(self._delete_current_note)

        menu.addSeparator()

        act_exit = menu.addAction("Exit")
        act_exit.triggered.connect(self._quit)

        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def _populate_older_notes_menu(self, submenu: QMenu) -> None:
        """Fill ``submenu`` with an action for every note except the active one.

        Each action label shows a 40-character content preview and the
        note's last-updated timestamp.  If no other notes exist, a
        disabled placeholder item is added instead.

        Args:
            submenu (QMenu): The submenu widget to populate in-place.
        """
        active_id = self.app_settings.options.active_note_id
        all_notes = self.database.list_notes()
        older = [n for n in all_notes if n.id != active_id]
        if not older:
            no_act = submenu.addAction("No other notes")
            no_act.setEnabled(False)
            return
        for note in older:
            preview = note.content.replace("\n", " ").strip()[:40]
            if len(note.content) > 40:
                preview += "…"
            label = (
                f"{preview or '(empty note)'}  ·  "
                f"{note.updated_at.strftime('%b %d, %H:%M')}"
            )
            act = submenu.addAction(label)
            act.triggered.connect(
                lambda checked=False, nid=note.id: self._switch_note(nid)
            )

    # Note management actions
    def _new_note(self) -> None:
        """Save the current note and switch the editor to a new blank note.

        Sets ``active_note_id`` to ``None`` in settings so the next
        auto-save creates a fresh database row.  Editor signals are
        blocked during the clear to suppress the "unsaved…" indicator.
        """
        self._auto_save()
        self.app_settings.update_settings_file(
            partial_settings=models.AppSettingsModel(active_note_id=None)
        )
        self.app_settings.read_settings_file()
        self.editor.blockSignals(True)
        self.editor.clear()
        self.editor.blockSignals(False)
        self._update_char_count()
        self.lbl_saved.setText("new note")
        self.lbl_saved.setStyleSheet(f"color: {const.ACCENT};")

    def _switch_note(self, note_id: int) -> None:
        """Save the current note and load a different note into the editor.

        Args:
            note_id (int): Primary key of the note to switch to.
        """
        self._auto_save()
        note = self.database.read_note_by_id(id=note_id)
        self.app_settings.update_settings_file(
            partial_settings=models.AppSettingsModel(active_note_id=note_id)
        )
        self.app_settings.read_settings_file()
        self.editor.blockSignals(True)
        self.editor.setText(note.content)
        self.editor.blockSignals(False)
        self._update_char_count()
        self.lbl_saved.setText("saved ✓")
        self.lbl_saved.setStyleSheet("color: #A6E3A1;")

    def _delete_current_note(self) -> None:
        """Delete the active note from the database and clear the editor.

        After deletion ``active_note_id`` is set to ``None`` so the next
        auto-save will create a new note if the user starts typing.
        """
        active_id = self.app_settings.options.active_note_id
        if active_id is not None:
            self.database.delete_note(id=active_id)
        self.app_settings.update_settings_file(
            partial_settings=models.AppSettingsModel(active_note_id=None)
        )
        self.app_settings.read_settings_file()
        self.editor.blockSignals(True)
        self.editor.clear()
        self.editor.blockSignals(False)
        self._update_char_count()
        self.lbl_saved.setText("note deleted")
        self.lbl_saved.setStyleSheet(f"color: {const.PLACEHOLDER};")

    # Persistence helpers
    def _load_note(self) -> str:
        """Return the content of the active note, or an empty string.

        Returns:
            str: Content of the note identified by
            ``app_settings.options.active_note_id``, or ``""`` when no
            active note ID is set.
        """
        if self.app_settings.options.active_note_id is None:
            return ""
        active_note = self.database.read_note_by_id(
            id=self.app_settings.options.active_note_id
        )
        return active_note.content

    def _save_note(self) -> None:
        """Persist the current editor content to the database.

        If no active note exists (``active_note_id`` is ``None``), a new
        row is created and the settings file is updated with the new ID.
        Otherwise the existing row is updated in-place.
        """
        content = self.editor.toPlainText()
        if self.app_settings.options.active_note_id is None:
            active_note_id = self.database.create_note(content=content)
            self.app_settings.update_settings_file(
                partial_settings=models.AppSettingsModel(active_note_id=active_note_id)
            )
        else:
            self.database.update_note(
                id=self.app_settings.options.active_note_id, new_content=content
            )
        self.app_settings.read_settings_file()
