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

from puzzle_solver import PuzzleSolver
from rules.rule import Move, Outcome, Rule


class TestPuzzleSolver(TestCase):
    def setUp(self):
        self.consulted = []
        self.puzzle = MagicMock()
        return super().setUp()

    def test_move_of_the_first_rule_that_has_one_is_found(self):
        move = Move(Outcome.MOVED, "hint", MagicMock(), 3)
        solver = PuzzleSolver(self.puzzle, [self.__rule("a", None), self.__rule("b", move)])
        self.assertIs(solver.find_move(), move)

    def test_rules_after_the_first_with_a_move_are_not_consulted(self):
        stop = Move(Outcome.STOPPED, "warning")
        PuzzleSolver(self.puzzle, [self.__rule("a", stop), self.__rule("b", stop)]).find_move()
        self.assertEqual(self.consulted, ["a"])

    def test_no_move_when_no_rule_has_one(self):
        solver = PuzzleSolver(self.puzzle, [self.__rule("a", None), self.__rule("b", None)])
        self.assertIsNone(solver.find_move())
        self.assertEqual(self.consulted, ["a", "b"])

    def test_making_a_move_enters_its_value(self):
        cell = MagicMock()
        PuzzleSolver(self.puzzle, []).make_move(Move(Outcome.MOVED, "hint", cell, 3))
        self.puzzle.enter_solved_value.assert_called_once_with(cell, 3)

    # Private functions

    def __rule(self, name, move):
        """A rule class that records being consulted and returns the move"""
        consulted = self.consulted

        class FakeRule(Rule):
            def find(self, puzzle):
                consulted.append(name)
                return move

        return FakeRule


if __name__ == "__main__":
    main()
