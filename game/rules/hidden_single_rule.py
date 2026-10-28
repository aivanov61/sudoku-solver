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

from game.cell import Cell
from game.rules.rule import Move, Outcome, Rule



class HiddenSingleRule(Rule):
    """A value that can go in only one cell of a box, row or column must go there"""

    NAME = "hidden single"

    def find(self, puzzle) -> Move:
        cell = puzzle.first_cell_where(Cell.hidden_single)
        if cell is None:
            return None
        value, house = cell.hidden_single()
        return self._move(Outcome.MOVED, f"{value} fits nowhere else in its {house.kind}.", cell, value)
