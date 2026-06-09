"""Tests for :mod:`quicknote.lib.database`."""

import time

import pytest

from quicknote.lib.database import Database


class TestCreateNote:
    def test_returns_integer_id(self, db: Database):
        note_id = db.create_note("Hello")
        assert isinstance(note_id, int)
        assert note_id >= 1

    def test_ids_are_unique(self, db: Database):
        id1 = db.create_note("First")
        id2 = db.create_note("Second")
        assert id1 != id2

    def test_empty_content_is_accepted(self, db: Database):
        note_id = db.create_note("")
        assert note_id is not None


class TestReadNoteById:
    def test_returns_correct_content(self, db: Database):
        note_id = db.create_note("Test content")
        note = db.read_note_by_id(note_id)
        assert note.content == "Test content"
        assert note.id == note_id

    def test_timestamps_are_populated(self, db: Database):
        note_id = db.create_note("timestamped")
        note = db.read_note_by_id(note_id)
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_raises_when_id_not_found(self, db: Database):
        with pytest.raises(Exception, match="Note ID not found"):
            db.read_note_by_id(9999)


class TestListNotes:
    def test_returns_empty_list_when_no_notes(self, db: Database):
        assert db.list_notes() == []

    def test_returns_all_created_notes(self, db: Database):
        db.create_note("Alpha")
        db.create_note("Beta")
        db.create_note("Gamma")
        notes = db.list_notes()
        assert len(notes) == 3

    def test_ordered_by_updated_at_descending(self, db: Database):
        id1 = db.create_note("Older")
        time.sleep(1)
        db.create_note("Newer")
        notes = db.list_notes()
        assert notes[0].updated_at >= notes[1].updated_at
        assert notes[1].id == id1


class TestUpdateNote:
    def test_content_is_changed(self, db: Database):
        note_id = db.create_note("Original")
        db.update_note(note_id, "Updated")
        note = db.read_note_by_id(note_id)
        assert note.content == "Updated"

    def test_updated_at_is_refreshed(self, db: Database):
        note_id = db.create_note("Before")
        before = db.read_note_by_id(note_id).updated_at
        time.sleep(1)
        db.update_note(note_id, "After")
        after = db.read_note_by_id(note_id).updated_at
        assert after > before

    def test_raises_when_id_not_found(self, db: Database):
        with pytest.raises(Exception, match="Note ID not found"):
            db.update_note(9999, "content")


class TestDeleteNote:
    def test_note_no_longer_readable_after_delete(self, db: Database):
        note_id = db.create_note("To delete")
        db.delete_note(note_id)
        with pytest.raises(Exception, match="Note ID not found"):
            db.read_note_by_id(note_id)

    def test_delete_reduces_list_count(self, db: Database):
        id1 = db.create_note("Keep")
        id2 = db.create_note("Remove")
        db.delete_note(id2)
        notes = db.list_notes()
        assert len(notes) == 1
        assert notes[0].id == id1

    def test_raises_when_id_not_found(self, db: Database):
        with pytest.raises(Exception, match="Note ID not found"):
            db.delete_note(9999)
