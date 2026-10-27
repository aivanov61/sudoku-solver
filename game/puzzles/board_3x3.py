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

from game.board import Board
from game.rectangular_block import RectangularBlock


class Board3x3(Board):
    """
    The standard 9x9 Sudoku layout: nine 3x3 blocks, three across and three down.

    The blocks are built with the board as their parent. They form a regular grid, so a cell's block
    is found by dividing its row and column by the block size.
    """

    NAME = "Standard 9x9"
    H_BLOCKS = 3  # columns
    V_BLOCKS = 3  # rows

    def __init__(self):
        super().__init__(v_cells=self.V_BLOCKS**2, h_cells=self.H_BLOCKS**2)
        self.__block_grid = [
            [
                RectangularBlock(self, row=block_row, col=block_col, rows=self.V_BLOCKS, cols=self.H_BLOCKS)
                for block_col in range(self.H_BLOCKS)
            ]
            for block_row in range(self.V_BLOCKS)
        ]

    # Interface required for Board

    def _blocks(self):
        return (block for blocks in self.__block_grid for block in blocks)

    def _block_at(self, row, col):
        return self.__block_grid[row // self.V_BLOCKS][col // self.H_BLOCKS]
