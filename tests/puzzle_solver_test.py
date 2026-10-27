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
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from puzzle_solver import PuzzleSolver
from rules.rule import Move, Outcome, Rule


class TestPuzzleSolver(TestCase):
    def setUp(self):
        self.consulted = []
        self.puzzle = MagicMock()
        self.puzzle.is_complete.return_value = False
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

    def test_first_next_points_out_the_move_without_making_it(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.MOVED, "why", cell, 3)])
        solver.next()
        self.puzzle.select.assert_called_once_with(cell)
        self.puzzle.enter_solved_value.assert_not_called()
        self.assertEqual(solver.pending_hint(), "why")

    def test_second_next_makes_the_move_pointed_out(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.MOVED, "why", cell, 3)])
        solver.next()
        solver.next()
        self.puzzle.enter_solved_value.assert_called_once_with(cell, 3)
        self.assertIsNone(solver.pending_hint())

    def test_cancelled_move_is_pointed_out_again_by_the_next_next(self):
        move = Move(Outcome.MOVED, "why", MagicMock(), 3)
        solver = self.__solver_with([move, move])
        solver.next()
        solver.cancel_pending_move()
        self.assertIsNone(solver.pending_hint())
        solver.next()
        self.puzzle.enter_solved_value.assert_not_called()
        self.assertEqual(solver.pending_hint(), "why")

    def test_next_warns_about_a_move_that_stops_solving_and_selects_its_cell(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.STOPPED, "dead end", cell)])
        with patch("display.Display.warn") as warn:
            solver.next()
        self.assertEqual(warn.call_args.args[0], "dead end")
        self.puzzle.select.assert_called_once_with(cell)
        self.assertIsNone(solver.pending_hint())

    def test_next_with_no_move_says_to_guess(self):
        with patch("display.Display.warn") as warn:
            self.__solver_with([]).next()
        self.assertIn("make a guess", warn.call_args.args[0])

    def test_auto_makes_every_move_then_warns_why_it_stopped(self):
        first, second = MagicMock(), MagicMock()
        moves = [Move(Outcome.MOVED, "why", first, 1), Move(Outcome.MOVED, "why", second, 2)]
        with patch("display.Display.warn") as warn:
            self.__solver_with(moves).auto()
        self.assertEqual(self.puzzle.enter_solved_value.call_count, 2)
        self.puzzle.select.assert_called_with(second)
        self.assertIn("make a guess", warn.call_args.args[0])

    def test_auto_that_completes_the_puzzle_ends_without_a_warning(self):
        def complete(cell, value):
            self.puzzle.is_complete.return_value = True

        self.puzzle.enter_solved_value.side_effect = complete
        with patch("display.Display.warn") as warn:
            self.__solver_with([Move(Outcome.MOVED, "why", MagicMock(), 1)]).auto()
        warn.assert_not_called()

    # Private functions

    def __rule(self, name, move):
        """A rule class that records being consulted and returns the move"""
        consulted = self.consulted

        class FakeRule(Rule):
            def find(self, puzzle):
                consulted.append(name)
                return move

        return FakeRule

    def __solver_with(self, moves):
        """A solver whose only rule returns the given moves one at a time, then None"""
        moves = list(moves)

        class ScriptedRule(Rule):
            def find(self, puzzle):
                return moves.pop(0) if moves else None

        return PuzzleSolver(self.puzzle, [ScriptedRule])


if __name__ == "__main__":
    main()
