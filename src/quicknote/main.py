"""Entry point for the QuickNote application.

Initialises the Qt application, registers the global hotkey in a daemon
thread, and shows the main window on first launch.
"""

import sys
import threading

import keyboard
from PySide6.QtWidgets import QApplication

from quicknote import const
from quicknote.lib.signals import HotkeySignals
from quicknote.lib.window import QuickNoteWindow


def main():
    """Start the QuickNote application.

    Creates the ``QApplication``, builds the main window, registers the
    global hotkey listener in a background daemon thread, and enters the
    Qt event loop.  The process exits with the event-loop's return code.
    """
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(const.APP_NAME)

    signals = HotkeySignals()
    window = QuickNoteWindow(signals)

    def register_hotkey():
        """Register the global hotkey and block until the process exits.

        Runs in a daemon thread so it does not prevent clean shutdown.
        Emits ``signals.triggered`` on the Qt event loop via a thread-safe
        signal whenever the configured hotkey combination is pressed.
        """
        keyboard.add_hotkey(const.HOTKEY, lambda: signals.triggered.emit())
        keyboard.wait()

    t = threading.Thread(target=register_hotkey, daemon=True)
    t.start()

    window._show_centered()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
