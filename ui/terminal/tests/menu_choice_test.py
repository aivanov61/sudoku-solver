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

sys.path.insert(0, ".")

from ui.terminal.menu_choice import MenuChoice


class TestMenuChoice(TestCase):
    def setUp(self):
        self.choice = MenuChoice("Size", ["small", "medium", "large"], chosen=1)
        return super().setUp()

    def test_shows_its_name_dotted_out_then_the_choice_and_where_it_is_among_them(self):
        self.assertEqual(self.choice.text(), "Size " + "." * (MenuChoice.NAME_WIDTH - 5) + " medium (2 of 3)")

    def test_tab_and_right_move_to_the_next_choice(self):
        for key in ("KEY_TAB", "KEY_RIGHT"):
            self.choice.handle(key)
        self.assertEqual(self.choice.chosen, 0)

    def test_shift_tab_and_left_move_to_the_previous_choice(self):
        for key in ("KEY_BTAB", "KEY_LEFT"):
            self.choice.handle(key)
        self.assertEqual(self.choice.chosen, 2)

    def test_other_keys_and_enter_change_nothing(self):
        for key in ("KEY_ENTER", "x", "5"):
            self.choice.handle(key)
        self.assertEqual(self.choice.chosen, 1)

    def test_enter_picks_it_with_the_index_chosen(self):
        self.assertEqual((self.choice.is_picked_by_enter(), self.choice.value), (True, 1))


if __name__ == "__main__":
    main()
