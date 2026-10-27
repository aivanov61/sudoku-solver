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
from rules.rule import Move, Outcome, Rule


class SingleValueRule(Rule):
    """A cell with only one possible value must hold that value"""

    def find(self, puzzle) -> Move:
        cell = puzzle.first_cell_where(Cell.single_possible_value)
        if cell is None:
            return None
        value = cell.single_possible_value()
        hint = f"Only {value} fits here: every other value is already in its row, column or box."
        return Move(Outcome.MOVED, hint, cell, value)
