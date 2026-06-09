"""SQLite persistence layer for QuickNote.

Provides a thin wrapper around the ``notes`` table, exposing typed CRUD
operations backed by :mod:`quicknote.lib.models`.
"""

import sqlite3
from datetime import datetime

from quicknote import const
from quicknote.lib import models


class Database:
    """Manages the SQLite connection and all note-related queries.

    The connection is opened in ``__init__`` and kept open for the
    lifetime of the object.  Call :meth:`close` explicitly when the
    application shuts down to flush any pending writes.

    Attributes:
        connect (sqlite3.Connection): Active connection to the SQLite
            database file at :data:`~quicknote.const.SQLITE_DATABASE_PATH`.
        cursor (sqlite3.Cursor): Cursor used for executing all queries.
    """

    def __init__(self) -> None:
        """Open the database connection and create the schema if absent."""
        self.connect = sqlite3.connect(str(const.SQLITE_DATABASE_PATH))
        self.cursor = self.connect.cursor()
        self._create_table()

    def _create_table(self):
        """Create the ``notes`` table if it does not already exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        self.connect.commit()

    def create_note(self, content: str) -> int | None:
        """Insert a new note and return its generated ID.

        Args:
            content (str): Plain-text body of the note.

        Returns:
            int | None: The ``ROWID`` / primary key of the newly inserted
            row, or ``None`` if the insert did not produce a row ID.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO notes(content, created_at, updated_at) VALUES (?, ?, ?)",
            (content, timestamp, timestamp),
        )
        self.connect.commit()
        return self.cursor.lastrowid

    def read_note_by_id(self, id: int) -> models.NoteModel:
        """Fetch a single note by its primary key.

        Args:
            id (int): Primary key of the note to retrieve.

        Returns:
            models.NoteModel: The matching note record.

        Raises:
            Exception: If no row with the given ``id`` exists.
        """
        self.cursor.execute("SELECT * FROM notes WHERE id = ?", (id,))
        result = self.cursor.fetchone()
        if result is None:
            raise Exception("Note ID not found.")
        return models.NoteModel(
            id=result[0],
            content=result[1],
            created_at=result[2],
            updated_at=result[3],
        )

    def list_notes(self) -> list[models.NoteModel]:
        """Return all notes ordered by most-recently updated first.

        Returns:
            list[models.NoteModel]: Every note in the database, sorted
            descending by ``updated_at``.  Returns an empty list when
            no notes exist.
        """
        self.cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
        results = self.cursor.fetchall()
        return [
            models.NoteModel(id=r[0], content=r[1], created_at=r[2], updated_at=r[3])
            for r in results
        ]

    def update_note(self, id: int, new_content: str) -> None:
        """Overwrite the content of an existing note and refresh its timestamp.

        Args:
            id (int): Primary key of the note to update.
            new_content (str): Replacement plain-text body.

        Raises:
            Exception: If no row with the given ``id`` exists.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "UPDATE notes SET content = ?, updated_at = ? WHERE id = ?",
            (new_content, timestamp, id),
        )
        self.connect.commit()
        if self.cursor.rowcount == 0:
            raise Exception("Note ID not found.")

    def delete_note(self, id: int) -> None:
        """Permanently remove a note from the database.

        Args:
            id (int): Primary key of the note to delete.

        Raises:
            Exception: If no row with the given ``id`` exists.
        """
        self.cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
        self.connect.commit()
        if self.cursor.rowcount == 0:
            raise Exception("Note ID not found.")

    def close(self) -> None:
        """Close the underlying SQLite connection.

        Should be called once when the application exits to ensure all
        pending transactions are flushed to disk.
        """
        self.connect.close()
