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

from border import Border
from cell import Cell


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

    # Interface required for boards

    def cell(self, row, col) -> Cell:
        return self._cells[row % self.rows][col % self.cols]

    def cells_in_row_or_col(self, row, col):
        """Yield the cells of this block that are in the given puzzle row or column"""
        yield from self.cells_where(lambda cell: cell.row == row or cell.col == col)

    def cells_where(self, condition):
        """Yield the cells of this block for which condition(cell) is true"""
        yield from (cell for cell in self.__cells() if condition(cell))

    # Interface required for cells

    def values(self) -> range:
        return range(1, self.rows * self.cols + 1)

    def cell_changed(self, cell) -> None:
        self.parent.cell_changed(cell)

    def related_cells(self, row, col):
        """Yield, once each, every other cell in the same block, row or column as the cell at row, col"""
        block_cells = list(self.__cells())
        yield from (cell for cell in block_cells if (cell.row, cell.col) != (row, col))
        yield from (cell for cell in self.parent.cells_in_row_or_col(row, col) if cell not in block_cells)

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
