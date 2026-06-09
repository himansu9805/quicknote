"""Tests for :mod:`quicknote.lib.models`."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from quicknote.lib.models import AppSettingsModel, NoteModel


class TestAppSettingsModel:
    def test_default_active_note_id_is_none(self):
        m = AppSettingsModel()
        assert m.active_note_id is None

    def test_accepts_integer_active_note_id(self):
        m = AppSettingsModel(active_note_id=5)
        assert m.active_note_id == 5

    def test_exclude_unset_omits_default_fields(self):
        m = AppSettingsModel()
        assert m.model_dump(exclude_unset=True) == {}

    def test_exclude_unset_includes_explicitly_set_none(self):
        m = AppSettingsModel(active_note_id=None)
        dumped = m.model_dump(exclude_unset=True)
        assert "active_note_id" in dumped
        assert dumped["active_note_id"] is None

    def test_exclude_unset_includes_explicit_integer(self):
        m = AppSettingsModel(active_note_id=10)
        dumped = m.model_dump(exclude_unset=True)
        assert dumped == {"active_note_id": 10}

    def test_model_copy_merges_partial_update(self):
        base = AppSettingsModel(active_note_id=1)
        updated = base.model_copy(update={"active_note_id": 99})
        assert updated.active_note_id == 99

    def test_rejects_non_integer_active_note_id(self):
        with pytest.raises(ValidationError):
            AppSettingsModel(active_note_id="not-an-int")


class TestNoteModel:
    def test_accepts_datetime_objects(self):
        now = datetime.now()
        note = NoteModel(id=1, content="hello", created_at=now, updated_at=now)
        assert note.created_at == now

    def test_parses_datetime_string(self):
        note = NoteModel(
            id=1,
            content="test",
            created_at="2026-01-15 10:30:00",
            updated_at="2026-01-15 10:30:00",
        )
        assert isinstance(note.created_at, datetime)
        assert note.created_at.year == 2026

    def test_content_is_preserved_exactly(self):
        text = "Line 1\nLine 2\n  indented"
        note = NoteModel(
            id=1,
            content=text,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert note.content == text

    def test_raises_on_missing_content(self):
        with pytest.raises(ValidationError):
            NoteModel(id=1, created_at=datetime.now(), updated_at=datetime.now())

    def test_raises_on_missing_timestamps(self):
        with pytest.raises(ValidationError):
            NoteModel(id=1, content="text")

    def test_raises_on_invalid_datetime_string(self):
        with pytest.raises(ValidationError):
            NoteModel(
                id=1,
                content="text",
                created_at="not-a-date",
                updated_at="not-a-date",
            )
