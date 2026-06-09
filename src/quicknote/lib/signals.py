"""Qt signal definitions shared across the QuickNote application.

Centralising signals in a dedicated ``QObject`` subclass allows them to
be passed to components that live on different threads without coupling
those components to each other directly.
"""

from PySide6.QtCore import QObject, Signal


class HotkeySignals(QObject):
    """Container for application-wide Qt signals.

    Attributes:
        triggered (Signal): Emitted by the global hotkey listener thread
            whenever the configured hotkey combination is pressed.  Slots
            connected to this signal run on the Qt event loop via Qt's
            automatic queued-connection mechanism.
    """

    triggered = Signal()
