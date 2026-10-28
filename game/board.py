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

from abc import ABC, abstractmethod

sys.path.insert(0, ".")

from game.cell import Cell
from game.cell_attrs import CellAttrs


class Board(ABC):
    """
    The grid of cells, laid out in blocks: where each cell is and what the cells hold.

    Each layout is a subclass in the puzzles folder with a NAME shown to the player, which builds its blocks
    and implements _blocks() and _block_at(). Only blocks look inside cells to find them: the board asks
    every block, because in other layouts the blocks may not form a regular grid.
    """

    def __init__(self, v_cells: int, h_cells: int):
        self.v_cells = v_cells
        self.h_cells = h_cells
        self.__listener = lambda cell: None  # hears of every change to a cell

    # Interface required for the puzzle

    def report_changes_to(self, listener) -> None:
        """Have listener(cell) called whenever a cell's value, attributes or possible values change"""
        self.__listener = listener

    def cells(self) -> list:
        """Return every cell, left to right and top to bottom"""
        return self.cells_where(lambda cell: True)

    def cell(self, row, col) -> Cell:
        return self._block_at(row, col).cell(row, col)

    def cells_where(self, condition) -> list:
        """Return the cells for which condition(cell) is true, left to right and top to bottom"""
        cells = (cell for block in self._blocks() for cell in block.cells_where(condition))
        return sorted(cells, key=lambda cell: (cell.row, cell.col))

    def first_cell_where(self, condition) -> Cell:
        """Return the first cell, left to right and top to bottom, for which condition(cell) is true, or None"""
        return next(iter(self.cells_where(condition)), None)

    def is_full(self) -> bool:
        return self.first_cell_where(lambda cell: cell.value() is None) is None

    def has_values(self) -> bool:
        return self.first_cell_where(lambda cell: cell.value() is not None) is not None

    def has_conflicts(self) -> bool:
        return self.first_cell_where(Cell.is_marked_in_conflict) is not None

    def givens(self) -> list:
        """Return (row, col, value) for each value entered while setting up the puzzle"""
        is_given = lambda cell: CellAttrs.INITIAL in cell.attr()
        return [(cell.row, cell.col, cell.value()) for cell in self.cells_where(is_given)]

    def clear(self) -> None:
        """Empty every cell"""
        for cell in self.cells_where(lambda cell: cell.value() is not None):
            cell.set(None)

    # Interface required for blocks

    def cells_in_row(self, row):
        """Yield the cells in the given row, left to right, as identified by each block"""
        for block in self._blocks():
            yield from block.cells_in_row(row)

    def cells_in_col(self, col):
        """Yield the cells in the given column, top to bottom, as identified by each block"""
        for block in self._blocks():
            yield from block.cells_in_col(col)

    def cell_changed(self, cell) -> None:
        self.__listener(cell)

    # Interface required from layout subclasses

    @abstractmethod
    def _blocks(self):
        """Yield every block of the layout"""

    @abstractmethod
    def _block_at(self, row, col):
        """Return the block that holds the cell at the given board row and column"""
