# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import dataclasses
import json
import os
import sys
import tempfile
from unittest import main, TestCase
from unittest.mock import patch

sys.path.insert(0, ".")

from game.marks_setting import MarksSetting
from game.save_file import SavedPuzzle, SaveFile, SaveFileError
from game.settings import Settings


class TestSaveFile(TestCase):
    SAVED = SavedPuzzle(
        layout="Standard 9x9",
        initializing=False,
        settings=Settings({MarksSetting.NAME: MarksSetting(3, MarksSetting.EVERY_HOUSE)}),
        selected_cell=(4, 7),
        tags=[(1, 2), (6, 0)],
        givens=[(0, 0, 5), (8, 8, 1)],
        moves=[(0, 1, 3, None), (2, 2, 7, "guess"), (3, 3, 9, "solved")],
    )

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "puzzle.json")
        return super().setUp()

    def tearDown(self):
        self.temp_dir.cleanup()
        return super().tearDown()

    def test_saved_puzzle_reads_back_unchanged(self):
        SaveFile.write(self.path, self.SAVED)
        self.assertEqual(SaveFile.read(self.path), self.SAVED)

    def test_file_records_its_format_and_version(self):
        SaveFile.write(self.path, self.SAVED)
        data = self.__json()
        self.assertEqual(data["format"], SaveFile.FORMAT)
        self.assertEqual(data["version"], SaveFile.VERSION)

    def test_older_version_is_upgraded_one_version_at_a_time(self):
        SaveFile.write(self.path, self.SAVED)
        upgrades = {
            SaveFile.VERSION: lambda state: {**state, "layout": state["layout"] + " v2"},
            SaveFile.VERSION + 1: lambda state: {**state, "layout": state["layout"] + " v3"},
        }
        with patch.object(SaveFile, "VERSION", SaveFile.VERSION + 2), patch.object(SaveFile, "UPGRADES", upgrades):
            self.assertEqual(SaveFile.read(self.path).layout, "Standard 9x9 v2 v3")

    def test_settings_are_saved_by_name(self):
        SaveFile.write(self.path, self.SAVED)
        marks = {"threshold": 3, "kinds": ["box", "row", "column"]}
        self.assertEqual(self.__json()["state"]["settings"], {"marks": marks})

    def test_a_file_saved_without_tags_is_read_with_none(self):
        SaveFile.write(self.path, self.SAVED)
        data = self.__json()
        del data["state"]["tags"]
        self.__write_json(data)
        self.assertEqual(SaveFile.read(self.path).tags, [])

    def test_a_file_saved_without_settings_is_read_with_the_default_settings(self):
        SaveFile.write(self.path, self.SAVED)
        data = self.__json()
        del data["state"]["settings"]
        self.__write_json(data)
        self.assertEqual(SaveFile.read(self.path).settings, Settings())

    def test_entries_from_a_newer_version_are_read_as_ignored_each_with_its_path(self):
        SaveFile.write(self.path, self.SAVED)
        data = self.__json()
        data["state"]["settings"]["marks"]["style"] = "dots"
        data["state"]["settings"]["themes"] = {"name": "dark"}
        data["state"]["notes"] = []
        data["hello"] = "world"
        self.__write_json(data)
        saved = SaveFile.read(self.path)
        self.assertEqual(saved.ignored, ("state.settings.marks.style", "state.settings.themes", "state.notes", "hello"))
        self.assertEqual(dataclasses.replace(saved, ignored=()), self.SAVED)

    def test_ignored_entries_are_not_saved_again(self):
        SaveFile.write(self.path, dataclasses.replace(self.SAVED, ignored=("notes",)))
        self.assertNotIn("ignored", self.__json()["state"])

    def test_newer_version_cannot_be_read_and_suggests_updating(self):
        SaveFile.write(self.path, self.SAVED)
        self.__write_json({**self.__json(), "version": SaveFile.VERSION + 1})
        with self.assertRaisesRegex(SaveFileError, "newer version.*update"):
            SaveFile.read(self.path)

    def test_missing_file_cannot_be_read(self):
        with self.assertRaisesRegex(SaveFileError, "Cannot find"):
            SaveFile.read(self.path)

    def test_file_that_is_not_json_is_damaged(self):
        with open(self.path, "w") as file:
            file.write("not a saved puzzle")
        with self.assertRaisesRegex(SaveFileError, "damaged"):
            SaveFile.read(self.path)

    def test_json_from_another_program_is_damaged(self):
        self.__write_json({"version": 1, "state": {}})
        with self.assertRaisesRegex(SaveFileError, "damaged"):
            SaveFile.read(self.path)

    def test_saved_puzzle_with_missing_parts_is_damaged(self):
        SaveFile.write(self.path, self.SAVED)
        data = self.__json()
        del data["state"]["givens"]
        self.__write_json(data)
        with self.assertRaisesRegex(SaveFileError, "damaged"):
            SaveFile.read(self.path)

    def test_saved_puzzle_with_an_unknown_marks_setting_is_damaged(self):
        SaveFile.write(self.path, self.SAVED)
        data = self.__json()
        data["state"]["settings"]["marks"]["threshold"] = 7
        self.__write_json(data)
        with self.assertRaisesRegex(SaveFileError, "damaged"):
            SaveFile.read(self.path)

    def test_bare_file_name_is_located_in_the_saved_games_folder(self):
        self.assertEqual(SaveFile.located("game.json"), os.path.join(SaveFile.FOLDER, "game.json"))

    def test_file_name_with_a_folder_is_used_as_given(self):
        for path in (os.path.join("elsewhere", "game.json"), os.path.join(".", "game.json")):
            self.assertEqual(SaveFile.located(path), path)

    def test_saving_creates_the_missing_saved_games_folder(self):
        with patch.object(SaveFile, "FOLDER", os.path.join(self.temp_dir.name, "saved_games")):
            SaveFile.write(SaveFile.located("game.json"), self.SAVED)
            self.assertTrue(os.path.exists(os.path.join(SaveFile.FOLDER, "game.json")))

    def test_saving_does_not_create_other_missing_folders(self):
        with self.assertRaises(OSError):
            SaveFile.write(os.path.join(self.temp_dir.name, "missing", "game.json"), self.SAVED)

    # Private functions

    def __json(self) -> dict:
        with open(self.path) as file:
            return json.load(file)

    def __write_json(self, data) -> None:
        with open(self.path, "w") as file:
            json.dump(data, file)


if __name__ == "__main__":
    main()
