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

from game.cell import Cell
from game.house import House
from game.rectangular_block import RectangularBlock


class TestRectangularBlock(TestCase):
    BLOCK_ROWS = 3
    BLOCK_COLS = 3

    def setUp(self):
        self.__setup_parent()
        self.block = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        return super().setUp()

    def test_cell_changes_are_passed_on_to_the_parent(self):
        cell = self.block.cell(1, 7)
        self.block.cell_changed(cell)
        self.parent.cell_changed.assert_called_once_with(cell)

    def test_houses_of_a_cell_are_its_box_then_its_row_and_column_from_the_parent(self):
        row_cells, col_cells = [self.__other_cell()], [self.__other_cell()]
        self.parent.cells_in_row.return_value = row_cells
        self.parent.cells_in_col.return_value = col_cells
        box, row, col = self.block.houses_of(1, 7)
        self.assertEqual((box.kind, row.kind, col.kind), (House.BOX, House.ROW, House.COLUMN))
        self.assertEqual(sorted((c.row, c.col) for c in box.cells), [(r, c) for r in range(3) for c in range(6, 9)])
        self.assertEqual((row.cells, col.cells), (row_cells, col_cells))
        self.parent.cells_in_row.assert_called_once_with(1)
        self.parent.cells_in_col.assert_called_once_with(7)

    def test_box_is_the_house_of_every_cell_in_the_block(self):
        box = self.block.box()
        self.assertEqual(box.kind, House.BOX)
        self.assertEqual(sorted((c.row, c.col) for c in box.cells), [(r, c) for r in range(3) for c in range(6, 9)])

    def test_houses_of_asks_parent_only_after_the_box(self):
        houses = self.block.houses_of(1, 7)
        next(houses)
        self.parent.cells_in_row.assert_not_called()
        self.parent.cells_in_col.assert_not_called()

    def test_related_cells_are_the_other_cells_in_the_block_then_the_parents_row_and_col_cells(self):
        row_cell, col_cell = self.__other_cell(), self.__other_cell()
        self.parent.cells_in_row.return_value = [row_cell]
        self.parent.cells_in_col.return_value = [col_cell]
        related = list(self.block.related_cells(1, 7))
        positions = [(cell.row, cell.col) for cell in related[:-2]]
        self.assertEqual(sorted(positions), [(r, c) for r in range(3) for c in range(6, 9) if (r, c) != (1, 7)])
        self.assertEqual(related[-2:], [row_cell, col_cell])

    def test_related_cells_yields_each_cell_once(self):
        own_cell, other_cell = self.block.cell(1, 6), self.__other_cell()
        self.parent.cells_in_row.return_value = [own_cell, other_cell]
        self.parent.cells_in_col.return_value = [other_cell]
        related = list(self.block.related_cells(1, 7))
        self.assertEqual((related.count(own_cell), related.count(other_cell)), (1, 1))

    def test_related_cells_leaves_out_the_cell_itself(self):
        cell = self.block.cell(1, 7)
        self.parent.cells_in_row.return_value = [cell]
        self.parent.cells_in_col.return_value = [cell]
        self.assertNotIn(cell, list(self.block.related_cells(1, 7)))

    def test_related_cells_asks_parent_only_after_the_block_cells(self):
        related = self.block.related_cells(1, 7)
        for _ in range(8):
            next(related)
        self.parent.cells_in_row.assert_not_called()

    def test_cells_where_yields_only_cells_matching_the_condition(self):
        self.__leave_only(self.block.cell(1, 7), {4})
        self.__leave_only(self.block.cell(2, 6), set())
        self.assertEqual([(c.row, c.col) for c in self.block.cells_where(Cell.single_possible_value)], [(1, 7)])
        self.assertEqual([(c.row, c.col) for c in self.block.cells_where(Cell.is_dead_end)], [(2, 6)])

    def test_cells_in_row_yields_block_cells_in_that_row_left_to_right(self):
        self.assertEqual([(cell.row, cell.col) for cell in self.block.cells_in_row(1)], [(1, 6), (1, 7), (1, 8)])

    def test_cells_in_col_yields_block_cells_in_that_column_top_to_bottom(self):
        self.assertEqual([(cell.row, cell.col) for cell in self.block.cells_in_col(7)], [(0, 7), (1, 7), (2, 7)])

    def test_cells_in_row_or_col_yield_nothing_when_the_block_is_not_in_line(self):
        self.assertEqual((list(self.block.cells_in_row(5)), list(self.block.cells_in_col(0))), ([], []))

    # Private functions

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        1. cells_in_row() and cells_in_col() - the puzzle's cells in a given row or column
        """
        self.parent = MagicMock()
        self.parent.cells_in_row.return_value = []
        self.parent.cells_in_col.return_value = []

    def __other_cell(self):
        """A cell outside this block"""
        return MagicMock(row=8, col=7)

    def __leave_only(self, cell, values):
        for value in set(self.block.values()) - values:
            cell.remove_possible(value)

if __name__ == "__main__":
    main()
