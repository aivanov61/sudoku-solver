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
from rules.conflicts_rule import ConflictsRule
from rules.rule import Outcome


class TestConflictsRule(TestCase):
    def test_no_conflict_means_no_move(self):
        move, puzzle = find_with(ConflictsRule(), cell=None)
        self.assertIsNone(move)
        puzzle.first_cell_where.assert_called_once_with(Cell.is_marked_in_conflict)

    def test_a_conflict_stops_solving_with_a_warning(self):
        move, _puzzle = find_with(ConflictsRule(), cell=MagicMock())
        self.assertIs(move.outcome, Outcome.STOPPED)
        self.assertIn("Resolve the conflicts first", move.hint)
        self.assertIsNone(move.cell)


if __name__ == "__main__":
    main()
