"""Generate version_info.txt for PyInstaller from a semver string.

Usage:
    python scripts/make_version_info.py 1.2.3
"""

import re
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: make_version_info.py <version>  e.g. 1.2.3")

    version = sys.argv[1].lstrip("v")
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        sys.exit(f"Version must be MAJOR.MINOR.PATCH, got: {version!r}")

    major, minor, patch = int(m[1]), int(m[2]), int(m[3])

    content = f"""\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Himansu'),
           StringStruct(u'FileDescription', u'QuickNote - Minimal notepad for Windows'),
           StringStruct(u'FileVersion', u'{major}.{minor}.{patch}.0'),
           StringStruct(u'InternalName', u'QuickNote'),
           StringStruct(u'LegalCopyright', u'Copyright (c) 2026 Himansu'),
           StringStruct(u'OriginalFilename', u'QuickNote.exe'),
           StringStruct(u'ProductName', u'QuickNote'),
           StringStruct(u'ProductVersion', u'{major}.{minor}.{patch}.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [0x0409, 1200])])
  ]
)
"""

    out = Path("version_info.txt")
    out.write_text(content, encoding="utf-8")
    print(f"Written {out} for version {major}.{minor}.{patch}")


if __name__ == "__main__":
    main()
