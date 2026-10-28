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
import os
import sys
import tempfile
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from game.game_file import GameFile
from game.tests.recording_ui import RecordingUI
from game.save_file import SavedPuzzle, SaveFile
from game.settings import Settings
from game.user_interface import MessageKind


class TestGameFile(TestCase):
    SAVED = SavedPuzzle("Standard 9x9", False, Settings(), (2, 2), [(0, 0, 1)], [(0, 1, 2, None)])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "puzzle.json")
        self.puzzle = MagicMock()
        self.puzzle.layout_name.return_value = "Standard 9x9"
        self.puzzle.has_values.return_value = True
        self.puzzle.saved_state.return_value = self.SAVED
        self.ui = RecordingUI()
        self.game_file = GameFile(self.puzzle, self.ui)
        return super().setUp()

    def tearDown(self):
        self.temp_dir.cleanup()
        return super().tearDown()

    def test_save_writes_the_puzzle_to_the_file_and_says_where(self):
        self.__save()
        self.assertEqual(SaveFile.read(self.path), self.SAVED)
        self.assertIn(f"Saved to {self.path}", self.ui.last_informed())
        self.assertEqual(self.ui.informed[-1].kind, MessageKind.INFO)

    def test_saving_an_empty_board_warns_instead_of_asking_for_a_file(self):
        self.puzzle.has_values.return_value = False
        self.game_file.save()
        self.assertEqual(self.ui.questions, [])
        self.assertIn("Nothing to save", self.ui.last_informed())

    def test_saving_over_an_existing_file_asks_first(self):
        self.__save()
        self.puzzle.saved_state.return_value = SavedPuzzle("Standard 9x9", True, Settings(), (0, 0), [], [])
        self.ui.confirms = False
        self.ui.questions.clear()
        self.__save()
        self.assertIn("already exists", self.ui.questions[-1])
        self.assertEqual(SaveFile.read(self.path), self.SAVED)

    def test_cancelled_save_writes_nothing(self):
        self.game_file.save()
        self.assertFalse(os.path.exists(self.path))

    def test_failed_save_says_why(self):
        self.path = os.path.join(self.temp_dir.name, "missing", "puzzle.json")
        self.__save()
        self.assertIn("Cannot save", self.ui.last_informed())

    def test_bare_file_name_is_saved_in_the_saved_games_folder_and_offered_as_typed(self):
        with patch.object(SaveFile, "FOLDER", os.path.join(self.temp_dir.name, "saved_games")):
            self.ui.file_name = "game.json"
            self.game_file.save()
            self.assertTrue(os.path.exists(os.path.join(SaveFile.FOLDER, "game.json")))
        self.assertEqual(self.__name_offered_by_restore(), "game")

    def test_restore_replays_the_saved_puzzle_after_confirming(self):
        self.__save()
        self.ui.questions.clear()
        self.__restore()
        self.assertIn("Really restore?", self.ui.questions[-1])
        self.puzzle.restore.assert_called_once_with(self.SAVED)

    def test_declining_the_restore_keeps_the_puzzle(self):
        self.__save()
        self.ui.confirms = False
        self.__restore()
        self.puzzle.restore.assert_not_called()

    def test_restore_onto_an_empty_board_does_not_ask(self):
        self.__save()
        self.puzzle.has_values.return_value = False
        self.ui.questions.clear()
        self.__restore()
        self.assertEqual(self.ui.questions, [("Restore from file:", self.__stem(self.path), ".json")])
        self.puzzle.restore.assert_called_once_with(self.SAVED)

    def test_restore_names_the_entries_it_ignored_or_just_counts_them(self):
        self.__restore_ignoring("notes", "themes")
        self.assertEqual(self.ui.last_informed(), "Ignored entries from a newer sudoku: notes, themes. ")
        self.assertEqual(self.ui.informed[-1].short, "Ignored 2 entries from a newer sudoku. ")
        self.assertEqual(self.ui.informed[-1].kind, MessageKind.WARNING)
        self.puzzle.restore.assert_called_once()

    def test_restore_names_a_single_ignored_entry_as_one(self):
        self.__restore_ignoring("notes")
        self.assertEqual(self.ui.last_informed(), "Ignored entry from a newer sudoku: notes. ")
        self.assertEqual(self.ui.informed[-1].short, "Ignored 1 entry from a newer sudoku. ")

    def test_restore_without_ignored_entries_does_not_warn(self):
        self.__save()
        self.ui.informed.clear()
        self.__restore()
        self.assertEqual(self.ui.informed, [])

    def test_restore_refuses_a_file_from_another_layout(self):
        SaveFile.write(self.path, SavedPuzzle("Other layout", True, Settings(), (0, 0), [(0, 0, 1)], []))
        self.__restore()
        self.assertIn('"Other layout"', self.ui.last_informed())
        self.puzzle.restore.assert_not_called()

    def test_restore_warns_about_a_file_it_cannot_read(self):
        self.__restore()
        self.assertIn("Cannot find", self.ui.last_informed())
        self.assertEqual(self.ui.informed[-1].kind, MessageKind.WARNING)
        self.puzzle.restore.assert_not_called()

    def test_the_last_file_name_used_is_offered_next_time_without_its_extension(self):
        self.__save()
        self.assertEqual(self.__name_offered_by_restore(), self.__stem(self.path))

    def test_the_default_file_name_is_offered_at_first(self):
        self.assertEqual(self.__name_offered_by_restore(), "sudoku")

    def test_the_file_name_is_asked_for_with_the_save_file_extension(self):
        self.game_file.save()
        prompt, default, extension = self.ui.questions[-1]
        self.assertEqual(extension, SaveFile.EXTENSION)
        self.assertEqual(SaveFile.EXTENSION, ".json")

    # Private functions

    def __save(self):
        """Save to the test's path"""
        self.ui.file_name = self.path
        self.game_file.save()

    def __restore(self):
        self.ui.file_name = self.path
        self.game_file.restore()

    def __restore_ignoring(self, *ignored):
        """Restore a file read as having entries this version doesn't know"""
        with patch.object(SaveFile, "read", return_value=dataclasses.replace(self.SAVED, ignored=ignored)):
            self.__restore()

    def __name_offered_by_restore(self) -> str:
        self.ui.file_name = None
        self.game_file.restore()
        prompt, default, extension = self.ui.questions[-1]
        return default

    def __stem(self, path) -> str:
        """The file name without the save file extension"""
        return path.removesuffix(".json")


if __name__ == "__main__":
    main()
