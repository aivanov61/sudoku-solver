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
import textwrap

sys.path.insert(0, ".")

from unittest import main, TestCase
from unittest.mock import MagicMock, patch

from blessed.keyboard import Keystroke

from game.border import Border
from game.cell_attrs import CellAttrs
from ui.terminal.display import Display


def status_term(width=80, height=40) -> MagicMock:
    """A stand-in terminal for the status line: its size, a wrap() splitting at words, and readable sequences"""
    term = MagicMock(width=width, height=height, clear_eos="<clear>", normal="</>")
    term.wrap = lambda text, width: textwrap.wrap(text, width)
    term.move_xy = lambda x, y: f"<{x},{y}>"
    term.yellow = lambda text: f"<yellow>{text}</yellow>"
    return term


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

    @patch("ui.terminal.display.echo")
    def test_possible_values_of_a_tagged_cell_are_drawn_in_the_tag_color(self, echo):
        display = board_display()
        display.draw_cell_possible_values(0, 0, [5], tagged=True)
        self.assertTrue(echo.call_args_list[-1].args[0].startswith(display.term.steelblue))


class TestDisplayMarks(TestCase):
    def test_marks_are_drawn_across_the_middle_line_of_the_cell(self):
        display = board_display(MagicMock())
        with patch("ui.terminal.display.echo"):
            display.draw_cell_marks(2, 5, (4,))
        display.term.move_xy.assert_called_with(display.x(5) + 1, display.y(2) + Display.CELL_VALUE_ROW)

    def test_one_mark_is_centred(self):
        self.assertIn("  ₄  ", self.__drawn((4,)))

    def test_up_to_three_marks_are_spaced(self):
        self.assertIn(" ₄ ₇ ", self.__drawn((4, 7)))
        self.assertIn("₁ ₄ ₇", self.__drawn((1, 4, 7)))

    def test_four_or_five_marks_are_closed_up(self):
        self.assertIn("₁₂₄₇", self.__drawn((1, 2, 4, 7)))
        self.assertIn("₁₂₄₇₉", self.__drawn((1, 2, 4, 7, 9)))

    def test_more_marks_than_fit_are_shown_as_dots(self):
        self.assertIn(".....", self.__drawn((1, 2, 3, 4, 7, 9)))

    def test_no_marks_blank_the_middle_line(self):
        self.assertIn(" " * Display.CELL_HORIZONTAL_SIZE, self.__drawn(()))

    def test_marks_of_a_tagged_cell_are_drawn_in_the_tag_color(self):
        display = board_display()
        with patch("ui.terminal.display.echo") as echo:
            display.draw_cell_marks(0, 0, (4,), tagged=True)
        self.assertTrue(echo.call_args_list[-1].args[0].startswith(display.term.steelblue))

    # Private functions

    def __drawn(self, marks) -> str:
        """Draw the marks on the real terminal; return what was written for them"""
        with patch("ui.terminal.display.echo") as echo:
            board_display().draw_cell_marks(0, 0, marks)
        return echo.call_args_list[-1].args[0]


