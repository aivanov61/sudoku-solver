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

import os
import sys
import tempfile
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from game_file import GameFile
from save_file import SavedPuzzle, SaveFile


class TestGameFile(TestCase):
    SAVED = SavedPuzzle("Standard 9x9", False, (2, 2), [(0, 0, 1)], [(0, 1, 2, None)])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "puzzle.json")
        self.puzzle = MagicMock()
        self.puzzle.layout_name.return_value = "Standard 9x9"
        self.puzzle.has_values.return_value = True
        self.puzzle.saved_state.return_value = self.SAVED
        self.game_file = GameFile(self.puzzle)
        return super().setUp()

    def tearDown(self):
        self.temp_dir.cleanup()
        return super().tearDown()

    def test_save_writes_the_puzzle_to_the_file_and_says_where(self):
        warn = self.__save()
        self.assertEqual(SaveFile.read(self.path), self.SAVED)
        self.assertIn(f"Saved to {self.path}", warn.call_args.args[0])

    def test_saving_an_empty_board_warns_instead_of_asking_for_a_file(self):
        self.puzzle.has_values.return_value = False
        with patch("display.Display.ask") as ask, patch("display.Display.warn") as warn:
            self.game_file.save()
        ask.assert_not_called()
        self.assertIn("Nothing to save", warn.call_args.args[0])

    def test_saving_over_an_existing_file_asks_first(self):
        self.__save()
        self.puzzle.saved_state.return_value = SavedPuzzle("Standard 9x9", True, (0, 0), [], [])
        with patch("display.Display.confirm", return_value=False) as confirm:
            self.__save()
        confirm.assert_called_once()
        self.assertEqual(SaveFile.read(self.path), self.SAVED)

    def test_cancelled_save_writes_nothing(self):
        with patch("display.Display.ask", return_value=None):
            self.game_file.save()
        self.assertFalse(os.path.exists(self.path))

    def test_failed_save_says_why(self):
        self.path = os.path.join(self.temp_dir.name, "missing", "puzzle.json")
        warn = self.__save()
        self.assertIn("Cannot save", warn.call_args.args[0])

    def test_bare_file_name_is_saved_in_the_saved_games_folder_and_offered_as_typed(self):
        with patch.object(SaveFile, "FOLDER", os.path.join(self.temp_dir.name, "saved_games")):
            with patch("display.Display.ask", return_value="game.json"), patch("display.Display.warn"):
                self.game_file.save()
            self.assertTrue(os.path.exists(os.path.join(SaveFile.FOLDER, "game.json")))
        self.assertEqual(self.__name_offered_by_restore(), "game.json")

    def test_restore_replays_the_saved_puzzle_after_confirming(self):
        self.__save()
        with patch("display.Display.confirm", return_value=True) as confirm:
            self.__restore()
        confirm.assert_called_once()
        self.puzzle.restore.assert_called_once_with(self.SAVED)

    def test_declining_the_restore_keeps_the_puzzle(self):
        self.__save()
        with patch("display.Display.confirm", return_value=False):
            self.__restore()
        self.puzzle.restore.assert_not_called()

    def test_restore_onto_an_empty_board_does_not_ask(self):
        self.__save()
        self.puzzle.has_values.return_value = False
        with patch("display.Display.confirm") as confirm:
            self.__restore()
        confirm.assert_not_called()
        self.puzzle.restore.assert_called_once_with(self.SAVED)

    def test_restore_refuses_a_file_from_another_layout(self):
        SaveFile.write(self.path, SavedPuzzle("Other layout", True, (0, 0), [(0, 0, 1)], []))
        with patch("display.Display.warn") as warn:
            self.__restore()
        self.assertIn('"Other layout"', warn.call_args.args[0])
        self.puzzle.restore.assert_not_called()

    def test_restore_warns_about_a_file_it_cannot_read(self):
        with patch("display.Display.warn") as warn:
            self.__restore()
        self.assertIn("Cannot find", warn.call_args.args[0])
        self.puzzle.restore.assert_not_called()

    def test_the_last_file_name_used_is_offered_next_time(self):
        self.__save()
        self.assertEqual(self.__name_offered_by_restore(), self.path)

    def test_the_default_file_name_is_offered_at_first(self):
        self.assertEqual(self.__name_offered_by_restore(), GameFile.DEFAULT_FILE_NAME)

    # Private functions

    def __save(self):
        """Save to the test's path; return the patched warning"""
        with patch("display.Display.ask", return_value=self.path), patch("display.Display.warn") as warn:
            self.game_file.save()
        return warn

    def __restore(self):
        with patch("display.Display.ask", return_value=self.path):
            self.game_file.restore()

    def __name_offered_by_restore(self) -> str:
        with patch("display.Display.ask", return_value=None) as ask:
            self.game_file.restore()
        return ask.call_args.args[1]


if __name__ == "__main__":
    main()
