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
from unittest.mock import patch

sys.path.insert(0, ".")

from board import Board
from display_attrs import DisplayAttrs
from puzzles.board_3x3 import Board3x3


class TestBoard(TestCase):
    def setUp(self):
        self.board = Board3x3()
        return super().setUp()

    def test_board_itself_cannot_be_created(self):
        with self.assertRaises(TypeError):
            Board(9, 9)

    def test_layout_missing_a_hook_cannot_be_created(self):
        class MissingBlockAt(Board):
            def _blocks(self):
                return iter(())

        with self.assertRaises(TypeError):
            MissingBlockAt(9, 9)

    def test_board_knows_its_size(self):
        self.assertEqual((self.board.v_cells, self.board.h_cells), (9, 9))

    def test_cell_returns_the_cell_at_a_position(self):
        cell = self.board.cell(4, 7)
        self.assertEqual((cell.row, cell.col), (4, 7))

    def test_cells_where_lists_matching_cells_left_to_right_top_to_bottom(self):
        for row, col in ((8, 0), (0, 8), (4, 4)):
            self.board.cell(row, col).set(row + 1)
        cells = self.board.cells_where(lambda cell: cell.value() is not None)
        self.assertEqual([(cell.row, cell.col) for cell in cells], [(0, 8), (4, 4), (8, 0)])

    def test_first_cell_where_is_the_first_match_or_none(self):
        self.board.cell(6, 2).set(1)
        self.board.cell(3, 5).set(2)
        has_value = lambda cell: cell.value() is not None
        self.assertEqual(self.__position(self.board.first_cell_where(has_value)), (3, 5))
        self.assertIsNone(self.board.first_cell_where(lambda cell: cell.value() == 9))

    def test_cells_in_row_or_col_yields_each_cell_in_that_row_and_col_once(self):
        positions = [self.__position(cell) for cell in self.board.cells_in_row_or_col(4, 4)]
        self.assertEqual(len(positions), len(set(positions)))
        self.assertEqual(set(positions), {(4, i) for i in range(9)} | {(i, 4) for i in range(9)})

    def test_board_is_full_once_every_cell_holds_a_value(self):
        self.assertFalse(self.board.is_full())
        for row in range(9):
            for col in range(9):
                self.board.cell(row, col).set((row * 3 + row // 3 + col) % 9 + 1)
        self.assertTrue(self.board.is_full())

    def test_board_has_values_once_any_cell_holds_one(self):
        self.assertFalse(self.board.has_values())
        self.board.cell(2, 2).set(5)
        self.assertTrue(self.board.has_values())

    def test_board_has_conflicts_while_a_value_clashes(self):
        self.board.cell(4, 4).set(5)
        self.assertFalse(self.board.has_conflicts())
        self.board.cell(4, 0).set(5)
        self.assertTrue(self.board.has_conflicts())

    def test_first_dead_end_is_the_first_empty_cell_with_no_possible_values(self):
        self.assertIsNone(self.board.first_dead_end())
        for col, value in enumerate(range(1, 9)):
            self.board.cell(0, col).set(value)
        self.board.cell(5, 8).set(9)
        self.assertEqual(self.__position(self.board.first_dead_end()), (0, 8))

    def test_givens_are_the_values_entered_as_initial(self):
        self.board.cell(1, 1).set(4, (DisplayAttrs.INITIAL,))
        self.board.cell(0, 5).set(7, (DisplayAttrs.INITIAL,))
        self.board.cell(2, 2).set(3)
        self.assertEqual(self.board.givens(), [(0, 5, 7), (1, 1, 4)])

    def test_clear_empties_every_cell(self):
        self.board.cell(1, 1).set(4)
        self.board.cell(4, 0).set(5)
        with patch("cell.Display"):
            self.board.clear()
        self.assertFalse(self.board.has_values())

    def test_render_draws_every_cell(self):
        with patch("cell.Display") as display:
            self.board.render()
        self.assertEqual(display.draw_cell.call_count, 81)

    # Private functions

    def __position(self, cell):
        return (cell.row, cell.col)


if __name__ == "__main__":
    main()
