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

    def test_next_goes_from_off_through_each_threshold_in_boxes_then_in_every_house_then_off(self):
        setting, seen = MarksSetting(), []
        for _ in range(9):
            setting = setting.next()
            seen.append((setting.threshold, setting.kinds))
        box, every = (House.BOX,), (House.BOX, House.ROW, House.COLUMN)
        expected = [(t, box) for t in (2, 3, 4, 5)] + [(t, every) for t in (2, 3, 4, 5)] + [(None, box)]
        self.assertEqual(seen, expected)
        self.assertFalse(setting.is_on())

    def test_an_unknown_threshold_or_kind_of_house_is_refused(self):
        for threshold, kinds in ((1, MarksSetting.BOX_ONLY), (6, MarksSetting.BOX_ONLY), (2, (House.ROW,))):
            with self.assertRaises(ValueError):
                MarksSetting(threshold, kinds)

    def test_a_setting_says_what_it_marks(self):
        box_2 = MarksSetting().next()
        every_3 = MarksSetting(3, MarksSetting.EVERY_HOUSE)
        self.assertEqual(MarksSetting().description(), "Must-be marks off. ")
        self.assertEqual(
            box_2.description(), "Must-be marks (config 1 of 8): 2 or fewer 'must be' values in their box. "
        )
        self.assertEqual(
            every_3.description(),
            "Must-be marks (config 6 of 8): 3 or fewer 'must be' values in their box, row or column. ",
        )


if __name__ == "__main__":
    main()
