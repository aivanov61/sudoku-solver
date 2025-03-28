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
from display import Border


class RectangularBlock:
    """
    Manage a rectangular block of cells where every block in the puzzle is the
    same size.

    The size and position of the block are provided during instantiation.
    """

    # fmt: off
    BORDERS = [
        [ Border({Border.TOP, Border.LEFT}),    Border({Border.TOP}),    Border({Border.TOP, Border.RIGHT}) ],
        [ Border({Border.LEFT}),                Border(),                Border({Border.RIGHT}) ],
        [ Border({Border.BOTTOM, Border.LEFT}), Border({Border.BOTTOM}), Border({Border.BOTTOM, Border.RIGHT}) ],
    ]
    # fmt: on

    def __init__(self, parent, row, col, rows=0, cols=0):
        self.parent = parent
        self.block_row = row
        self.block_col = col
        self.rows = rows
        self.cols = cols
        self.__initialize_cells()

    # Interface required for puzzles (arrangement of rectangular blocks)

    def render(self) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                self._cells[row][col].render()

    def cell(self, row, col) -> Cell:
        return self._cells[row % self.rows][col % self.cols]

    # Interface required for cell instances

    def values(self) -> range:
        return range(1, self.rows * self.cols + 1)

    def add_possible(self, row, col, value) -> None:
        pass

    def remove_possible(self, row, col, value) -> None:
        pass

    # Private functions

    def __initialize_cells(self):
        self._cells = [[None for _col in range(self.rows)] for _row in range(self.cols)]
        for row in range(self.rows):
            for col in range(self.cols):
                self._cells[row][col] = Cell(parent=self, **self.__phys_pos(row, col), borders=self.BORDERS[row][col])

    def __phys_pos(self, row, col):
        return {
            "row": self.block_row * self.rows + row,
            "col": self.block_col * self.cols + col,
        }
