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

sys.path.insert(0, ".")

from game.puzzles.board_3x3 import Board3x3
from game.rules.pointing_pair_rule import PointingPairRule
from game.rules.rule import Outcome
from game.rules.tests.rule_test_helper import board_puzzle


class TestPointingPairRule(TestCase):
    REASON = "in one box, 4 can only go in one row"

    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        return super().setUp()

    def test_a_value_confined_to_one_line_of_a_box_is_ruled_out_of_the_rest_of_the_line(self):
        self.__leave_4_in_box_0_only_in_row_0()
        ruled_out = PointingPairRule().eliminations(self.puzzle)
        fours = {(cell.row, cell.col) for cell, value in ruled_out if value == 4}
        self.assertEqual(fours, {(0, col) for col in range(3, 9)})
        self.assertEqual(ruled_out[(self.board.cell(0, 5), 4)], self.REASON)

    def test_only_a_box_confines_a_value_to_a_line(self):
        self.__fill((0, 3, 1), (0, 4, 2), (0, 5, 3), (0, 6, 5), (0, 7, 6), (0, 8, 7))  # 4 in row 0 only in box 0
        ruled_out = PointingPairRule().eliminations(self.puzzle)
        self.assertNotIn((self.board.cell(1, 0), 4), ruled_out)

    def test_no_value_made_single_by_the_eliminations_means_no_move(self):
        self.__leave_4_in_box_0_only_in_row_0()
        self.assertIsNone(PointingPairRule().find(self.puzzle))

    def test_a_single_value_left_once_the_value_is_ruled_out_is_the_move(self):
        self.__leave_4_in_box_0_only_in_row_0()
        self.__leave_column_8_only_4_and_9_in_rows_0_and_2()
        move = PointingPairRule().find(self.puzzle)
        self.assertEqual((move.outcome, move.cell, move.value), (Outcome.MOVED, self.board.cell(0, 8), 9))
        self.assertEqual(move.hint, f"Only 9 fits here: {self.REASON}, which rules 4 out here. [pointing pair] ")

    def test_a_hidden_single_left_once_the_value_is_ruled_out_is_the_move(self):
        self.__leave_4_in_box_0_only_in_row_0()
        self.__leave_column_8_only_4_and_9_in_rows_0_and_2()
        self.puzzle.first_cell_where.side_effect = None
        self.puzzle.first_cell_where.return_value = self.board.cell(2, 8)
        move = PointingPairRule().find(self.puzzle)
        self.assertEqual((move.cell, move.value), (self.board.cell(2, 8), 4))
        self.assertEqual(move.hint, f"4 fits nowhere else in its column: {self.REASON}. [pointing pair] ")

    # Private functions

    def __fill(self, *entries):
        for row, col, value in entries:
            self.board.cell(row, col).set(value)

    def __leave_4_in_box_0_only_in_row_0(self):
        """Fill box 0 but for row 0 and (2, 2), and put 4 in column 2, so box 0's 4 can only go in (0, 0) or (0, 1)"""
        self.__fill((1, 0, 1), (1, 1, 2), (1, 2, 3), (2, 0, 5), (2, 1, 6), (5, 2, 4))

    def __leave_column_8_only_4_and_9_in_rows_0_and_2(self):
        self.__fill((1, 8, 8), (3, 8, 1), (4, 8, 2), (5, 8, 3), (6, 8, 5), (7, 8, 6), (8, 8, 7))


if __name__ == "__main__":
    main()
