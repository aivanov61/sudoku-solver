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
from game.rules.combined_rule import CombinedRule
from game.rules.rule import Elimination, Outcome
from game.rules.tests.rule_test_helper import board_puzzle


class TestCombinedRule(TestCase):
    def setUp(self):
        self.board = Board3x3()
        self.puzzle = board_puzzle(self.board)
        self.ruled_out = {}
        self.puzzle.everything_ruled_out.return_value = self.ruled_out
        return super().setUp()

    # Finding the move

    def test_no_move_when_nothing_is_ruled_out(self):
        self.assertIsNone(CombinedRule().find(self.puzzle))

    def test_no_move_when_what_is_ruled_out_forces_nothing(self):
        self.__rule_out(self.board.cell(0, 0), 3)
        self.assertIsNone(CombinedRule().find(self.puzzle))

    def test_only_value_left_once_others_are_ruled_out_is_the_move(self):
        cell = self.__left_with(0, 0, 3, 5, 7)
        self.__rule_out(cell, 3)
        self.__rule_out(cell, 5)
        move = CombinedRule().find(self.puzzle)
        self.assertIs(move.outcome, Outcome.MOVED)
        self.assertIs(move.cell, cell)
        self.assertEqual(move.value, 7)
        self.assertEqual(move.hint, "Only 7 fits here once 3 and 5 are ruled out (press w for why). [combined rules] ")

    def test_the_hint_reads_right_for_one_value_ruled_out(self):
        cell = self.__left_with(0, 0, 5, 7)
        self.__rule_out(cell, 5)
        self.assertEqual(CombinedRule().find(self.puzzle).hint, "Only 7 fits here once 5 is ruled out (press w for why). [combined rules] ")

    def test_a_value_ruled_out_of_every_other_place_in_a_house_is_the_move(self):
        first, second = self.__leave_4_two_places_in_row_0()
        self.__rule_out(second, 4)
        move = CombinedRule().find(self.puzzle)
        self.assertIs(move.cell, first)
        self.assertEqual(move.value, 4)
        self.assertEqual(move.hint, "4 fits nowhere else in its row once it is ruled out of (1,5) (press w for why). [combined rules] ")

    def test_a_cell_already_forced_without_the_removals_is_left_to_the_simpler_rules(self):
        self.__left_with(0, 0, 7)
        self.__rule_out(self.board.cell(4, 4), 2)
        self.assertIsNone(CombinedRule().find(self.puzzle))

    def test_a_cell_left_with_no_values_is_not_a_move(self):
        cell = self.__left_with(0, 0, 3, 5)
        self.__rule_out(cell, 3)
        self.__rule_out(cell, 5)
        self.assertIsNone(CombinedRule().find(self.puzzle))

    # Which move

    def test_the_move_needing_the_fewest_removals_comes_first(self):
        long_chain, short_chain = self.__left_with(0, 0, 3, 7), self.__left_with(4, 4, 2, 6)
        earlier = self.__rule_out(self.board.cell(8, 8), 1)
        self.__rule_out(long_chain, 3, (earlier,))
        self.__rule_out(short_chain, 2)
        self.assertIs(CombinedRule().find(self.puzzle).cell, short_chain)

    def test_moves_needing_as_many_removals_go_left_to_right_and_top_to_bottom(self):
        lower, upper = self.__left_with(1, 0, 3, 7), self.__left_with(0, 8, 2, 6)
        self.__rule_out(lower, 3)
        self.__rule_out(upper, 2)
        self.assertIs(CombinedRule().find(self.puzzle).cell, upper)

    # The removals a move needs

    def test_the_move_carries_the_removals_it_needs_and_what_they_rely_on_oldest_first(self):
        cell, far = self.__left_with(0, 0, 3, 7), self.board.cell(8, 8)
        earlier = self.__rule_out(self.board.cell(4, 4), 1)
        self.__rule_out(far, 2)
        needed = self.__rule_out(cell, 3, (earlier,))
        self.assertEqual(list(CombinedRule().find(self.puzzle).reasons), [earlier, needed])

    def test_a_value_with_one_place_needs_its_removals_from_the_other_places(self):
        _first, second = self.__leave_4_two_places_in_row_0()
        needed = self.__rule_out(second, 4)
        self.assertEqual(list(CombinedRule().find(self.puzzle).reasons), [needed])

    def test_it_rules_nothing_out_itself(self):
        self.assertEqual(CombinedRule().eliminations(self.puzzle), {})
        self.puzzle.everything_ruled_out.assert_not_called()

    # Private functions

    def __left_with(self, row, col, *values):
        """Return the cell, with only the values still possible"""
        cell = self.board.cell(row, col)
        for value in set(range(1, 10)) - set(values):
            cell.remove_possible(value)
        return cell

    def __leave_4_two_places_in_row_0(self) -> tuple:
        """Return the only two cells of row 0 where 4 is still possible"""
        for col in set(range(9)) - {1, 4}:
            self.board.cell(0, col).remove_possible(4)
        return self.board.cell(0, 1), self.board.cell(0, 4)

    def __rule_out(self, cell, value, relied_on=()) -> tuple:
        """Note the value as ruled out of the cell, returning the (cell, value)"""
        self.ruled_out[(cell, value)] = Elimination("why", "rule", relied_on)
        return (cell, value)


if __name__ == "__main__":
    main()
