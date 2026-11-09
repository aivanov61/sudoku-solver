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
from game.rules.naked_pair_rule import NakedPairRule
from game.rules.rule import Outcome
from game.rules.tests.rule_test_helper import board_puzzle


class TestNakedPairRule(TestCase):
    REASON = "in row 1, (1,2) and (1,5) can only hold 4 and 7"

    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        self.first, self.second = self.board.cell(0, 1), self.board.cell(0, 4)
        return super().setUp()

    # What is ruled out

    def test_both_values_are_ruled_out_of_the_rest_of_the_house(self):
        self.__make_pair()
        ruled_out = NakedPairRule().eliminations(self.puzzle)
        rest = {(0, col) for col in range(9) if col not in (1, 4)}
        for digit in (4, 7):
            self.assertEqual({(cell.row, cell.col) for cell, value in ruled_out if value == digit and cell.row == 0}, rest)
        self.assertEqual(ruled_out[(self.board.cell(0, 8), 7)].why, self.REASON)
        self.assertEqual(ruled_out[(self.board.cell(0, 8), 7)].rule, "naked pair")

    def test_the_pair_keeps_its_own_values(self):
        self.__make_pair()
        ruled_out = NakedPairRule().eliminations(self.puzzle)
        self.assertNotIn((self.first, 4), ruled_out)
        self.assertNotIn((self.second, 7), ruled_out)

    def test_a_pair_sharing_a_box_too_is_ruled_out_of_the_rest_of_both(self):
        self.__leave(0, 0, 4, 7)
        self.__leave(0, 1, 4, 7)
        ruled_out = NakedPairRule().eliminations(self.puzzle)
        self.assertIn((self.board.cell(0, 8), 4), ruled_out)
        self.assertIn((self.board.cell(2, 2), 4), ruled_out)

    def test_two_cells_with_different_values_are_not_a_pair(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 4, 8)
        self.assertEqual(NakedPairRule().eliminations(self.puzzle), {})

    def test_a_cell_with_a_third_value_is_not_in_a_pair(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 4, 7, 9)
        self.assertEqual(NakedPairRule().eliminations(self.puzzle), {})

    def test_a_value_already_ruled_out_is_not_ruled_out_again(self):
        self.__make_pair()
        already = (self.board.cell(0, 8), 4)
        self.assertNotIn(already, NakedPairRule().eliminations(self.puzzle, {already: "why"}))

    # Relying on what was ruled out first

    def test_a_value_ruled_out_of_a_cell_can_leave_a_pair(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 4, 7, 9)
        ruled_out = NakedPairRule().eliminations(self.puzzle, {(self.second, 9): "why"})
        self.assertEqual(ruled_out[(self.board.cell(0, 8), 4)].relied_on, ((self.second, 9),))

    def test_a_pair_with_nothing_ruled_out_first_relies_on_nothing(self):
        self.__make_pair()
        self.assertEqual(NakedPairRule().eliminations(self.puzzle)[(self.board.cell(0, 8), 4)].relied_on, ())

    # What it points at

    def test_an_elimination_points_at_the_house_and_the_pair_with_its_values(self):
        self.__make_pair()
        highlight = NakedPairRule().eliminations(self.puzzle)[(self.board.cell(0, 8), 4)].highlight
        self.assertEqual(highlight.house.name(), "row 1")
        self.assertEqual(highlight.cells, {self.first: (4, 7), self.second: (4, 7)})

    def test_an_elimination_shows_as_gone_just_the_values_each_cell_loses(self):
        self.__make_pair()
        self.__leave(0, 8, 4, 9)
        self.__leave(0, 7, 3, 8)
        gone = NakedPairRule().eliminations(self.puzzle)[(self.board.cell(0, 8), 4)].highlight.gone
        self.assertEqual(gone[self.board.cell(0, 8)], (4,))
        self.assertEqual(gone[self.board.cell(0, 0)], (4, 7))
        self.assertNotIn(self.board.cell(0, 7), gone)

    # The move

    def test_no_value_made_single_by_the_eliminations_means_no_move(self):
        self.__make_pair()
        self.assertIsNone(NakedPairRule().find(self.puzzle))

    def test_a_single_value_left_once_the_values_are_ruled_out_is_the_move(self):
        self.__make_pair()
        self.__leave(0, 8, 4, 9)
        move = NakedPairRule().find(self.puzzle)
        self.assertEqual((move.outcome, move.cell, move.value), (Outcome.MOVED, self.board.cell(0, 8), 9))
        self.assertEqual(move.hint, f"Only 9 fits here: {self.REASON}, which rules 4 out here. [naked pair] ")
        self.assertEqual(move.highlight.house.name(), "row 1")

    # Private functions

    def __make_pair(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 4, 7)

    def __leave(self, row, col, *values):
        """Take every other value off the cell"""
        for value in set(range(1, 10)) - set(values):
            self.board.cell(row, col).remove_possible(value)


if __name__ == "__main__":
    main()
