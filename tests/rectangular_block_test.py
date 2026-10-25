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
from unittest.mock import MagicMock

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
        1. remove_possible() - remove a value from the row and column
        2. is_conflicting() - whether the row or column already holds the value
        """
        self.parent = MagicMock()
        self.parent.is_conflicting.return_value = False

    BLOCK_ROWS = 3
    BLOCK_COLS = 3

    def test_block_can_render(self):
        block1 = RectangularBlock(self.parent, 0, 0, self.BLOCK_ROWS, self.BLOCK_COLS)
        block2 = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        block1.render()
        block2.render()

    def test_remove_possible_removes_value_from_every_cell_in_block(self):
        self.block.remove_possible(1, 7, 5)
        for row in range(self.BLOCK_ROWS):
            for col in range(self.BLOCK_COLS):
                self.assertNotIn(5, self.block.cell(row, col).possible_values())

    def test_remove_possible_leaves_other_values_possible(self):
        self.block.remove_possible(1, 7, 5)
        self.assertEqual(self.block.cell(0, 0).possible_values(), set(self.block.values()) - {5})

    def test_remove_possible_is_passed_to_parent(self):
        self.block.remove_possible(1, 7, 5)
        self.parent.remove_possible.assert_called_once_with(1, 7, 5)

    def test_value_is_conflicting_when_another_cell_in_block_holds_it(self):
        self.block.cell(0, 6).set(5)
        self.parent.is_conflicting.reset_mock()
        self.assertTrue(self.block.is_conflicting(2, 8, 5))
        self.parent.is_conflicting.assert_not_called()

    def test_value_in_the_same_cell_is_not_conflicting(self):
        self.block.cell(0, 6).set(5)
        self.assertFalse(self.block.is_conflicting(0, 6, 5))

    def test_conflict_check_is_passed_to_parent_when_block_has_no_conflict(self):
        self.parent.is_conflicting.return_value = True
        self.assertTrue(self.block.is_conflicting(1, 7, 5))
        self.parent.is_conflicting.assert_called_once_with(1, 7, 5)

    def test_remove_possible_in_row_and_col_removes_value_only_from_cells_in_that_row_or_col(self):
        self.block.remove_possible_in_row_and_col(1, 7, 5)
        for cell in (self.block.cell(1, 6), self.block.cell(1, 8), self.block.cell(0, 7), self.block.cell(2, 7)):
            self.assertNotIn(5, cell.possible_values())
        for cell in (self.block.cell(0, 6), self.block.cell(0, 8), self.block.cell(2, 6), self.block.cell(2, 8)):
            self.assertIn(5, cell.possible_values())

    def test_remove_possible_in_row_and_col_handles_row_outside_block(self):
        self.block.remove_possible_in_row_and_col(5, 7, 5)
        for row in range(self.BLOCK_ROWS):
            self.assertNotIn(5, self.block.cell(row, 7).possible_values())
            self.assertIn(5, self.block.cell(row, 6).possible_values())

    def test_has_value_in_row_or_col_finds_value_in_row(self):
        self.block.cell(1, 6).set(5)
        self.assertTrue(self.block.has_value_in_row_or_col(1, 0, 5))

    def test_has_value_in_row_or_col_finds_value_in_col(self):
        self.block.cell(1, 6).set(5)
        self.assertTrue(self.block.has_value_in_row_or_col(7, 6, 5))

    def test_has_value_in_row_or_col_ignores_value_outside_row_and_col(self):
        self.block.cell(1, 6).set(5)
        self.assertFalse(self.block.has_value_in_row_or_col(0, 7, 5))

    def test_has_value_in_row_or_col_ignores_the_cell_itself(self):
        self.block.cell(1, 6).set(5)
        self.assertFalse(self.block.has_value_in_row_or_col(1, 6, 5))


if __name__ == "__main__":
    main()
