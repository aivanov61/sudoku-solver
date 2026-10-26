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
from rule_test_helper import apply_rule
from rules.rule import Outcome
from rules.single_value_rule import SingleValueRule


class TestSingleValueRule(TestCase):
    def test_no_single_value_cell_means_nothing_to_do(self):
        outcome, puzzle, _warn = apply_rule(SingleValueRule(), cell=None)
        self.assertIs(outcome, Outcome.NONE)
        puzzle.first_cell_where.assert_called_once_with(Cell.single_possible_value)
        puzzle.enter_solved_value.assert_not_called()

    def test_a_single_value_cell_is_selected_and_filled_in(self):
        cell = MagicMock()
        cell.single_possible_value.return_value = 7
        outcome, puzzle, _warn = apply_rule(SingleValueRule(), cell=cell)
        self.assertIs(outcome, Outcome.MOVED)
        puzzle.select.assert_called_once_with(cell)
        puzzle.enter_solved_value.assert_called_once_with(cell, 7)


if __name__ == "__main__":
    main()
