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
from rules.dead_end_rule import DeadEndRule
from rules.rule import Outcome


class TestDeadEndRule(TestCase):
    def test_no_dead_end_means_no_move(self):
        move, puzzle = find_with(DeadEndRule(), cell=None)
        self.assertIsNone(move)
        puzzle.first_cell_where.assert_called_once_with(Cell.is_dead_end)

    def test_a_dead_end_stops_solving_with_a_warning_at_that_cell(self):
        cell = MagicMock()
        move, puzzle = find_with(DeadEndRule(), cell=cell)
        self.assertIs(move.outcome, Outcome.STOPPED)
        self.assertIs(move.cell, cell)
        self.assertIn("try undoing until this square shows at least one possible value", move.hint)
        puzzle.select.assert_not_called()


if __name__ == "__main__":
    main()