class TestDisplayMissingValue(TestCase):
    def test_a_missing_value_is_drawn_white_on_red_in_the_middle_of_its_cell(self):
        display = Display(MagicMock())
        display.geometry(9, 9)
        display.term.white_on_red = lambda text: f"<white on red>{text}"
        with patch("ui.terminal.display.echo") as echo:
            display.draw_cell_missing_value(2, 5, 4)
        middle = (display.x(5) + Display.CELL_WIDTH // 2, display.y(2) + Display.CELL_VALUE_ROW)
        display.term.move_xy.assert_called_with(*middle)
        self.assertEqual(echo.call_args.args[0], "<white on red>4")


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

    def test_minimum_width_without_the_panel_is_the_puzzles_width(self):
        display = Display(MagicMock(), panel=False)
        display.geometry(9, 9)
        self.assertEqual(display.min_width(), 9 * Display.CELL_WIDTH + 1)

    def test_minimum_height_is_the_puzzle_and_the_status_line(self):
        self.assertEqual(board_display(MagicMock()).min_height(), 9 * Display.CELL_HEIGHT + 2)

    def test_minimum_height_without_the_panel_has_room_for_messages_to_wrap(self):
        display = Display(MagicMock(), panel=False)
        display.geometry(9, 9)
        self.assertEqual(display.min_height(), 9 * Display.CELL_HEIGHT + 1 + Display.STATUS_LINES_WITHOUT_PANEL)

    def test_a_display_has_the_panel_unless_told_otherwise(self):
        self.assertEqual((Display(MagicMock()).panel, Display(MagicMock(), panel=False).panel), (True, False))


class TestDisplayStyled(TestCase):
    def test_text_is_styled_with_the_rendered_attributes(self):
        term = MagicMock(steelblue="<steelblue>", normal="</>")
        self.assertEqual(board_display(term).styled("hint", (CellAttrs.SOLVED,)), "<steelblue>hint</>")


class TestDisplayStatusLine(TestCase):
    STATUS_Y = 9 * Display.CELL_HEIGHT + 1

    def test_text_is_shown_on_the_status_line_as_given(self):
        echo, term = self.__show("<styled>")
        echo.assert_called_once_with("<clear><styled>")
        term.inkey.assert_not_called()

    def test_text_waits_for_a_key_when_asked_after_the_prompt(self):
        echo, term = self.__show("Careful. ", wait=True)
        echo.assert_called_once_with("<clear>Careful. " + Display.HIT_ANY_KEY.strip())
        term.inkey.assert_called_once()

    def test_long_text_is_split_at_words_onto_the_lines_below(self):
        echo, _term = self.__show("one two three four five six", width=20)
        echo.assert_called_once_with(f"<clear>one two three four<0,{self.STATUS_Y + 1}>five six")

    def test_text_longer_than_the_lines_left_is_cut_short(self):
        echo, _term = self.__show("one two three four five six seven eight", width=12, height=self.STATUS_Y + 2)
        echo.assert_called_once_with(f"<clear>one two<0,{self.STATUS_Y + 1}>three four…</>")

    def test_warning_is_shown_in_yellow(self):
        with patch("ui.terminal.display.echo") as echo:
            board_display(status_term()).warn("careful")
        echo.assert_called_once_with("<clear><yellow>careful</yellow>")

    # Private functions

    def __show(self, text, wait=False, width=80, height=40):
        term = status_term(width, height)
        with patch("ui.terminal.display.echo") as echo:
            board_display(term).show_on_status_line(text, wait=wait)
        return echo, term


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
        term = status_term()
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

    def test_the_suffix_is_shown_after_the_text_with_the_cursor_before_it(self):
        echoed = []
        self.__ask_with([self.__key("KEY_ENTER")], default="ab", suffix=".json", echoed=echoed)
        self.assertIn("<yellow>File: ab.json</yellow>", echoed)
        self.assertIn("<left 5>", echoed)

    def test_the_suffix_is_not_part_of_the_answer(self):
        self.assertEqual(self.__ask_with([self.__key("KEY_ENTER")], default="ab", suffix=".json"), "ab")

    def test_left_arrow_moves_the_cursor_and_typing_inserts_there(self):
        keys = [self.__key("KEY_LEFT"), Keystroke("x"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="ab", suffix=".json"), "axb")

    def test_the_cursor_stops_at_the_start_of_the_text(self):
        keys = [self.__key("KEY_LEFT")] * 3 + [Keystroke("x"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="ab", suffix=".json"), "xab")

    def test_the_cursor_stops_before_the_suffix(self):
        keys = [self.__key("KEY_LEFT"), self.__key("KEY_RIGHT"), self.__key("KEY_RIGHT"), Keystroke("x"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="ab", suffix=".json"), "abx")

    def test_backspace_removes_the_character_before_the_cursor(self):
        keys = [self.__key("KEY_LEFT"), self.__key("KEY_BACKSPACE"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="ab", suffix=".json"), "b")

    def test_delete_removes_the_character_at_the_cursor(self):
        keys = [self.__key("KEY_LEFT"), self.__key("KEY_DELETE"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="ab", suffix=".json"), "a")

    def test_delete_at_the_end_of_the_text_does_nothing(self):
        keys = [self.__key("KEY_DELETE"), self.__key("KEY_ENTER")]
        self.assertEqual(self.__ask_with(keys, default="ab", suffix=".json"), "ab")

    # Private functions

    def __key(self, name) -> Keystroke:
        return Keystroke("", code=1, name=name)

    def __ask_with(self, keys, default, suffix="", echoed=None):
        """Answer the prompt with the keys; collect what it echoed, if a list is given"""
        term = status_term()
        term.inkey.side_effect = keys
        term.move_left = lambda count: f"<left {count}>"
        term.clear_eos = ""
        with patch("ui.terminal.display.echo", side_effect=lambda text: echoed is not None and echoed.append(text)):
            return board_display(term).ask("File:", default, suffix)


if __name__ == "__main__":
    main()
