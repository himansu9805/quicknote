# QuickNote

A minimal, always-available notepad for Windows.
Lives in the system tray. Pops up with a hotkey. Stays out of your way.

---

## Features

- **Global hotkey** `Ctrl+Shift+Q` — show or hide the window from anywhere on the desktop
- **Multiple notes** — create, switch between, and delete notes from the hamburger menu
- **Auto-save** — editor content is saved to SQLite every 3 seconds automatically
- **System tray icon** — runs silently in the background; right-click for quick actions
- **Frameless floating window** — drag it anywhere on screen
- **`Esc`** — instantly dismiss the window back to the tray
- Dark theme with a clean, minimal UI

---

## Requirements

- Windows 10 or 11
- Python 3.14
- [Poetry](https://python-poetry.org/) (dependency and environment manager)

> **Administrator privileges required** — the `keyboard` library needs elevated
> permissions to register global hotkeys that work across all applications.
> Right-click your terminal and choose **"Run as Administrator"** before running
> the commands below.

---

## Installation

```powershell
# 1. Clone or download the repository
cd quicknote

# 2. Install dependencies into an isolated virtual environment
poetry install

# 3. Run the application
poetry run python -m quicknote.main
```

---

## Run on Windows Startup (optional)

To start QuickNote automatically with Windows:

1. Press `Win+R`, type `shell:startup`, press **Enter**.
2. Create a file named `start_quicknote.bat` in the startup folder:

```bat
@echo off
cd /d "C:\path\to\quicknote"
poetry run pythonw -m quicknote.main
```

3. Save and close. QuickNote will launch silently on the next login.

---

## Usage

| Action | How |
|---|---|
| Show / Hide window | `Ctrl+Shift+Q` or click the tray icon |
| Hide window | `Esc` or the × button |
| Open action menu | Click the ☰ (hamburger) button |
| New note | Menu → **+ New Note** |
| Switch to another note | Menu → **Older Notes** → select a note |
| Delete current note | Menu → **Delete This Note** |
| Exit application | Menu → **Exit** or right-click tray → **Quit** |

---

## Data storage

All user data is written to `~/.quicknote/` (`C:\Users\<YourName>\.quicknote\`):

| File | Contents |
|---|---|
| `data.db` | SQLite database containing all notes |
| `settings.json` | Lightweight settings (e.g. the active note ID) |

---

## Project structure

```
src/quicknote/
├── main.py              # Entry point — Qt app, hotkey thread
├── const.py             # Application-wide constants and paths
└── lib/
    ├── app_settings.py  # Settings file read/write
    ├── database.py      # SQLite CRUD layer
    ├── icon_manager.py  # Dynamic SVG icon colourisation
    ├── models.py        # Pydantic data models
    ├── signals.py       # Qt signal definitions
    └── window.py        # Main window and all UI logic
```

---

## License

MIT — see [LICENSE](LICENSE).
