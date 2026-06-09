"""Pydantic data models for QuickNote.

Each model is a thin, validated data container.  They are used both as
return types from the database layer and as serialisation targets for the
settings file.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AppSettingsModel(BaseModel):
    """Persistent application settings.

    Stored as JSON in ``~/.quicknote/settings.json`` and read on every
    startup.  Fields default to ``None`` / sensible values so the file
    can be missing or empty without causing errors.

    Attributes:
        active_note_id (int | None): Database ID of the note currently
            open in the editor.  ``None`` when no note has been created
            yet or after the active note is deleted.
    """

    active_note_id: int | None = Field(
        default=None,
        title="Active Note ID",
    )


class NoteModel(BaseModel):
    """A single note record as returned from the database.

    Attributes:
        id (int): Auto-incremented primary key assigned by SQLite.
        content (str): Full plain-text content of the note.
        created_at (datetime): UTC timestamp when the note was first
            inserted into the database.
        updated_at (datetime): UTC timestamp of the most recent content
            update.
    """

    id: int = Field(..., title="Note ID")
    content: str = Field(..., title="Content of current note")
    created_at: datetime = Field(..., title="Note created at")
    updated_at: datetime = Field(..., title="Note updated at")
