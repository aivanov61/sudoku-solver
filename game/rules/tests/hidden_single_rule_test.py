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
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from game.cell import Cell
from game.house import House
from game.rules.tests.rule_test_helper import find_with
from game.rules.hidden_single_rule import HiddenSingleRule
from game.rules.rule import Outcome


class TestHiddenSingleRule(TestCase):
    def test_no_hidden_single_means_no_move(self):
        move, puzzle = find_with(HiddenSingleRule(), cell=None)
        self.assertIsNone(move)
        puzzle.first_cell_where.assert_called_once_with(Cell.hidden_single)

    def test_a_hidden_single_is_the_move_with_a_hint_naming_its_house(self):
        cell = MagicMock()
        cell.hidden_single.return_value = (4, House(House.ROW, []))
        move, puzzle = find_with(HiddenSingleRule(), cell=cell)
        self.assertIs(move.outcome, Outcome.MOVED)
        self.assertIs(move.cell, cell)
        self.assertEqual(move.value, 4)
        self.assertEqual(move.hint, "4 fits nowhere else in its row. [hidden single] ")
        puzzle.enter_solved_value.assert_not_called()


if __name__ == "__main__":
    main()
