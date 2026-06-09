"""Shared pytest fixtures for the QuickNote test suite.

Fixtures patch the module-level path constants so that every test runs
against temporary files in pytest's ``tmp_path`` directory and never
touches the real ``~/.quicknote/`` user data.
"""

import pytest

from quicknote import const
from quicknote.lib.database import Database


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Yield a :class:`~quicknote.lib.database.Database` backed by a temp file.

    Patches :data:`quicknote.const.SQLITE_DATABASE_PATH` for the duration
    of the test and closes the connection on teardown.
    """
    monkeypatch.setattr(const, "SQLITE_DATABASE_PATH", tmp_path / "test.db")
    database = Database()
    yield database
    database.close()


@pytest.fixture
def settings_env(tmp_path, monkeypatch):
    """Patch settings paths to a temporary directory.

    Patches both :data:`quicknote.const.APP_FILES_PATH` and
    :data:`quicknote.const.SETTINGS_FILE_PATH` so tests never read or
    write the real user settings file.

    Returns:
        pathlib.Path: The temporary directory acting as ``APP_FILES_PATH``.
    """
    monkeypatch.setattr(const, "APP_FILES_PATH", tmp_path)
    monkeypatch.setattr(const, "SETTINGS_FILE_PATH", tmp_path / "settings.json")
    return tmp_path
