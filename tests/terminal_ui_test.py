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
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from cell_attrs import CellAttrs
from display import Display
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
            styled.assert_called_once_with("why", (CellAttrs.SOLVED,))

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

    def test_show_board_clears_the_screen_and_draws_every_cell_whole(self):
        cells = [self.__cell(0, 0, value=5), self.__cell(0, 1, possible={1, 2})]
        with patch("terminal_ui.Display") as display:
            self.ui.show_board(cells)
        display.clear_screen.assert_called_once()
        self.assertEqual(display.draw_cell.call_count, 2)
        display.draw_cell_value.assert_any_call(0, 0, 5, ())
        display.draw_cell_possible_values.assert_any_call(0, 1, {1, 2}, ())

    def test_a_cell_not_yet_drawn_is_drawn_whole(self):
        display = self.__drawn_after_change(None, self.__cell(2, 3, value=4))
        display.draw_cell.assert_called_once()
        display.draw_cell_value.assert_called_once_with(2, 3, 4, ())

    def test_changed_attributes_redraw_the_whole_cell(self):
        cell = self.__cell(value=4)
        display = self.__drawn_after_change(cell, self.__cell(value=4, attrs=(CellAttrs.GUESS,)))
        display.draw_cell.assert_called_once()
        display.draw_cell_value.assert_called_once()
        display.draw_cell_possible_values.assert_called_once()

    def test_a_changed_value_redraws_only_the_value(self):
        display = self.__drawn_after_change(self.__cell(value=4), self.__cell(value=6))
        display.draw_cell.assert_not_called()
        display.draw_cell_value.assert_called_once_with(0, 0, 6, ())
        display.draw_cell_possible_values.assert_not_called()

    def test_an_empty_cell_is_drawn_blank(self):
        display = self.__drawn_after_change(self.__cell(value=4), self.__cell(value=None))
        display.draw_cell_value.assert_called_once_with(0, 0, " ", ())

    def test_changed_possible_values_redraw_only_the_possible_values(self):
        display = self.__drawn_after_change(self.__cell(possible={1, 2}), self.__cell(possible={2}))
        display.draw_cell.assert_not_called()
        display.draw_cell_value.assert_not_called()
        display.draw_cell_possible_values.assert_called_once_with(0, 0, {2}, ())

    def test_an_unchanged_cell_is_not_redrawn(self):
        display = self.__drawn_after_change(self.__cell(value=4), self.__cell(value=4))
        self.assertEqual(display.method_calls, [])

    def test_guesses_going_deeper_than_the_last_shade_warn(self):
        self.assertEqual(self.__warnings_for_depths([10, 11]), ["No more shades of gray left - repeating last shade. "])

    def test_guesses_staying_beyond_the_last_shade_do_not_warn_again(self):
        self.assertEqual(len(self.__warnings_for_depths([11, 12, 11])), 1)

    def test_coming_back_within_the_shades_and_going_beyond_again_warns_again(self):
        self.assertEqual(len(self.__warnings_for_depths([11, 10, 11])), 2)

    def test_guesses_within_the_shades_do_not_warn(self):
        self.assertEqual(self.__warnings_for_depths([1, 2, 10, 9, 0]), [])

    # Private functions

    def __cell(self, row=0, col=0, value=None, attrs=(), possible=frozenset()):
        """A stand-in for a cell as it is at one moment"""
        cell = MagicMock(row=row, col=col)
        cell.value.return_value = value
        cell.attr.return_value = attrs
        cell.possible_values.return_value = set(possible)
        return cell

    def __drawn_after_change(self, before, after):
        """Report the cell as before (if any), then as after; return the patched Display used for the second report"""
        with patch("terminal_ui.Display"):
            before and self.ui.cell_changed(before)
        with patch("terminal_ui.Display") as display:
            self.ui.cell_changed(after)
        return display

    def __warnings_for_depths(self, depths) -> list:
        """Report each guess depth in turn; return the text of every warning shown"""
        with patch.object(TerminalUI, "inform") as inform:
            for depth in depths:
                self.ui.guess_depth_changed(depth)
        return [call.args[0].text for call in inform.call_args_list]

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
