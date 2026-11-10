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

from game.actions import Action
from game.house import House
from game.marks_setting import MarksSetting


class TestMarksSetting(TestCase):
    CHOICES = (MarksSetting.OFF, MarksSetting.SNYDER, MarksSetting.MUST_BE)

    def test_marks_are_box_marks_with_2_places_at_first(self):
        self.assertEqual((MarksSetting().threshold, MarksSetting().kinds), (2, MarksSetting.BOX_ONLY))

    def test_snyder_marks_are_off_for_the_whole_puzzle_at_first(self):
        self.assertEqual(MarksSetting().whole_puzzle, MarksSetting.OFF)

    def test_options_are_the_kind_of_house_the_threshold_and_the_whole_puzzle_as_set(self):
        kind, threshold, whole = MarksSetting(3, MarksSetting.EVERY_HOUSE, MarksSetting.SNYDER).options()
        self.assertEqual({option.group for option in (kind, threshold, whole)}, {"Must-be marks (Snyder notation)"})
        self.assertEqual((kind.name, threshold.name, whole.name), ("Kind of house", "Threshold", "Whole puzzle"))
        self.assertEqual(kind.labels(), ["box", "box, row or column"])
        self.assertEqual(threshold.labels(), ["2 or fewer places", "3 or fewer places", "4 or fewer places",
                                              "5 or fewer places"])
        self.assertEqual(whole.labels(), ["off", "Snyder marks", "must be"])
        self.assertEqual((kind.value, threshold.value, whole.value), (MarksSetting.EVERY_HOUSE, 3, MarksSetting.SNYDER))

    def test_the_whole_puzzle_choices_have_notes_naming_the_tag_key(self):
        _kind, threshold, whole = MarksSetting().options()
        self.assertEqual(threshold.notes, ())
        self.assertEqual(whole.note_action, Action.TAG)
        self.assertEqual(whole.notes, (
            "Only cells you tag with {key} show marks: what each one must be",
            "All other cells show Snyder marks; {key} still shows what a cell must be",
            "Every cell shows what it must be, as if you had tagged it with {key}",
        ))

    def test_a_setting_is_made_from_its_options_as_chosen(self):
        kind, threshold, whole = MarksSetting().options()
        chosen = [kind.with_choice(1), threshold.with_choice(3), whole.with_choice(1)]
        self.assertEqual(MarksSetting.from_options(chosen), MarksSetting(5, MarksSetting.EVERY_HOUSE, MarksSetting.SNYDER))

    def test_only_snyder_marks_show_snyder_marks(self):
        shown = [MarksSetting(whole_puzzle=choice).shows_snyder_marks() for choice in self.CHOICES]
        self.assertEqual(shown, [False, True, False])

    def test_only_must_be_treats_every_cell_as_tagged(self):
        treated = [MarksSetting(whole_puzzle=choice).treats_every_cell_as_tagged() for choice in self.CHOICES]
        self.assertEqual(treated, [False, False, True])

    def test_a_setting_is_saved_as_plain_data_and_read_back(self):
        setting = MarksSetting(4, MarksSetting.EVERY_HOUSE, MarksSetting.SNYDER)
        self.assertEqual(setting.saved(), {"threshold": 4, "kinds": ["box", "row", "column"], "whole_puzzle": "snyder"})
        self.assertEqual(MarksSetting.from_saved(setting.saved()), setting)

    def test_an_unknown_threshold_kind_of_house_or_whole_puzzle_is_refused(self):
        off = MarksSetting.OFF
        refused = ((None, MarksSetting.BOX_ONLY, off), (1, MarksSetting.BOX_ONLY, off), (6, MarksSetting.BOX_ONLY, off),
                   (2, (House.ROW,), off), (2, MarksSetting.BOX_ONLY, "yes"), (2, MarksSetting.BOX_ONLY, True))
        for threshold, kinds, whole_puzzle in refused:
            with self.assertRaises(ValueError):
                MarksSetting(threshold, kinds, whole_puzzle)


if __name__ == "__main__":
    main()
