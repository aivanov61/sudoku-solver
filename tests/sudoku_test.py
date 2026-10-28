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

import sys
from unittest import main, TestCase
from unittest.mock import call, MagicMock, patch

from blessed.keyboard import Keystroke

sys.path.insert(0, ".")

from sudoku import Main


class TestMain(TestCase):
    def test_the_key_that_ends_the_splash_is_read_in_cbreak_mode(self):
        term = self.__run_with_keys(Keystroke("\r", code=343, name="KEY_ENTER"), Keystroke(""))
        calls = term.mock_calls
        self.assertLess(calls.index(call.cbreak().__enter__()), calls.index(call.inkey(timeout=5.0)))
        self.assertLess(calls.index(call.inkey(timeout=5.0)), calls.index(call.cbreak().__exit__(None, None, None)))

    def test_the_display_has_the_command_panel_by_default(self):
        self.__run_with_keys(Keystroke("x"), Keystroke(""))
        self.display_class.assert_called_once_with(panel=True)

    def test_no_panel_leaves_the_command_panel_out(self):
        self.__run_with_keys(Keystroke("x"), Keystroke(""), args=["--no-panel"])
        self.display_class.assert_called_once_with(panel=False)

    def test_other_keys_pressed_during_the_splash_are_dropped(self):
        keys = [Keystroke("\r", code=343, name="KEY_ENTER"), Keystroke("\n", code=343, name="KEY_ENTER"), Keystroke("x")]
        term = self.__run_with_keys(*keys, Keystroke(""))
        self.assertEqual(term.inkey.call_count, 4)
        self.assertEqual(term.inkey.call_args_list[1:], [call(timeout=0)] * 3)

    # Private functions

    def __run_with_keys(self, *keys, args=()) -> MagicMock:
        """
        Run with the command line arguments and no layouts, so the program ends after the splash; return the
        terminal it read the keys from
        """
        display = MagicMock()
        display.term.inkey.side_effect = keys
        with (
            patch("sudoku.Display", return_value=display) as self.display_class,
            patch("sudoku.Copyright"),
            patch("sudoku.PuzzleCatalog.available", return_value=[]),
            patch("builtins.print"),
        ):
            Main().run(list(args))
        return display.term


if __name__ == "__main__":
    main()
