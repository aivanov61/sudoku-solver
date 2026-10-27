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

import random
import sys

sys.path.insert(0, ".")

from unittest import main, TestCase
from unittest.mock import MagicMock, patch

from blessed.keyboard import Keystroke

from game.border import Border
from game.cell_attrs import CellAttrs
from ui.terminal.display import Display


def board_display(term=None) -> Display:
    """A display for a 9x9 board, on the given terminal (the real one if none)"""
    display = Display(term)
    display.geometry(9, 9)
    return display


class TestDisplay(TestCase):
    def setUp(self):
        self.display = board_display()
        return super().setUp()

    def tearDown(self):
        self.display.term.inkey(timeout=1.0)
        return super().tearDown()

    def test_screen_size_validation(self):
        self.display.validate_screen_size()

    def test_draw_puzzle(self):
        for row in range(3):
            for col in range(3):
                self.draw_block(row, col)
        self.fill_blocks()

    def test_warn(self0):
        self0.display.warn("Testing - this line should be yellow")

    def draw_block(self, block_row, block_col):
        self.display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 0, border=Border({Border.TOP, Border.LEFT}))
        self.display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 1, border=Border({Border.TOP}))
        self.display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 2, border=Border({Border.TOP, Border.RIGHT}))

        self.display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 0, border=Border({Border.LEFT}))
        self.display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 1, border=Border())
        self.display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 2, border=Border({Border.RIGHT}))

        self.display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 0, border=Border({Border.LEFT, Border.BOTTOM}))
        self.display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 1, border=Border({Border.BOTTOM}))
        self.display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 2, border=Border({Border.RIGHT, Border.BOTTOM}))

    def fill_blocks(self):
        for row in range(9):
            for col in range(9):
                self.display.draw_cell_value(row, col, 1 + (row + col) // 2)
                self.display.draw_cell_possible_values(row, col, random.choices(range(1, 10), k=random.randint(0, 6)))
        self.display.move_to_status_line()


class TestDisplayBoardSize(TestCase):
    def test_each_display_keeps_its_own_board_size(self):
        small, large = Display(MagicMock()), Display(MagicMock())
        small.geometry(4, 4)
        large.geometry(9, 9)
        self.assertEqual(small.status_line_location(), (0, 13))
        self.assertEqual(large.status_line_location(), (0, 28))

    def test_a_display_uses_the_terminal_it_is_given(self):
        term = MagicMock()
        self.assertIs(Display(term).term, term)


class TestDisplayPossibleValues(TestCase):
    @patch("ui.terminal.display.echo")
    def test_possible_values_are_drawn_in_increasing_order(self, echo):
        board_display().draw_cell_possible_values(0, 0, [9, 5, 1])
        drawn = echo.call_args_list[-1].args[0]
        self.assertIn("".join(str(v).translate(Display.small_nums) for v in (1, 5, 9)), drawn)


class TestDisplayCommandPanel(TestCase):
    def test_title_and_commands_are_drawn_right_of_the_puzzle(self):
        with patch("ui.terminal.display.echo") as echo:
            board_display().draw_command_panel("PLAY", [("u", "undo"), ("q CTRL-C", "quit")])
        drawn = "".join(call.args[0] for call in echo.call_args_list)
        self.assertIn("PLAY", drawn)
        self.assertIn("undo", drawn)
        self.assertIn("quit", drawn)

    def test_every_line_beside_the_puzzle_is_cleared(self):
        display = board_display()
        with patch("ui.terminal.display.echo") as echo:
            display.draw_command_panel("PLAY", [])
        self.assertEqual(echo.call_count, display.y(9) + 1)

    def test_minimum_width_is_80_columns(self):
        self.assertEqual(board_display().min_width(), 80)


class TestDisplayStyled(TestCase):
    def test_text_is_styled_with_the_rendered_attributes(self):
        term = MagicMock(steelblue="<steelblue>", normal="</>")
        self.assertEqual(board_display(term).styled("hint", (CellAttrs.SOLVED,)), "<steelblue>hint</>")


class TestDisplayStatusLine(TestCase):
    def test_text_is_shown_on_the_status_line_as_given(self):
        echo, hit_any_key = self.__show("<styled>")
        echo.assert_called_once_with("<clear><styled>")
        hit_any_key.assert_not_called()

    def test_text_waits_for_a_key_when_asked(self):
        echo, hit_any_key = self.__show("<styled>", wait=True)
        hit_any_key.assert_called_once()

    def test_warning_is_shown_in_yellow(self):
        term = MagicMock(clear_eol="<clear>")
        term.yellow = lambda text: f"<yellow>{text}</yellow>"
        with patch("ui.terminal.display.echo") as echo:
            board_display(term).warn("careful")
        echo.assert_called_once_with("<clear><yellow>careful</yellow>")

    # Private functions

    def __show(self, text, wait=False):
        display = board_display(MagicMock(clear_eol="<clear>"))
        with patch("ui.terminal.display.echo") as echo, patch.object(display, "hit_any_key_to_continue") as hit_any_key:
            display.show_on_status_line(text, wait=wait)
        return echo, hit_any_key


class TestDisplayConfirm(TestCase):
    def test_y_confirms(self):
        self.assertTrue(self.__confirm_with("y"))

    def test_capital_y_confirms(self):
        self.assertTrue(self.__confirm_with("Y"))

    def test_any_other_key_declines(self):
        self.assertFalse(self.__confirm_with("n"))
        self.assertFalse(self.__confirm_with("q"))

    def test_interrupted_prompt_declines(self):
        self.assertFalse(self.__confirm_with(KeyboardInterrupt()))

    # Private functions

    def __confirm_with(self, key):
        term = MagicMock()
        term.inkey.side_effect = [key]
        with patch("ui.terminal.display.echo"):
            return board_display(term).confirm("Really?")


class TestDisplayAsk(TestCase):
    def test_enter_accepts_the_default(self):
        self.assertEqual(self.__ask_with([self.__key("KEY_ENTER")], default="sudoku.json"), "sudoku.json")

    def test_typed_characters_are_added_to_the_default(self):
        keys = [Keystroke("2"), Keystroke("!"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="a"), "a2!")

    def test_backspace_removes_the_last_character(self):
        keys = [self.__key("KEY_BACKSPACE"), Keystroke("b"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="aa"), "ab")

    def test_escape_cancels(self):
        self.assertIsNone(self.__ask_with([Keystroke("x"), self.__key("KEY_ESCAPE")], default="a"))

    def test_other_special_keys_are_ignored(self):
        keys = [self.__key("KEY_LEFT"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="a"), "a")

    def test_interrupted_prompt_cancels(self):
        self.assertIsNone(self.__ask_with([KeyboardInterrupt()], default="a"))

    # Private functions

    def __key(self, name) -> Keystroke:
        return Keystroke("", code=1, name=name)

    def __ask_with(self, keys, default):
        term = MagicMock()
        term.inkey.side_effect = keys
        with patch("ui.terminal.display.echo"):
            return board_display(term).ask("File:", default)


if __name__ == "__main__":
    main()
