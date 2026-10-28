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

sys.path.insert(0, ".")

from game.house import House
from game.marks_setting import MarksSetting


class TestMarksSetting(TestCase):
    def test_marks_are_off_at_first(self):
        self.assertFalse(MarksSetting().is_on())

    def test_options_are_the_kind_of_house_then_the_threshold_as_set(self):
        kind, threshold = MarksSetting(3, MarksSetting.EVERY_HOUSE).options()
        self.assertEqual((kind.group, kind.name, threshold.group, threshold.name), (
            "Must-be marks (Snyder notation)", "Kind of house", "Must-be marks (Snyder notation)", "Threshold"
        ))
        self.assertEqual(kind.labels(), ["box", "box, row or column"])
        self.assertEqual(threshold.labels(), ["off", "2 or fewer places", "3 or fewer places", "4 or fewer places",
                                              "5 or fewer places"])
        self.assertEqual((kind.value, threshold.value), (MarksSetting.EVERY_HOUSE, 3))

    def test_a_setting_is_made_from_its_options_as_chosen(self):
        kind, threshold = MarksSetting().options()
        chosen = [kind.with_choice(1), threshold.with_choice(4)]
        self.assertEqual(MarksSetting.from_options(chosen), MarksSetting(5, MarksSetting.EVERY_HOUSE))

    def test_a_setting_is_saved_as_plain_data_and_read_back(self):
        setting = MarksSetting(4, MarksSetting.EVERY_HOUSE)
        self.assertEqual(setting.saved(), {"threshold": 4, "kinds": ["box", "row", "column"]})
        self.assertEqual(MarksSetting.from_saved(setting.saved()), setting)

    def test_marks_turned_off_keep_their_kind_of_house(self):
        kind, threshold = MarksSetting(2, MarksSetting.EVERY_HOUSE).options()
        setting = MarksSetting.from_options([kind, threshold.with_choice(0)])
        self.assertEqual((setting.is_on(), setting.kinds), (False, MarksSetting.EVERY_HOUSE))

    def test_an_unknown_threshold_or_kind_of_house_is_refused(self):
        for threshold, kinds in ((1, MarksSetting.BOX_ONLY), (6, MarksSetting.BOX_ONLY), (2, (House.ROW,))):
            with self.assertRaises(ValueError):
                MarksSetting(threshold, kinds)


if __name__ == "__main__":
    main()
