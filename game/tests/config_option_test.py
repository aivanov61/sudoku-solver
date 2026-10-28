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

from game.config_option import ConfigOption


class TestConfigOption(TestCase):
    OPTION = ConfigOption("Group", "Size", (("small", 1), ("medium", 2), ("large", 3)), 2)

    def test_labels_are_the_choices_in_order(self):
        self.assertEqual(self.OPTION.labels(), ["small", "medium", "large"])

    def test_the_chosen_index_is_where_the_value_is_among_the_choices(self):
        self.assertEqual(self.OPTION.chosen_index(), 1)

    def test_an_option_has_no_notes_unless_given_them(self):
        self.assertEqual((self.OPTION.notes, self.OPTION.note_action), ((), None))

    def test_with_choice_returns_the_option_with_that_choice_made(self):
        self.assertEqual(self.OPTION.with_choice(2).value, 3)
        self.assertEqual(self.OPTION.value, 2)


if __name__ == "__main__":
    main()
