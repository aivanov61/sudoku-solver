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
from game.rules.naked_triple_rule import NakedTripleRule
from game.rules.rule import Outcome
from game.rules.tests.rule_test_helper import board_puzzle


class TestNakedTripleRule(TestCase):
    REASON = "in row 1, (1,2), (1,5) and (1,8) can only hold 4, 7 and 9"

    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        self.first, self.second, self.third = self.board.cell(0, 1), self.board.cell(0, 4), self.board.cell(0, 7)
        return super().setUp()

    # What is ruled out

    def test_all_three_values_are_ruled_out_of_the_rest_of_the_house(self):
        self.__make_triple()
        ruled_out = NakedTripleRule().eliminations(self.puzzle)
        rest = {(0, col) for col in range(9) if col not in (1, 4, 7)}
        for digit in (4, 7, 9):
            self.assertEqual({(cell.row, cell.col) for cell, value in ruled_out if value == digit and cell.row == 0}, rest)
        self.assertEqual(ruled_out[(self.board.cell(0, 8), 7)].why, self.REASON)
        self.assertEqual(ruled_out[(self.board.cell(0, 8), 7)].rule, "naked triple")

    def test_the_triple_keeps_its_own_values(self):
        self.__make_triple()
        ruled_out = NakedTripleRule().eliminations(self.puzzle)
        for found in ((self.first, 4), (self.second, 7), (self.third, 9)):
            self.assertNotIn(found, ruled_out)

    def test_three_cells_can_each_hold_all_three_values(self):
        for col in (1, 4, 7):
            self.__leave(0, col, 4, 7, 9)
        self.assertIn((self.board.cell(0, 8), 4), NakedTripleRule().eliminations(self.puzzle))

    def test_three_cells_sharing_four_values_are_not_a_triple(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 7, 9)
        self.__leave(0, 7, 4, 8)
        self.assertEqual(NakedTripleRule().eliminations(self.puzzle), {})

    def test_two_cells_are_not_a_triple(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 7, 9)
        self.assertEqual(NakedTripleRule().eliminations(self.puzzle), {})

    def test_a_value_already_ruled_out_is_not_ruled_out_again(self):
        self.__make_triple()
        already = (self.board.cell(0, 8), 4)
        self.assertNotIn(already, NakedTripleRule().eliminations(self.puzzle, {already: "why"}))

    # Relying on what was ruled out first

    def test_a_value_ruled_out_of_a_cell_can_leave_a_triple(self):
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 7, 9)
        self.__leave(0, 7, 2, 4, 9)
        ruled_out = NakedTripleRule().eliminations(self.puzzle, {(self.third, 2): "why"})
        self.assertEqual(ruled_out[(self.board.cell(0, 8), 4)].relied_on, ((self.third, 2),))

    # What it points at

    def test_an_elimination_points_at_the_house_and_the_triple_with_its_values(self):
        self.__make_triple()
        highlight = NakedTripleRule().eliminations(self.puzzle)[(self.board.cell(0, 8), 4)].highlight
        self.assertEqual(highlight.house.name(), "row 1")
        self.assertEqual(highlight.cells, {self.first: (4, 7), self.second: (7, 9), self.third: (4, 9)})

    # The move

    def test_a_single_value_left_once_the_values_are_ruled_out_is_the_move(self):
        self.__make_triple()
        self.__leave(0, 8, 4, 5)
        move = NakedTripleRule().find(self.puzzle)
        self.assertEqual((move.outcome, move.cell, move.value), (Outcome.MOVED, self.board.cell(0, 8), 5))
        self.assertEqual(move.hint, f"Only 5 fits here: {self.REASON}, which rules 4 out here. [naked triple] ")

    # Its level

    def test_the_rule_is_at_the_triples_level(self):
        self.assertEqual(NakedTripleRule.LEVEL, "triples")

    # Private functions

    def __make_triple(self):
        """Leave three cells of row 0 only 4, 7 and 9 between them, none of them holding all three"""
        self.__leave(0, 1, 4, 7)
        self.__leave(0, 4, 7, 9)
        self.__leave(0, 7, 4, 9)

    def __leave(self, row, col, *values):
        """Take every other value off the cell"""
        for value in set(range(1, 10)) - set(values):
            self.board.cell(row, col).remove_possible(value)


if __name__ == "__main__":
    main()
