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

import importlib
import inspect
import pkgutil
import sys
from unittest import main, TestCase

sys.path.insert(0, ".")

from game import rules
from game.rules.conflicts_rule import ConflictsRule
from game.rules.dead_end_rule import DeadEndRule
from game.rules.order import RULES
from game.rules.rule import Rule
from game.rules.single_value_rule import SingleValueRule


class TestRuleOrder(TestCase):
    def test_rules_are_applied_conflicts_first_then_dead_ends_then_moves(self):
        self.assertEqual(RULES, (ConflictsRule, DeadEndRule, SingleValueRule))

    def test_every_rule_in_the_rules_folder_is_in_the_order(self):
        defined = set()
        for info in pkgutil.iter_modules(rules.__path__):
            module = importlib.import_module(f"{rules.__name__}.{info.name}")
            defined |= {
                obj
                for obj in vars(module).values()
                if inspect.isclass(obj) and issubclass(obj, Rule) and obj is not Rule
            }
        self.assertEqual(defined, set(RULES))


if __name__ == "__main__":
    main()
