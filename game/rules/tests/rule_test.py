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

from game.rules.order import RULES
from game.rules.rule import Move, Outcome, Rule


class TestRule(TestCase):
    def test_a_rules_move_ends_its_hint_with_the_rules_name_in_brackets(self):
        cell = MagicMock()

        class ExampleRule(Rule):
            NAME = "example"

            def find(self, puzzle):
                return self._move(Outcome.MOVED, "Because.", cell, 3)

        move = ExampleRule().find(MagicMock())
        self.assertEqual((move.outcome, move.hint, move.cell, move.value), (Outcome.MOVED, "Because. [example] ", cell, 3))

    def test_a_rule_rules_nothing_out_unless_it_says_so(self):
        class ExampleRule(Rule):
            def find(self, puzzle):
                return None

        self.assertEqual(ExampleRule().eliminations(MagicMock()), {})

    def test_every_rule_has_a_name(self):
        for rule in RULES:
            self.assertTrue(rule.NAME, rule)

    def test_a_warning_with_a_value_points_it_out_as_missing_in_its_cell(self):
        cell = MagicMock()
        self.assertEqual(Move(Outcome.STOPPED, "stuck", cell, 4).missing(), (cell, 4))

    def test_a_warning_without_a_value_points_nothing_out(self):
        self.assertIsNone(Move(Outcome.STOPPED, "stuck", MagicMock()).missing())

    def test_a_move_that_fills_a_cell_points_nothing_out(self):
        self.assertIsNone(Move(Outcome.MOVED, "why", MagicMock(), 4).missing())


if __name__ == "__main__":
    main()
