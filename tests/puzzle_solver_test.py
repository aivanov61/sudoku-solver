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
from rules.rule import Outcome, Rule


class TestPuzzleSolver(TestCase):
    def setUp(self):
        self.applied = []
        return super().setUp()

    def test_outcome_of_the_first_rule_that_acts_is_returned(self):
        solver = PuzzleSolver(MagicMock(), [self.__rule("a", Outcome.NONE), self.__rule("b", Outcome.MOVED)])
        self.assertIs(solver.next_move(), Outcome.MOVED)

    def test_rules_after_the_first_that_acts_are_not_applied(self):
        rules = [self.__rule("a", Outcome.STOPPED), self.__rule("b", Outcome.MOVED)]
        PuzzleSolver(MagicMock(), rules).next_move()
        self.assertEqual(self.applied, ["a"])

    def test_nothing_to_do_when_no_rule_acts(self):
        solver = PuzzleSolver(MagicMock(), [self.__rule("a", Outcome.NONE), self.__rule("b", Outcome.NONE)])
        self.assertIs(solver.next_move(), Outcome.NONE)
        self.assertEqual(self.applied, ["a", "b"])

    # Private functions

    def __rule(self, name, outcome):
        """A rule class that records being applied and returns the outcome"""
        applied = self.applied

        class FakeRule(Rule):
            def apply(self, puzzle):
                applied.append(name)
                return outcome

        return FakeRule


if __name__ == "__main__":
    main()
