# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import sys
sys.path.insert(0, '.')

from cell import Cell
from display import Border

class RectangularBlock:
    """
    Manage a rectangular block of cells where every block in the puzzle is the
    same size.

    The size and position of the block are provided during instantiation.
    """
    BORDERS= [
        [ Border({Border.TOP,Border.LEFT}),    Border({Border.TOP}),    Border({Border.TOP,Border.RIGHT}) ],
        [ Border({Border.LEFT}),               Border(),                Border({Border.RIGHT}) ],
        [ Border({Border.LEFT,Border.BOTTOM}), Border({Border.BOTTOM}), Border({Border.RIGHT,Border.BOTTOM}) ],
    ]

    def __init__(self, parent, row, col, rows=0, cols=0):
        self.parent = parent
        self.block_row = row
        self.block_col = col
        self.rows = rows
        self.cols = cols
        self.__initialize_cells()

    def __initialize_cells(self):
        self._cells = [[None for _col in range(self.rows)] for _row in range(self.cols)]
        for row in range(self.rows):
            for col in range(self.cols):
                self._cells[row][col] = Cell(parent=self, **self.phys_pos(row, col), borders=self.BORDERS[row][col])

    def phys_pos(self, row, col):
        return {
            'row': self.block_row * self.rows + row,
            'col': self.block_col * self.cols + col
        }

    def render(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self._cells[row][col].render()

    def cell(self, row, col):
        return self._cells[row % self.rows ][col % self.cols]

    def values(self):
        return range(1, self.rows * self.cols + 1)
