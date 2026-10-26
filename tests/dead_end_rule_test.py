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
from rules.dead_end_rule import DeadEndRule
from rules.rule import Outcome


class TestDeadEndRule(TestCase):
    def test_no_dead_end_means_nothing_to_do(self):
        outcome, puzzle, warn = apply_rule(DeadEndRule(), cell=None)
        self.assertIs(outcome, Outcome.NONE)
        puzzle.first_cell_where.assert_called_once_with(Cell.is_dead_end)
        warn.assert_not_called()

    def test_a_dead_end_is_selected_and_stops_solving_with_a_warning(self):
        cell = MagicMock()
        outcome, puzzle, warn = apply_rule(DeadEndRule(), cell=cell)
        self.assertIs(outcome, Outcome.STOPPED)
        puzzle.select.assert_called_once_with(cell)
        self.assertIn("try undoing until this square shows at least one possible value", warn.call_args.args[0])


if __name__ == "__main__":
    main()
