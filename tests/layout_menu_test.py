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

from blessed.keyboard import Keystroke

sys.path.insert(0, ".")

from display import Display
from layout_menu import LayoutMenu
from puzzle_catalog import PuzzleLayout


class TestLayoutMenu(TestCase):
    ENTER = Keystroke("\n", code=343, name="KEY_ENTER")
    BACKSPACE = Keystroke("\b", code=263, name="KEY_BACKSPACE")

    def setUp(self):
        playable = [PuzzleLayout(f"Layout {n}", puzzle_class=object) for n in range(2, 6)]
        self.layouts = [PuzzleLayout("bad.py")] + playable
        return super().setUp()

    def test_number_and_enter_chooses_that_layout(self):
        self.assertIs(self.__choose("3", self.ENTER), self.layouts[2])

    def test_number_without_enter_does_not_choose(self):
        self.assertIsNone(self.__choose("3", "q", "y"))

    def test_backspace_corrects_the_number(self):
        self.assertIs(self.__choose("4", self.BACKSPACE, "2", self.ENTER), self.layouts[1])

    def test_broken_layout_is_rejected_and_another_can_be_chosen(self):
        self.assertIs(self.__choose("1", self.ENTER, "2", self.ENTER), self.layouts[1])
        self.assertIn("bad.py (broken: could not be loaded) can't be started", self.__drawn())

    def test_number_outside_the_list_is_rejected(self):
        self.assertIsNone(self.__choose("9", self.ENTER, "q", "y"))
        self.assertIn("There is no layout 9", self.__drawn())

    def test_number_with_more_digits_than_the_layouts_can_be_typed(self):
        self.assertIsNone(self.__choose("1", "0", self.ENTER, "q", "y"))
        self.assertIn("There is no layout 10", self.__drawn())

    def test_number_not_listed_is_reported_without_leading_zeros(self):
        self.__choose(*"000000000", self.ENTER, "0", "0", "1", "0", self.ENTER, "q", "y")
        self.assertIn("There is no layout 0\n", self.__drawn())
        self.assertIn("There is no layout 10\n", self.__drawn())

    def test_digits_beyond_nine_mark_the_number_too_big(self):
        self.__choose(*"1234567890", "q", "y")
        self.assertTrue(self.__last_drawn().endswith("123456789..."))

    def test_number_too_big_is_rejected(self):
        self.assertIsNone(self.__choose(*"1234567890", self.ENTER, "q", "y"))
        self.assertIn("Number too big", self.__drawn())

    def test_backspace_removes_the_too_big_mark_first(self):
        self.__choose(*"1234567890", self.BACKSPACE, "q", "y")
        self.assertTrue(self.__last_drawn().endswith("123456789"))

    def test_backspace_then_removes_digits(self):
        self.__choose(*"1234567890", self.BACKSPACE, self.BACKSPACE, "q", "y")
        self.assertTrue(self.__last_drawn().endswith("12345678"))

    def test_another_digit_after_backspace_marks_it_too_big_again(self):
        self.__choose(*"1234567890", self.BACKSPACE, "5", "q", "y")
        self.assertTrue(self.__last_drawn().endswith("123456789..."))

    def test_q_quits(self):
        self.assertIsNone(self.__choose("q", "y"))

    def test_quit_asks_for_confirmation(self):
        self.__choose("q", "y")
        self.assertIn("Really quit? (y/n)", self.__drawn())

    def test_quit_not_confirmed_returns_to_the_menu(self):
        self.assertIs(self.__choose("q", "n", "2", self.ENTER), self.layouts[1])

    def test_ctrl_c_while_asking_to_quit_quits(self):
        self.assertIsNone(self.__choose("q", KeyboardInterrupt()))

    def test_ctrl_c_quits(self):
        self.assertIsNone(self.__choose(KeyboardInterrupt()))

    def test_prompt_asks_for_number_and_enter(self):
        self.__choose("q", "y")
        self.assertIn("Layout number (1-5) + ENTER, or (q)uit: ", self.__drawn())

    def test_all_layouts_fit_on_one_page_when_there_is_room(self):
        self.__choose("q", "y")
        self.assertIn("  5. Layout 5", self.__drawn())
        self.assertNotIn("(n)ext", self.__drawn())

    def test_layouts_that_do_not_fit_are_split_into_pages(self):
        self.__choose("q", "y", height=7)
        self.assertIn("page 1 of 3", self.__drawn())
        self.assertIn("  2. Layout 2", self.__drawn())
        self.assertNotIn("  3. Layout 3", self.__drawn())
        self.assertIn("(p)revious, (n)ext, or (q)uit", self.__drawn())

    def test_next_shows_the_next_page(self):
        self.__choose("n", "q", "y", height=7)
        self.assertIn("page 2 of 3", self.__last_drawn())
        self.assertIn("  3. Layout 3", self.__last_drawn())

    def test_previous_on_the_first_page_does_nothing(self):
        self.__choose("p", "q", "y", height=7)
        self.assertIn("page 1 of 3", self.__last_drawn())

    def test_next_on_the_last_page_does_nothing(self):
        self.__choose("n", "n", "n", "q", "y", height=7)
        self.assertIn("page 3 of 3", self.__last_drawn())

    def test_a_layout_on_another_page_can_be_chosen_by_number(self):
        self.assertIs(self.__choose("5", self.ENTER, height=7), self.layouts[4])

    # Private functions

    def __choose(self, *keys, height=24):
        with patch("layout_menu.echo") as self.echo, patch.object(Display, "term") as term:
            term.height = height
            term.yellow.side_effect = lambda text: text
            term.inkey.side_effect = [Keystroke(key) if type(key) is str else key for key in keys]
            return LayoutMenu(self.layouts).choose()

    def __drawn(self) -> str:
        return "".join(str(call.args[0]) for call in self.echo.call_args_list)

    def __last_drawn(self) -> str:
        return str(self.echo.call_args_list[-1].args[0])


if __name__ == "__main__":
    main()
