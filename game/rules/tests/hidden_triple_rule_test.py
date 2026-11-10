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

from unittest import main, TestCase

from game.puzzles.board_3x3 import Board3x3
from game.rules.hidden_triple_rule import HiddenTripleRule
from game.rules.rule import Outcome
from game.rules.tests.rule_test_helper import board_puzzle


class TestHiddenTripleRule(TestCase):
    REASON = "in row 1, 4, 7 and 9 can only go in (1,2), (1,5) and (1,8)"

    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        self.first, self.second, self.third = self.board.cell(0, 1), self.board.cell(0, 4), self.board.cell(0, 7)
        return super().setUp()

    # What is ruled out

    def test_every_other_value_is_ruled_out_of_the_three_cells(self):
        self.__hide_triple()
        ruled_out = HiddenTripleRule().eliminations(self.puzzle)
        for cell in (self.first, self.second, self.third):
            self.assertEqual({value for other, value in ruled_out if other is cell}, {1, 2, 3, 5, 6, 8})
        self.assertEqual(ruled_out[(self.first, 8)].why, self.REASON)
        self.assertEqual(ruled_out[(self.first, 8)].rule, "hidden triple")

    def test_each_value_can_have_just_two_of_the_three_places(self):
        self.__keep_only_in(4, 0, 1, 4)
        self.__keep_only_in(7, 0, 4, 7)
        self.__keep_only_in(9, 0, 1, 7)
        self.assertEqual(HiddenTripleRule().eliminations(self.puzzle)[(self.first, 8)].why, self.REASON)

    def test_cells_holding_only_the_triple_lose_nothing(self):
        self.__hide_triple()
        for col in (1, 4, 7):
            self.__leave(0, col, 4, 7, 9)
        self.assertEqual(HiddenTripleRule().eliminations(self.puzzle), {})

    def test_three_values_across_four_cells_are_not_a_triple(self):
        self.__keep_only_in(4, 0, 1, 4)
        self.__keep_only_in(7, 0, 4, 7)
        self.__keep_only_in(9, 0, 7, 8)
        self.assertEqual(HiddenTripleRule().eliminations(self.puzzle), {})

    def test_a_value_with_one_place_is_a_hidden_single_not_part_of_a_triple(self):
        self.__keep_only_in(4, 0, 1)
        self.__keep_only_in(7, 0, 1, 4)
        self.__keep_only_in(9, 0, 4, 7)
        self.assertEqual(HiddenTripleRule().eliminations(self.puzzle), {})

    # Relying on what was ruled out first

    def test_a_value_ruled_out_of_a_cell_can_leave_a_triple(self):
        fourth = self.board.cell(0, 8)
        self.__keep_only_in(4, 0, 1, 4, 8)
        self.__keep_only_in(7, 0, 1, 4, 7)
        self.__keep_only_in(9, 0, 1, 4, 7)
        ruled_out = HiddenTripleRule().eliminations(self.puzzle, {(fourth, 4): "why"})
        self.assertEqual(ruled_out[(self.first, 8)].relied_on, ((fourth, 4),))

    # What it points at

    def test_an_elimination_points_at_the_house_and_the_three_cells_with_the_triple(self):
        self.__hide_triple()
        highlight = HiddenTripleRule().eliminations(self.puzzle)[(self.first, 8)].highlight
        self.assertEqual(highlight.house.name(), "row 1")
        self.assertEqual(highlight.cells, {self.first: (4, 7, 9), self.second: (4, 7, 9), self.third: (4, 7, 9)})

    # The move

    def test_a_hidden_single_left_once_the_values_are_ruled_out_is_the_move(self):
        self.__hide_triple()
        for row in range(1, 9):
            if row != 5:
                self.board.cell(row, 1).remove_possible(8)
        move = HiddenTripleRule().find(self.puzzle)
        self.assertEqual((move.outcome, move.cell, move.value), (Outcome.MOVED, self.board.cell(5, 1), 8))
        self.assertEqual(move.hint, f"8 fits nowhere else in its column: {self.REASON}. [hidden triple] ")

    # Its level

    def test_the_rule_is_at_the_triples_level(self):
        self.assertEqual(HiddenTripleRule.LEVEL, "triples")

    # Private functions

    def __hide_triple(self):
        for value in (4, 7, 9):
            self.__keep_only_in(value, 0, 1, 4, 7)

    def __keep_only_in(self, value, row, *cols):
        """Take the value off every cell of the row but those in the columns"""
        for col in set(range(9)) - set(cols):
            self.board.cell(row, col).remove_possible(value)

    def __leave(self, row, col, *values):
        """Take every other value off the cell"""
        for value in set(range(1, 10)) - set(values):
            self.board.cell(row, col).remove_possible(value)


if __name__ == "__main__":
    main()
