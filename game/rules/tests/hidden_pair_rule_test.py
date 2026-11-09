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
from game.rules.hidden_pair_rule import HiddenPairRule
from game.rules.rule import Outcome
from game.rules.tests.rule_test_helper import board_puzzle


class TestHiddenPairRule(TestCase):
    REASON = "in row 1, 4 and 7 can only go in (1,2) and (1,5)"

    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        self.first, self.second = self.board.cell(0, 1), self.board.cell(0, 4)
        return super().setUp()

    # What is ruled out

    def test_every_other_value_is_ruled_out_of_the_two_cells(self):
        self.__hide_pair()
        ruled_out = HiddenPairRule().eliminations(self.puzzle)
        self.assertEqual({value for cell, value in ruled_out if cell is self.first}, {1, 2, 3, 5, 6, 8, 9})
        self.assertEqual({value for cell, value in ruled_out if cell is self.second}, {1, 2, 3, 5, 6, 8, 9})
        self.assertEqual(ruled_out[(self.first, 9)].why, self.REASON)
        self.assertEqual(ruled_out[(self.first, 9)].rule, "hidden pair")

    def test_cells_holding_only_the_pair_lose_nothing(self):
        self.__hide_pair()
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 4, 7)
        self.assertEqual(HiddenPairRule().eliminations(self.puzzle), {})

    def test_two_values_with_different_places_are_not_a_pair(self):
        self.__keep_only_in(4, 0, 1, 4)
        self.__keep_only_in(7, 0, 1, 5)
        self.assertEqual(HiddenPairRule().eliminations(self.puzzle), {})

    def test_a_value_with_one_place_is_a_hidden_single_not_part_of_a_pair(self):
        self.__keep_only_in(4, 0, 1)
        self.__keep_only_in(7, 0, 1, 4)
        self.assertEqual(HiddenPairRule().eliminations(self.puzzle), {})

    def test_a_value_already_ruled_out_is_not_ruled_out_again(self):
        self.__hide_pair()
        already = (self.first, 9)
        self.assertNotIn(already, HiddenPairRule().eliminations(self.puzzle, {already: "why"}))

    # Relying on what was ruled out first

    def test_a_value_ruled_out_of_a_cell_can_leave_a_pair(self):
        self.__hide_pair()
        third = self.board.cell(0, 8)
        third.add_possible(4)
        ruled_out = HiddenPairRule().eliminations(self.puzzle, {(third, 4): "why"})
        self.assertEqual(ruled_out[(self.first, 9)].relied_on, ((third, 4),))

    def test_a_value_ruled_out_for_two_reasons_keeps_the_one_relying_on_fewest(self):
        self.__keep_only_in(4, 0, 0, 1)
        self.__keep_only_in(7, 0, 0, 1)
        for row in (1, 2):
            self.__keep_only_in(4, row)
            self.__keep_only_in(7, row)
        relied_on = self.board.cell(1, 0)
        relied_on.add_possible(4)
        elimination = HiddenPairRule().eliminations(self.puzzle, {(relied_on, 4): "why"})[(self.board.cell(0, 0), 9)]
        self.assertEqual(elimination.why, "in row 1, 4 and 7 can only go in (1,1) and (1,2)")
        self.assertEqual(elimination.relied_on, ())

    def test_a_pair_with_nothing_ruled_out_first_relies_on_nothing(self):
        self.__hide_pair()
        self.assertEqual(HiddenPairRule().eliminations(self.puzzle)[(self.first, 9)].relied_on, ())

    # What it points at

    def test_an_elimination_points_at_the_house_and_the_two_cells_with_the_pair(self):
        self.__hide_pair()
        highlight = HiddenPairRule().eliminations(self.puzzle)[(self.first, 9)].highlight
        self.assertEqual(highlight.house.name(), "row 1")
        self.assertEqual(highlight.cells, {self.first: (4, 7), self.second: (4, 7)})

    def test_an_elimination_shows_the_pair_as_gone_from_the_other_empty_cells_of_the_house(self):
        self.__hide_pair()
        self.board.cell(0, 8).set(5)
        gone = HiddenPairRule().eliminations(self.puzzle)[(self.first, 9)].highlight.gone
        self.assertEqual(gone, {self.board.cell(0, col): (4, 7) for col in (0, 2, 3, 5, 6, 7)})

    # The move

    def test_no_value_made_single_by_the_eliminations_means_no_move(self):
        self.__hide_pair()
        self.assertIsNone(HiddenPairRule().find(self.puzzle))

    def test_a_hidden_single_left_once_the_values_are_ruled_out_is_the_move(self):
        self.__hide_pair()
        for row in range(1, 9):
            if row != 5:
                self.board.cell(row, 1).remove_possible(9)
        move = HiddenPairRule().find(self.puzzle)
        self.assertEqual((move.outcome, move.cell, move.value), (Outcome.MOVED, self.board.cell(5, 1), 9))
        self.assertEqual(move.hint, f"9 fits nowhere else in its column: {self.REASON}. [hidden pair] ")
        self.assertEqual(move.highlight.house.name(), "row 1")

    # Private functions

    def __hide_pair(self):
        self.__keep_only_in(4, 0, 1, 4)
        self.__keep_only_in(7, 0, 1, 4)

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
