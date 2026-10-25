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

from rectangular_block import RectangularBlock


class TestRectangularBlock(TestCase):

    def setUp(self):
        self.__setup_parent()
        self.block = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        return super().setUp()

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        1. cells_in_row_or_col() - the puzzle's cells in a given row or column
        """
        self.parent = MagicMock()
        self.parent.cells_in_row_or_col.return_value = []

    BLOCK_ROWS = 3
    BLOCK_COLS = 3

    def test_block_can_render(self):
        block1 = RectangularBlock(self.parent, 0, 0, self.BLOCK_ROWS, self.BLOCK_COLS)
        block2 = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        block1.render()
        block2.render()

    def test_remove_possible_removes_value_from_every_other_cell_in_block(self):
        self.block.remove_possible(1, 7, 5)
        for row in range(self.BLOCK_ROWS):
            for col in range(6, 6 + self.BLOCK_COLS):
                if (row, col) != (1, 7):
                    self.assertNotIn(5, self.block.cell(row, col).possible_values())

    def test_remove_possible_leaves_other_values_possible(self):
        self.block.remove_possible(1, 7, 5)
        self.assertEqual(self.block.cell(0, 6).possible_values(), set(self.block.values()) - {5})

    def test_remove_possible_removes_value_from_row_and_col_cells_given_by_parent(self):
        other_cell = self.__other_cell()
        self.parent.cells_in_row_or_col.return_value = [other_cell]
        self.block.remove_possible(1, 7, 5)
        self.parent.cells_in_row_or_col.assert_called_once_with(1, 7)
        other_cell.remove_possible.assert_called_once_with(5)

    def test_remove_possible_skips_parent_cells_that_are_in_this_block(self):
        own_cell = self.block.cell(1, 6)
        self.parent.cells_in_row_or_col.return_value = [own_cell]
        with patch.object(own_cell, "remove_possible") as remove_possible:
            self.block.remove_possible(1, 7, 5)
        remove_possible.assert_called_once_with(5)

    def test_value_is_conflicting_when_another_cell_in_block_holds_it(self):
        self.block.cell(0, 6).set(5)
        self.parent.cells_in_row_or_col.reset_mock()
        self.assertTrue(self.block.is_conflicting(2, 8, 5))
        self.parent.cells_in_row_or_col.assert_not_called()

    def test_value_in_the_same_cell_is_not_conflicting(self):
        self.block.cell(0, 6).set(5)
        self.assertFalse(self.block.is_conflicting(0, 6, 5))

    def test_value_is_conflicting_when_a_row_or_col_cell_given_by_parent_holds_it(self):
        self.parent.cells_in_row_or_col.return_value = [self.__other_cell(value=5)]
        self.assertTrue(self.block.is_conflicting(1, 7, 5))

    def test_value_is_not_conflicting_when_no_related_cell_holds_it(self):
        self.parent.cells_in_row_or_col.return_value = [self.__other_cell(value=3)]
        self.assertFalse(self.block.is_conflicting(1, 7, 5))

    def test_cells_in_row_or_col_yields_block_cells_in_that_row_or_col(self):
        cells = self.block.cells_in_row_or_col(1, 7)
        self.assertEqual({(cell.row, cell.col) for cell in cells}, {(1, 6), (1, 7), (1, 8), (0, 7), (2, 7)})

    def test_cells_in_row_or_col_handles_row_outside_block(self):
        cells = self.block.cells_in_row_or_col(5, 7)
        self.assertEqual({(cell.row, cell.col) for cell in cells}, {(0, 7), (1, 7), (2, 7)})

    def test_cells_in_row_or_col_yields_nothing_when_block_is_not_in_line(self):
        self.assertEqual(list(self.block.cells_in_row_or_col(5, 0)), [])

    def __other_cell(self, value=None):
        """A cell outside this block, in row 8 of column 7"""
        cell = MagicMock(row=8, col=7)
        cell.value.return_value = value
        return cell

if __name__ == "__main__":
    main()
