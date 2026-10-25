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
        for cell in self.__cells():
            cell.render()

    def cell(self, row, col) -> Cell:
        return self._cells[row % self.rows][col % self.cols]

    def remove_possible_in_row_and_col(self, row, col, value) -> None:
        for cell in self.__cells_in_row_or_col(row, col):
            cell.remove_possible(value)

    def has_value_in_row_or_col(self, row, col, value) -> bool:
        return self.__holds_value(self.__cells_in_row_or_col(row, col), row, col, value)

    # Interface required for cell instances

    def values(self) -> range:
        return range(1, self.rows * self.cols + 1)

    def add_possible(self, row, col, value) -> None:
        pass

    def remove_possible(self, row, col, value) -> None:
        for cell in self.__cells():
            cell.remove_possible(value)
        self.parent.remove_possible(row, col, value)

    def is_conflicting(self, row, col, value) -> bool:
        return self.__holds_value(self.__cells(), row, col, value) or self.parent.is_conflicting(row, col, value)

    # Private functions

    def __initialize_cells(self):
        self._cells = [[None for _col in range(self.cols)] for _row in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                self._cells[row][col] = Cell(parent=self, **self.__phys_pos(row, col), borders=self.BORDERS[row][col])

    def __phys_pos(self, row, col):
        return {
            "row": self.block_row * self.rows + row,
            "col": self.block_col * self.cols + col,
        }

    def __cells(self):
        return (cell for cells in self._cells for cell in cells)

    def __cells_in_row_or_col(self, row, col):
        return (cell for cell in self.__cells() if cell.row == row or cell.col == col)

    def __holds_value(self, cells, row, col, value) -> bool:
        """Return True if any of the cells, other than the one at row, col, holds the value"""
        return any(cell.value() == value and (cell.row, cell.col) != (row, col) for cell in cells)
