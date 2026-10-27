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
from unittest.mock import patch

from blessed.keyboard import Keystroke

from display import Display, Border
from display_attrs import DisplayAttrs


class TestDisplay(TestCase):
    Display.geometry({"h_cells": 9, "v_cells": 9})

    def setUp(self):
        return super().setUp()

    def tearDown(self):
        Display.term.inkey(timeout=1.0)
        return super().tearDown()

    def test_screen_size_validation(self):
        Display.validate_screen_size()

    def test_draw_puzzle(self):
        for row in range(3):
            for col in range(3):
                self.draw_block(row, col)
        self.fill_blocks()

    def test_warn(self0):
        Display.warn("Testing - this line should be yellow")

    def draw_block(self, block_row, block_col):
        Display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 0, border=Border({Border.TOP, Border.LEFT}))
        Display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 1, border=Border({Border.TOP}))
        Display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 2, border=Border({Border.TOP, Border.RIGHT}))

        Display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 0, border=Border({Border.LEFT}))
        Display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 1, border=Border())
        Display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 2, border=Border({Border.RIGHT}))

        Display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 0, border=Border({Border.LEFT, Border.BOTTOM}))
        Display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 1, border=Border({Border.BOTTOM}))
        Display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 2, border=Border({Border.RIGHT, Border.BOTTOM}))

    def fill_blocks(self):
        for row in range(9):
            for col in range(9):
                Display.draw_cell_value(row, col, 1 + (row + col) // 2)
                Display.draw_cell_possible_values(row, col, random.choices(range(1, 10), k=random.randint(0, 6)))
        Display.move_to_status_line()


class TestDisplayPossibleValues(TestCase):
    @patch("display.echo")
    def test_possible_values_are_drawn_in_increasing_order(self, echo):
        Display.draw_cell_possible_values(0, 0, [9, 5, 1])
        drawn = echo.call_args_list[-1].args[0]
        self.assertIn("".join(str(v).translate(Display.small_nums) for v in (1, 5, 9)), drawn)


class TestDisplayCommandPanel(TestCase):
    def test_title_and_commands_are_drawn_right_of_the_puzzle(self):
        with patch("display.echo") as echo:
            Display.draw_command_panel("PLAY", [("u", "undo"), ("q CTRL-C", "quit")])
        drawn = "".join(call.args[0] for call in echo.call_args_list)
        self.assertIn("PLAY", drawn)
        self.assertIn("undo", drawn)
        self.assertIn("quit", drawn)

    def test_every_line_beside_the_puzzle_is_cleared(self):
        with patch("display.echo") as echo:
            Display.draw_command_panel("PLAY", [])
        self.assertEqual(echo.call_count, Display.y(Display.geom["v_cells"]) + 1)

    def test_minimum_width_is_80_columns(self):
        self.assertEqual(Display.min_width(), 80)


class TestDisplayStyled(TestCase):
    def test_text_is_styled_with_the_rendered_attributes(self):
        with patch.object(Display, "term") as term:
            term.steelblue = "<steelblue>"
            term.normal = "</>"
            self.assertEqual(Display.styled("hint", (DisplayAttrs.SOLVED,)), "<steelblue>hint</>")


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
        with patch("display.echo"), patch.object(Display, "term") as term:
            term.inkey.side_effect = [key]
            return Display.confirm("Really?")


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
        return Keystroke("", code=1, name=name)

    def __ask_with(self, keys, default):
        with patch("display.echo"), patch.object(Display, "term") as term:
            term.inkey.side_effect = keys
            return Display.ask("File:", default)


if __name__ == "__main__":
    main()
