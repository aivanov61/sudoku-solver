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
from unittest.mock import patch

sys.path.insert(0, ".")

from display import Display
from display_attrs import DisplayAttrs
from terminal_ui import TerminalUI
from user_interface import Message, MessageKind


class TestTerminalUI(TestCase):
    def setUp(self):
        self.ui = TerminalUI()
        return super().setUp()

    def test_status_shows_a_warning_in_yellow_and_clears_the_rest_of_the_line(self):
        self.assertEqual(self.__status(Message("careful", MessageKind.WARNING)), "<yellow>careful</yellow><clear>")

    def test_status_shows_information_in_yellow(self):
        self.assertEqual(self.__status(Message("saved", MessageKind.INFO)), "<yellow>saved</yellow><clear>")

    def test_status_shows_success_and_hints_in_the_solved_style(self):
        for kind in (MessageKind.SUCCESS, MessageKind.HINT):
            with patch("display.Display.styled", side_effect=lambda text, attrs: f"<{attrs[0]}>{text}") as styled:
                self.assertEqual(self.__status(Message("why", kind)), "<solved>why<clear>")
            styled.assert_called_once_with("why", (DisplayAttrs.SOLVED,))

    def test_status_without_a_message_blanks_the_line(self):
        self.assertEqual(self.__status(None), "<clear>")

    def test_inform_shows_the_message_and_waits_for_a_key(self):
        with patch.object(Display, "term") as term, patch("display.Display.show_on_status_line") as show:
            term.yellow = lambda text: f"<yellow>{text}</yellow>"
            self.ui.inform(Message("careful", MessageKind.WARNING))
        show.assert_called_once_with("<yellow>careful</yellow>", wait=True)

    def test_confirm_asks_on_the_status_line(self):
        with patch("display.Display.confirm", return_value=True) as confirm:
            self.assertTrue(self.ui.confirm("Really?"))
        confirm.assert_called_once_with("Really?")

    def test_file_name_is_asked_for_on_the_status_line(self):
        with patch("display.Display.ask", return_value="game.json") as ask:
            self.assertEqual(self.ui.ask_file_name("Save to file:", "sudoku.json"), "game.json")
        ask.assert_called_once_with("Save to file:", "sudoku.json")

    # Private functions

    def __status(self, message) -> str:
        """Show the message on the status line and return what was written there"""
        with patch.object(Display, "term") as term, patch("display.Display.move_to_status_line"):
            term.yellow = lambda text: f"<yellow>{text}</yellow>"
            term.clear_eol = "<clear>"
            with patch("terminal_ui.echo") as echo:
                self.ui.status(message)
        return echo.call_args.args[0]


if __name__ == "__main__":
    main()
