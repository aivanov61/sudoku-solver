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

from cell import Cell
from rule_test_helper import find_with
from rules.rule import Outcome
from rules.single_value_rule import SingleValueRule


class TestSingleValueRule(TestCase):
    def test_no_single_value_cell_means_no_move(self):
        move, puzzle = find_with(SingleValueRule(), cell=None)
        self.assertIsNone(move)
        puzzle.first_cell_where.assert_called_once_with(Cell.single_possible_value)

    def test_a_single_value_cell_is_the_move_with_a_hint(self):
        cell = MagicMock()
        cell.single_possible_value.return_value = 7
        move, puzzle = find_with(SingleValueRule(), cell=cell)
        self.assertIs(move.outcome, Outcome.MOVED)
        self.assertIs(move.cell, cell)
        self.assertEqual(move.value, 7)
        self.assertEqual(move.hint, "Only 7 fits here: every other value is already in its row, column or box.")
        puzzle.enter_solved_value.assert_not_called()


if __name__ == "__main__":
    main()
