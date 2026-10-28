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

from blessed.keyboard import Keystroke

sys.path.insert(0, ".")

from ui.terminal.menu import Menu
from ui.terminal.menu_choice import MenuChoice
from ui.terminal.menu_entry import MenuEntry
from ui.terminal.menu_heading import MenuHeading


class TestMenu(TestCase):
    ENTER = Keystroke("\n", code=343, name="KEY_ENTER")
    ESCAPE = Keystroke("\x1b", code=361, name="KEY_ESCAPE")
    UP = Keystroke("", code=259, name="KEY_UP")
    DOWN = Keystroke("", code=258, name="KEY_DOWN")
    TAB = Keystroke("\t", code=512, name="KEY_TAB")
    QUIT_QUESTION = "Really quit? (y/n)"

    def setUp(self):
        self.entries = [MenuEntry(f"Layout {n}", n) for n in range(1, 7)]
        return super().setUp()

    # Choosing

    def test_the_first_entry_is_selected_at_first(self):
        self.assertEqual(self.__choose(self.ENTER), 1)
        self.assertIn("  [Layout 1]", self.__last_screen())

    def test_down_and_up_move_the_selection(self):
        self.assertEqual(self.__choose(self.DOWN, self.DOWN, self.UP, self.ENTER), 2)
        self.assertIn("  [Layout 2]", self.__last_screen())

    def test_up_on_the_first_entry_does_nothing(self):
        self.assertEqual(self.__choose(self.UP, self.ENTER), 1)

    def test_down_on_the_last_entry_does_nothing(self):
        self.assertEqual(self.__choose(*[self.DOWN] * 6, self.ENTER), 6)

    def test_other_keys_are_ignored(self):
        self.assertEqual(self.__choose("x", "5", self.ENTER), 1)

    def test_an_entry_that_cannot_be_picked_is_grayed_out_and_skipped(self):
        self.entries[0] = MenuEntry("Broken", 1, can_pick=False)
        self.entries[2] = MenuEntry("Broken", 3, can_pick=False)
        self.assertEqual(self.__choose(self.DOWN, self.ENTER), 4)
        self.assertIn("  <Broken>", self.__last_screen())

    def test_with_nothing_to_pick_nothing_is_selected_and_enter_picks_nothing(self):
        self.entries = [MenuEntry("Broken", 1, can_pick=False)]
        self.assertIsNone(self.__choose(self.DOWN, self.ENTER))
        self.assertNotIn("[", self.__last_screen())

    # Quitting

    def test_escape_asks_to_quit_and_y_quits(self):
        self.assertIsNone(self.__choose(self.ESCAPE, "y"))
        self.assertIn("Really quit? (y/n)", self.__last_screen())

    def test_q_asks_to_quit_too(self):
        self.assertIsNone(self.__choose("q", "Y"))
        self.assertIn("Really quit? (y/n)", self.__last_screen())

    def test_quit_not_confirmed_returns_to_the_menu(self):
        self.assertEqual(self.__choose(self.DOWN, "q", "n", self.ENTER), 2)
        self.assertNotIn("Really quit?", self.__last_screen())

    def test_ctrl_c_quits(self):
        self.assertIsNone(self.__choose(KeyboardInterrupt()))

    def test_ctrl_c_while_asking_to_quit_quits(self):
        self.assertIsNone(self.__choose("q", KeyboardInterrupt()))

    def test_without_a_quit_question_escape_and_q_leave_at_once(self):
        for key in (self.ESCAPE, "q"):
            self.assertIsNone(self.__choose(key, quit_question=None))
            self.assertNotIn(self.QUIT_QUESTION, self.__last_screen())

    # Headings and choices

    def test_a_heading_is_shown_but_skipped(self):
        self.entries = [MenuHeading("Group"), MenuEntry("Layout 1", 1)]
        self.assertEqual(self.__choose(self.UP, self.ENTER), 1)
        self.assertEqual(self.__item_lines(), ["  Group", "  [Layout 1]"])

    def test_the_selected_line_takes_the_keys_the_menu_does_not_use(self):
        choice = MenuChoice("Size", ["small", "large"])
        self.entries = [MenuHeading("Group"), choice]
        self.__choose(self.TAB, self.ESCAPE, quit_question=None)
        self.assertEqual(choice.chosen, 1)
        self.assertEqual(self.__item_lines()[1], "    [" + choice.text() + "]")

    def test_enter_on_a_choice_picks_nothing(self):
        self.entries = [MenuChoice("Size", ["small", "large"])]
        self.assertIsNone(self.__choose(self.ENTER, self.ESCAPE, quit_question=None))
        self.assertEqual(self.entries[0].chosen, 0)

    def test_shift_tab_read_as_two_keys_is_taken_as_one(self):
        choice = MenuChoice("Size", ["small", "medium", "large"])
        self.entries = [choice]
        shift_tab = [Keystroke("\x1b[", code=0, name="CSI"), Keystroke("Z")]
        self.__choose(*shift_tab, self.ESCAPE, quit_question=None)
        self.assertEqual(choice.chosen, 2)

    # The screen

    def test_the_title_and_the_keys_help_are_shown(self):
        self.__choose(self.ENTER)
        self.assertEqual(self.__last_screen()[:2], ["Pick one:", ""])
        self.assertEqual(self.__last_screen()[-1], "ENTER picks")

    def test_all_entries_are_shown_without_more_when_they_fit(self):
        self.__choose(self.ENTER)
        self.assertEqual(self.__shown_entries(), [f"Layout {n}" for n in range(1, 7)])
        self.assertNotIn(Menu.MORE, self.__last_screen())

    def test_entries_that_do_not_fit_leave_more_at_the_bottom(self):
        self.__choose(self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), ["  [Layout 1]", "  Layout 2", "  Layout 3", Menu.MORE])

    def test_moving_down_past_the_bottom_scrolls_a_line_and_shows_more_at_the_top(self):
        self.__choose(*[self.DOWN] * 3, self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  Layout 3", "  [Layout 4]", Menu.MORE])

    def test_more_at_the_bottom_goes_away_at_the_last_entry(self):
        self.__choose(*[self.DOWN] * 5, self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  Layout 4", "  Layout 5", "  [Layout 6]"])

    def test_more_at_the_top_goes_away_back_at_the_first_entry(self):
        self.__choose(*[self.DOWN] * 5, *[self.UP] * 5, self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), ["  [Layout 1]", "  Layout 2", "  Layout 3", Menu.MORE])

    def test_down_with_only_entries_that_cannot_be_picked_below_scrolls_them_into_view(self):
        self.entries[4] = MenuEntry("Broken", 5, can_pick=False)
        self.entries[5] = MenuEntry("Broken", 6, can_pick=False)
        self.__choose(*[self.DOWN] * 5, self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  [Layout 4]", "  <Broken>", "  <Broken>"])

    def test_a_selection_too_far_down_to_show_is_scrolled_into_view(self):
        self.entries = [MenuEntry("Broken", n, can_pick=False) for n in range(1, 6)] + [MenuEntry("Layout 6", 6)]
        self.__choose(self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  <Broken>", "  <Broken>", "  [Layout 6]"])

    def test_the_first_entry_to_pick_is_scrolled_only_until_it_is_the_last_line_shown(self):
        self.entries[:4] = [MenuEntry("Broken", n, can_pick=False) for n in range(1, 5)]
        self.entries.append(MenuEntry("Layout 7", 7))
        self.__choose(self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  <Broken>", "  [Layout 5]", Menu.MORE])

    def test_up_past_the_only_entry_to_pick_scrolls_the_entries_above_into_view_with_a_hint(self):
        self.entries = [MenuEntry(f"Broken {n}", n, can_pick=False) for n in range(1, 6)] + [MenuEntry("Layout 6", 6)]
        self.__choose(self.UP, KeyboardInterrupt(), height=9)
        self.assertEqual(self.__shown_entries(), ["---more---", "Broken 3", "Broken 4", "---more---"])
        self.assertEqual(self.__last_screen()[-2], Menu.HINT)

    def test_enter_with_the_highlighted_line_out_of_view_brings_it_back_without_picking_it(self):
        self.entries = [MenuEntry(f"Broken {n}", n, can_pick=False) for n in range(1, 6)] + [MenuEntry("Layout 6", 6)]
        self.assertIsNone(self.__choose(self.UP, self.UP, self.ENTER, "q", "y", height=9))
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  <Broken 4>", "  <Broken 5>", "  [Layout 6]"])
        self.assertEqual(self.__choose(self.UP, self.ENTER, self.ENTER, height=9), 6)

    def test_while_the_highlighted_line_is_out_of_view_up_and_down_only_scroll(self):
        broken = [MenuEntry(f"Broken {n}", n, can_pick=False) for n in range(1, 10)]
        self.entries = [MenuEntry("Layout 1", 1), *broken[1:4], MenuEntry("Layout 5", 5), *broken[5:]]
        self.assertEqual(self.__choose(*[self.DOWN] * 3, self.UP, self.ENTER, height=9), 5)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  [Layout 5]", "  <Broken 6>", Menu.MORE])
        self.assertEqual(self.__last_screen()[-2], "")

    def test_with_nothing_to_pick_down_scrolls_a_line(self):
        self.entries = [MenuEntry("Broken", n, can_pick=False) for n in range(1, 7)]
        self.__choose(self.DOWN, self.DOWN, self.ENTER, height=9)
        self.assertEqual(self.__item_lines(), [Menu.MORE, "  <Broken>", "  <Broken>", Menu.MORE])

    def test_with_nothing_to_pick_scrolling_stops_at_the_bottom_and_up_scrolls_back(self):
        self.entries = [MenuEntry(f"Broken {n}", n, can_pick=False) for n in range(1, 7)]
        self.__choose(*[self.DOWN] * 5, self.ENTER, height=9)
        self.assertEqual(self.__shown_entries(), ["---more---", "Broken 4", "Broken 5", "Broken 6"])
        self.__choose(*[self.DOWN] * 5, *[self.UP] * 3, self.ENTER, height=9)
        self.assertEqual(self.__shown_entries(), ["Broken 1", "Broken 2", "Broken 3", "---more---"])

    # Private functions

    def __choose(self, *keys, height=24, quit_question=QUIT_QUESTION):
        display = MagicMock()
        display.term.height = height
        display.term.yellow.side_effect = lambda text: text
        display.term.reverse.side_effect = lambda text: f"[{text}]"
        display.term.gray50.side_effect = lambda text: f"<{text}>"
        display.term.inkey.side_effect = [Keystroke(key) if type(key) is str else key for key in keys]
        with patch("ui.terminal.menu.echo") as self.echo:
            return Menu("Pick one:", self.entries, "ENTER picks", display, quit_question).choose()

    def __last_screen(self) -> list:
        return str(self.echo.call_args_list[-1].args[0]).split("\n")

    def __item_lines(self) -> list:
        """The lines between the title's blank line and the blank line above the message"""
        return self.__last_screen()[2:-3]

    def __shown_entries(self) -> list:
        return [line.strip(" []<>") for line in self.__item_lines()]


if __name__ == "__main__":
    main()
