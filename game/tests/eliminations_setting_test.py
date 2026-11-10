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
from unittest.mock import patch

from game.eliminations_setting import EliminationsSetting
from game.rules.box_line_rule import BoxLineRule
from game.rules.hidden_single_rule import HiddenSingleRule
from game.rules.pointing_pair_rule import PointingPairRule
from game.rules.rule import Rule


class TestEliminationsSetting(TestCase):
    def test_nothing_is_removed_at_first(self):
        self.assertEqual(EliminationsSetting().level, EliminationsSetting.NONE)

    def test_levels_are_none_then_each_rules_level_once_in_rule_order(self):
        self.assertEqual(EliminationsSetting.levels(), ("none", "intersections", "pairs", "triples"))

    def test_a_rule_with_a_new_level_adds_that_level(self):
        with patch("game.eliminations_setting.RULES", (PointingPairRule, HiddenSingleRule, PairsRule)):
            self.assertEqual(EliminationsSetting.levels(), ("none", "intersections", "pairs"))

    def test_no_level_includes_no_rule(self):
        self.assertFalse(EliminationsSetting().includes(PointingPairRule()))

    def test_a_level_includes_its_own_rules(self):
        setting = EliminationsSetting("intersections")
        self.assertTrue(setting.includes(PointingPairRule()))
        self.assertTrue(setting.includes(BoxLineRule()))

    def test_a_level_includes_the_rules_of_the_levels_before_it_but_not_after(self):
        with patch("game.eliminations_setting.RULES", (PointingPairRule, PairsRule)):
            self.assertTrue(EliminationsSetting("pairs").includes(PointingPairRule()))
            self.assertFalse(EliminationsSetting("intersections").includes(PairsRule()))

    def test_a_rule_that_rules_nothing_out_is_never_included(self):
        self.assertFalse(EliminationsSetting("intersections").includes(HiddenSingleRule()))

    def test_the_option_offers_every_level_as_set(self):
        option, = EliminationsSetting("intersections").options()
        self.assertEqual((option.group, option.name), ("Ruled-out values", "Remove from cells"))
        self.assertEqual(option.labels(), ["none", "intersections", "pairs", "triples"])
        self.assertEqual(option.value, "intersections")

    def test_every_level_has_a_note(self):
        option, = EliminationsSetting().options()
        self.assertEqual(option.notes, (
            "Cells keep every value their row, column and box allow",
            "Cells lose values ruled out by intersections or simpler, cascading",
            "Cells lose values ruled out by pairs or simpler, cascading",
            "Cells lose values ruled out by triples or simpler, cascading",
        ))

    def test_a_setting_is_made_from_its_option_as_chosen(self):
        option, = EliminationsSetting().options()
        self.assertEqual(EliminationsSetting.from_options([option.with_choice(1)]), EliminationsSetting("intersections"))

    def test_a_level_is_saved_by_name_and_read_back(self):
        setting = EliminationsSetting("intersections")
        self.assertEqual(setting.saved(), {"level": "intersections"})
        self.assertEqual(EliminationsSetting.from_saved(setting.saved()), setting)

    def test_an_unknown_level_is_refused(self):
        with self.assertRaises(ValueError):
            EliminationsSetting("nonsense")


class PairsRule(Rule):
    """A rule at a level after the intersections, standing in for one added later"""

    LEVEL = "pairs"

    def find(self, puzzle):
        return None


if __name__ == "__main__":
    main()
