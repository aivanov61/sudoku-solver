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

import json
import os
import sys
import tempfile
from unittest import main, TestCase
from unittest.mock import patch

sys.path.insert(0, ".")

from save_file import SavedPuzzle, SaveFile, SaveFileError


class TestSaveFile(TestCase):
    SAVED = SavedPuzzle(
        layout="Standard 9x9",
        initializing=False,
        selected_cell=(4, 7),
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

    # Private functions

    def __json(self) -> dict:
        with open(self.path) as file:
            return json.load(file)

    def __write_json(self, data) -> None:
        with open(self.path, "w") as file:
            json.dump(data, file)


if __name__ == "__main__":
    main()
