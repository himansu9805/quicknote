"""Tests for :mod:`quicknote.lib.app_settings`."""

import json

from quicknote.lib.app_settings import AppSettings
from quicknote.lib.models import AppSettingsModel


class TestReadSettingsFile:
    def test_creates_default_file_when_missing(self, settings_env):
        settings = AppSettings()
        assert settings.options.active_note_id is None
        assert (settings_env / "settings.json").exists()

    def test_written_file_is_valid_json(self, settings_env):
        AppSettings()
        data = json.loads((settings_env / "settings.json").read_text())
        assert isinstance(data, dict)

    def test_reads_existing_active_note_id(self, settings_env):
        (settings_env / "settings.json").write_text(json.dumps({"active_note_id": 42}))
        settings = AppSettings()
        assert settings.options.active_note_id == 42

    def test_resets_on_corrupt_json(self, settings_env):
        (settings_env / "settings.json").write_text("{corrupt json!!!")
        settings = AppSettings()
        assert settings.options.active_note_id is None

    def test_resets_on_invalid_field_type(self, settings_env):
        (settings_env / "settings.json").write_text(
            json.dumps({"active_note_id": "not-an-int"})
        )
        settings = AppSettings()
        assert settings.options.active_note_id is None

    def test_options_is_always_model_instance(self, settings_env):
        settings = AppSettings()
        assert isinstance(settings.options, AppSettingsModel)


class TestUpdateSettingsFile:
    def test_persists_active_note_id(self, settings_env):
        settings = AppSettings()
        settings.update_settings_file(AppSettingsModel(active_note_id=7))
        assert settings.options.active_note_id == 7

    def test_change_is_readable_by_new_instance(self, settings_env):
        settings = AppSettings()
        settings.update_settings_file(AppSettingsModel(active_note_id=7))
        reloaded = AppSettings()
        assert reloaded.options.active_note_id == 7

    def test_options_remains_model_instance_after_update(self, settings_env):
        settings = AppSettings()
        settings.update_settings_file(AppSettingsModel(active_note_id=3))
        assert isinstance(settings.options, AppSettingsModel)

    def test_can_clear_active_note_id_to_none(self, settings_env):
        settings = AppSettings()
        settings.update_settings_file(AppSettingsModel(active_note_id=5))
        settings.update_settings_file(AppSettingsModel(active_note_id=None))
        assert settings.options.active_note_id is None

    def test_none_is_persisted_to_file(self, settings_env):
        settings = AppSettings()
        settings.update_settings_file(AppSettingsModel(active_note_id=5))
        settings.update_settings_file(AppSettingsModel(active_note_id=None))
        reloaded = AppSettings()
        assert reloaded.options.active_note_id is None
