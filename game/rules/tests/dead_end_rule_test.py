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
from unittest.mock import call, MagicMock

sys.path.insert(0, ".")

from game.cell import Cell
from game.house import House
from game.rules.tests.rule_test_helper import find_with
from game.rules.dead_end_rule import DeadEndRule
from game.rules.rule import Outcome


class TestDeadEndRule(TestCase):
    def test_no_dead_end_means_no_move(self):
        move, puzzle = find_with(DeadEndRule(), cell=None)
        self.assertIsNone(move)
        self.assertEqual(
            puzzle.first_cell_where.call_args_list, [call(Cell.is_dead_end), call(Cell.unplaceable_value)]
        )

    def test_a_dead_end_stops_solving_with_a_warning_at_that_cell(self):
        cell = MagicMock()
        move, puzzle = find_with(DeadEndRule(), cell=cell)
        self.assertIs(move.outcome, Outcome.STOPPED)
        self.assertIs(move.cell, cell)
        self.assertEqual(move.hint, "Dead end; try either undoing or rewinding-back-to-a-previous-guess. [dead end] ")
        self.assertIsNone(move.value)
        puzzle.select.assert_not_called()

    def test_a_value_with_no_place_left_in_a_house_stops_solving_at_the_cell_found(self):
        cell, row = MagicMock(), House(House.ROW, [])
        cell.unplaceable_value.return_value = (4, row)
        puzzle = MagicMock()
        puzzle.first_cell_where.side_effect = lambda condition: cell if condition is Cell.unplaceable_value else None
        move = DeadEndRule().find(puzzle)
        self.assertIs(move.outcome, Outcome.STOPPED)
        self.assertEqual((move.cell, move.value, move.house), (cell, 4, row))
        self.assertEqual(move.hint, "Dead end; try either undoing or rewinding-back-to-a-previous-guess. [dead end] ")


if __name__ == "__main__":
    main()
