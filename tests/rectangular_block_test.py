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
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from cell import Cell
from rectangular_block import RectangularBlock


class TestRectangularBlock(TestCase):
    BLOCK_ROWS = 3
    BLOCK_COLS = 3

    def setUp(self):
        self.__setup_parent()
        self.block = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        return super().setUp()

    def test_block_can_render(self):
        block1 = RectangularBlock(self.parent, 0, 0, self.BLOCK_ROWS, self.BLOCK_COLS)
        block2 = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        block1.render()
        block2.render()

    def test_related_cells_are_the_other_cells_in_the_block_then_the_parents_row_and_col_cells(self):
        other_cell = self.__other_cell()
        self.parent.cells_in_row_or_col.return_value = [other_cell]
        related = list(self.block.related_cells(1, 7))
        positions = [(cell.row, cell.col) for cell in related[:-1]]
        self.assertEqual(sorted(positions), [(r, c) for r in range(3) for c in range(6, 9) if (r, c) != (1, 7)])
        self.assertIs(related[-1], other_cell)
        self.parent.cells_in_row_or_col.assert_called_once_with(1, 7)

    def test_related_cells_skips_parent_cells_that_are_in_this_block(self):
        own_cell = self.block.cell(1, 6)
        self.parent.cells_in_row_or_col.return_value = [own_cell]
        related = list(self.block.related_cells(1, 7))
        self.assertEqual(related.count(own_cell), 1)

    def test_related_cells_asks_parent_only_after_the_block_cells(self):
        related = self.block.related_cells(1, 7)
        for _ in range(8):
            next(related)
        self.parent.cells_in_row_or_col.assert_not_called()

    def test_cells_where_yields_only_cells_matching_the_condition(self):
        self.__leave_only(self.block.cell(1, 7), {4})
        self.__leave_only(self.block.cell(2, 6), set())
        self.assertEqual([(c.row, c.col) for c in self.block.cells_where(Cell.single_possible_value)], [(1, 7)])
        self.assertEqual([(c.row, c.col) for c in self.block.cells_where(Cell.is_dead_end)], [(2, 6)])

    def test_cells_in_row_or_col_yields_block_cells_in_that_row_or_col(self):
        cells = self.block.cells_in_row_or_col(1, 7)
        self.assertEqual({(cell.row, cell.col) for cell in cells}, {(1, 6), (1, 7), (1, 8), (0, 7), (2, 7)})

    def test_cells_in_row_or_col_handles_row_outside_block(self):
        cells = self.block.cells_in_row_or_col(5, 7)
        self.assertEqual({(cell.row, cell.col) for cell in cells}, {(0, 7), (1, 7), (2, 7)})

    def test_cells_in_row_or_col_yields_nothing_when_block_is_not_in_line(self):
        self.assertEqual(list(self.block.cells_in_row_or_col(5, 0)), [])

    # Private functions

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        1. cells_in_row_or_col() - the puzzle's cells in a given row or column
        """
        self.parent = MagicMock()
        self.parent.cells_in_row_or_col.return_value = []

    def __other_cell(self, value=None):
        """A cell outside this block, in row 8 of column 7"""
        cell = MagicMock(row=8, col=7)
        cell.value.return_value = value
        return cell

    def __leave_only(self, cell, values):
        for value in set(self.block.values()) - values:
            cell.remove_possible(value)

if __name__ == "__main__":
    main()
