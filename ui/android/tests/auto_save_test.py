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
import tempfile
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

from game.save_file import SavedPuzzle, SaveFile
from game.settings import Settings
from game.tests.recording_ui import RecordingUI
from game.user_interface import MessageKind
from ui.android.auto_save import AutoSave


class TestAutoSave(TestCase):
    SAVED = SavedPuzzle("Standard 9x9", False, Settings(), (2, 2), [], [(0, 0, 1)], [(0, 1, 2, None)])
    OTHER = SavedPuzzle("Standard 9x9", True, Settings(), (0, 0), [], [(4, 4, 7)], [])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "autosave.json")
        self.puzzle = MagicMock()
        self.puzzle.layout_name.return_value = "Standard 9x9"
        self.puzzle.has_values.return_value = True
        self.puzzle.saved_state.return_value = self.SAVED
        self.ui = RecordingUI()
        self.auto_save = AutoSave(self.path, self.ui)
        return super().setUp()

    def tearDown(self):
        self.temp_dir.cleanup()
        return super().tearDown()

    # The saved game's layout

    def test_the_saved_layout_is_the_layout_of_the_game_saved(self):
        SaveFile.write(self.path, self.SAVED)
        self.assertEqual(AutoSave.saved_layout(self.path), "Standard 9x9")

    def test_there_is_no_saved_layout_without_a_file(self):
        self.assertIsNone(AutoSave.saved_layout(self.path))

    def test_there_is_no_saved_layout_when_the_file_cannot_be_read(self):
        self.__write_damaged()
        self.assertIsNone(AutoSave.saved_layout(self.path))

    # Saving

    def test_save_writes_the_game_to_the_file(self):
        self.auto_save.save(self.puzzle)
        self.assertEqual(SaveFile.read(self.path), self.SAVED)

    def test_save_says_nothing_when_it_works(self):
        self.auto_save.save(self.puzzle)
        self.assertEqual(self.ui.informed, [])

    def test_saving_an_empty_board_writes_nothing(self):
        self.puzzle.has_values.return_value = False
        self.auto_save.save(self.puzzle)
        self.assertFalse(os.path.exists(self.path))

    def test_saving_an_empty_board_deletes_the_game_saved_before(self):
        self.auto_save.save(self.puzzle)
        self.puzzle.has_values.return_value = False
        self.auto_save.save(self.puzzle)
        self.assertFalse(os.path.exists(self.path))

    def test_a_failed_save_says_why(self):
        self.auto_save = AutoSave(os.path.join(self.temp_dir.name, "missing", "autosave.json"), self.ui)
        self.auto_save.save(self.puzzle)
        self.assertIn("Cannot save the game", self.ui.last_informed())
        self.assertEqual(self.ui.informed[-1].kind, MessageKind.WARNING)

    # Restoring

    def test_restore_restores_the_game_saved(self):
        SaveFile.write(self.path, self.SAVED)
        self.auto_save.restore(self.puzzle)
        self.puzzle.restore.assert_called_once_with(self.SAVED)
        self.assertEqual(self.ui.informed, [])

    def test_restore_without_a_file_leaves_the_game_new_and_says_nothing(self):
        self.auto_save.restore(self.puzzle)
        self.puzzle.restore.assert_not_called()
        self.assertEqual(self.ui.informed, [])

    def test_restore_warns_about_a_file_it_cannot_read_and_leaves_the_game_new(self):
        self.__write_damaged()
        self.auto_save.restore(self.puzzle)
        self.assertIn("damaged", self.ui.last_informed())
        self.assertIn("A new puzzle is started", self.ui.last_informed())
        self.assertEqual(self.ui.informed[-1].kind, MessageKind.WARNING)
        self.puzzle.restore.assert_not_called()

    def test_restore_warns_about_a_game_on_another_layout_and_leaves_the_game_new(self):
        SaveFile.write(self.path, dataclasses.replace(self.SAVED, layout="Other layout"))
        self.auto_save.restore(self.puzzle)
        self.assertIn('"Other layout"', self.ui.last_informed())
        self.puzzle.restore.assert_not_called()

    def test_restore_names_the_entries_it_ignored(self):
        with patch.object(SaveFile, "read", return_value=dataclasses.replace(self.SAVED, ignored=("notes",))):
            SaveFile.write(self.path, self.SAVED)
            self.auto_save.restore(self.puzzle)
        self.assertEqual(self.ui.last_informed(), "Ignored entry from a newer sudoku: notes. ")
        self.puzzle.restore.assert_called_once()

    # A file that cannot be read is kept until there is something to save

    def test_a_file_that_cannot_be_read_is_kept_while_the_board_is_empty(self):
        self.__write_damaged()
        self.auto_save.restore(self.puzzle)
        self.puzzle.has_values.return_value = False
        self.auto_save.save(self.puzzle)
        self.assertTrue(os.path.exists(self.path))

    def test_a_file_that_cannot_be_read_is_overwritten_once_there_is_something_to_save(self):
        self.__write_damaged()
        self.auto_save.restore(self.puzzle)
        self.auto_save.save(self.puzzle)
        self.assertEqual(SaveFile.read(self.path), self.SAVED)

    def test_a_file_that_cannot_be_read_is_kept_once_the_game_is_over(self):
        self.__write_damaged()
        self.auto_save.restore(self.puzzle)
        self.auto_save.forget()
        self.assertTrue(os.path.exists(self.path))

    # Forgetting, once the game is over

    def test_forget_deletes_the_game_saved(self):
        self.auto_save.save(self.puzzle)
        self.auto_save.forget()
        self.assertFalse(os.path.exists(self.path))

    def test_forget_deletes_the_game_restored(self):
        SaveFile.write(self.path, self.SAVED)
        self.auto_save.restore(self.puzzle)
        self.auto_save.forget()
        self.assertFalse(os.path.exists(self.path))

    def test_forget_without_a_file_does_nothing(self):
        self.auto_save.forget()
        self.assertFalse(os.path.exists(self.path))

    def test_a_game_saved_and_forgotten_can_be_saved_again(self):
        self.auto_save.save(self.puzzle)
        self.auto_save.forget()
        self.puzzle.saved_state.return_value = self.OTHER
        self.auto_save.save(self.puzzle)
        self.assertEqual(SaveFile.read(self.path), self.OTHER)

    # Private functions

    def __write_damaged(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("not a save file")


if __name__ == "__main__":
    main()
