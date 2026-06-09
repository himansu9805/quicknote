"""Dynamic SVG icon loading and colourisation for QuickNote.

SVG templates stored under :data:`~quicknote.const.ICONS_DIRECTORY_PATH`
are expected to contain a ``{color}`` placeholder that is substituted at
runtime, allowing the same source file to be recoloured without keeping
multiple copies on disk.
"""

from enum import Enum

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QIcon, QPixmap

from quicknote import const


class Icons(Enum):
    """Registry of available icon names.

    Each member's value is the stem of an SVG file located in
    :data:`~quicknote.const.ICONS_DIRECTORY_PATH`.

    Attributes:
        HAMBURGER (str): Three-line menu icon used in the title bar.
    """

    HAMBURGER = "hamburger"


def get_icon(icon: Icons, color: str = "#000000") -> QIcon:
    """Load an SVG icon template and return it colourised as a ``QIcon``.

    The SVG file is read from disk, the ``{color}`` placeholder is
    replaced with ``color``, and the result is rasterised into a
    ``QPixmap`` before being wrapped in a ``QIcon``.

    Args:
        icon (Icons): Enum member identifying which SVG file to load.
        color (str): CSS hex colour string (e.g. ``"#CDD6F4"``) to
            substitute into the SVG template.  Defaults to black.

    Returns:
        QIcon: The colourised icon ready for use in Qt widgets.  Returns
        an empty ``QIcon`` if the SVG file is missing or empty.
    """
    with open(
        str(const.ICONS_DIRECTORY_PATH / f"{icon.value}.svg"), encoding="utf-8"
    ) as file:
        template = file.read()

    if not template:
        print(f"Warning: Icon '{icon.value}' not found in mapping registry.")
        return QIcon()

    formatted_svg = template.format(color=color)
    byte_array = QByteArray(formatted_svg.encode("utf-8"))
    pixmap = QPixmap()
    pixmap.loadFromData(byte_array)
    return QIcon(pixmap)
