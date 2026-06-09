"""Persistent application settings for QuickNote.

Settings are stored as a JSON file at
:data:`~quicknote.const.SETTINGS_FILE_PATH` and validated against
:class:`~quicknote.lib.models.AppSettingsModel` on every read.  A
missing or malformed file is silently reset to defaults so the
application never crashes on startup due to a corrupted settings file.
"""

import json

from quicknote import const
from quicknote.lib import models


class AppSettings:
    """Read and write the application settings JSON file.

    The settings file is created with defaults the first time the
    application runs, or whenever it is found to be missing or corrupt.

    Attributes:
        options (models.AppSettingsModel): In-memory representation of
            the current settings.  Always a valid model instance; never
            a raw dict.
    """

    def __init__(self) -> None:
        """Initialise and immediately load settings from disk."""
        self.options = models.AppSettingsModel()
        self.read_settings_file()

    def _reset_settings_file(self) -> None:
        """Write a fresh default settings file and reset in-memory state.

        Creates the parent directory if it does not yet exist.  Called
        automatically when the file is absent or contains invalid JSON.
        """
        const.APP_FILES_PATH.mkdir(parents=True, exist_ok=True)
        self.options = models.AppSettingsModel()
        with open(str(const.SETTINGS_FILE_PATH), "w", encoding="utf-8") as file:
            file.write(self.options.model_dump_json(indent=4))

    def read_settings_file(self) -> None:
        """Load settings from the JSON file into :attr:`options`.

        If the file does not exist, contains invalid JSON, or fails
        Pydantic validation the file is reset to defaults via
        :meth:`_reset_settings_file`.
        """
        try:
            with open(str(const.SETTINGS_FILE_PATH), encoding="utf-8") as file:
                data = json.load(file)
            self.options = models.AppSettingsModel.model_validate(data)
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            self._reset_settings_file()

    def update_settings_file(self, partial_settings: models.AppSettingsModel) -> None:
        """Merge a partial settings update and persist it to disk.

        Only fields that were explicitly set on ``partial_settings`` are
        merged into the current :attr:`options`; unset fields retain
        their existing values.

        Args:
            partial_settings (models.AppSettingsModel): A model instance
                whose set fields will be merged into the current settings.
                Fields left at their Pydantic defaults are ignored.
        """
        try:
            if not isinstance(self.options, models.AppSettingsModel):
                self.read_settings_file()

            updated_settings = partial_settings.model_dump(exclude_unset=True)
            updated_model = self.options.model_copy(update=updated_settings)

            json_data = updated_model.model_dump_json(indent=4)
            with open(str(const.SETTINGS_FILE_PATH), "w", encoding="utf-8") as file:
                file.write(json_data)

            self.options = updated_model
        except OSError:
            pass
