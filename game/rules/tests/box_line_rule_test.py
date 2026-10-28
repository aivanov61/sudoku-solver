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
from game.rules.box_line_rule import BoxLineRule
from game.rules.tests.rule_test_helper import board_puzzle


class TestBoxLineRule(TestCase):
    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        return super().setUp()

    def test_a_value_confined_to_one_box_of_a_line_is_ruled_out_of_the_rest_of_the_box(self):
        self.__fill((0, 3, 1), (0, 4, 2), (0, 5, 3), (0, 6, 5), (0, 7, 6), (0, 8, 7))  # 4 in row 0 only in box 0
        ruled_out = BoxLineRule().eliminations(self.puzzle)
        fours = {(cell.row, cell.col) for cell, value in ruled_out if value == 4}
        self.assertEqual(fours, {(row, col) for row in (1, 2) for col in range(3)})
        self.assertEqual(ruled_out[(self.board.cell(2, 1), 4)], "in one row, 4 can only go in one box")

    def test_only_a_line_confines_a_value_to_a_box(self):
        self.__fill((1, 0, 1), (1, 1, 2), (1, 2, 3), (2, 0, 5), (2, 1, 6), (5, 2, 4))  # 4 in box 0 only in row 0
        ruled_out = BoxLineRule().eliminations(self.puzzle)
        self.assertNotIn((self.board.cell(0, 5), 4), ruled_out)

    # Private functions

    def __fill(self, *entries):
        for row, col, value in entries:
            self.board.cell(row, col).set(value)


if __name__ == "__main__":
    main()
