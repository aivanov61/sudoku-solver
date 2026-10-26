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

sys.path.insert(0, ".")

from cell import Cell
from rules.rule import Outcome, Rule


class SingleValueRule(Rule):
    """A cell with only one possible value must hold that value"""

    def apply(self, puzzle) -> Outcome:
        cell = puzzle.first_cell_where(Cell.single_possible_value)
        if cell is None:
            return Outcome.NONE
        puzzle.select(cell)
        puzzle.enter_solved_value(cell, cell.single_possible_value())
        return Outcome.MOVED
