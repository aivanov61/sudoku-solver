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
from unittest.mock import patch

sys.path.insert(0, ".")

from game.marks_setting import MarksSetting
from game.settings import Settings


class TestSettings(TestCase):
    MARKS = MarksSetting(3, MarksSetting.EVERY_HOUSE)

    def test_every_setting_starts_as_its_default(self):
        self.assertEqual(Settings().of(MarksSetting), MarksSetting())

    def test_options_are_every_settings_options_in_turn(self):
        with patch.object(Settings, "KINDS", (MarksSetting, OtherSetting)):
            settings = Settings({MarksSetting.NAME: self.MARKS, OtherSetting.NAME: OtherSetting()})
            self.assertEqual(settings.options(), self.MARKS.options() + OtherSetting().options())

    def test_options_as_chosen_go_back_to_their_own_settings(self):
        with patch.object(Settings, "KINDS", (MarksSetting, OtherSetting)):
            options = Settings().options()
            chosen = Settings().from_options([options[0].with_choice(1), options[1].with_choice(1), *options[2:]])
            self.assertEqual(chosen.of(MarksSetting), MarksSetting(3, MarksSetting.EVERY_HOUSE))
            self.assertEqual(chosen.of(OtherSetting), OtherSetting())

    def test_settings_are_saved_by_name_and_read_back(self):
        settings = Settings({MarksSetting.NAME: self.MARKS})
        saved = settings.saved()
        self.assertEqual(saved, {"marks": {"threshold": 3, "kinds": ["box", "row", "column"], "whole_puzzle": False}})
        self.assertEqual(Settings.from_saved(saved), settings)

    def test_a_setting_missing_from_what_was_saved_is_its_default(self):
        self.assertEqual(Settings.from_saved({}), Settings())


class OtherSetting:
    """A second kind of setting, standing in for one added later"""

    NAME = "other"

    def options(self) -> list:
        return [MarksSetting().options()[0]]

    def from_options(options) -> "OtherSetting":
        return OtherSetting()

    def __eq__(self, other) -> bool:
        return isinstance(other, OtherSetting)


if __name__ == "__main__":
    main()
