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

from dataclasses import dataclass, field

sys.path.insert(0, ".")

from game.marks_setting import MarksSetting


@dataclass(frozen=True)
class Settings:
    """
    Every setting the player can configure, each kept and saved under its kind's NAME.

    A new setting is a class listed in KINDS, with a NAME, a default made by calling the class, options() giving
    its ConfigOptions, from_options() making it back from them, and saved() and from_saved() giving it as plain
    data for the save file and back.  A setting missing from a save file is read as its default, so adding one
    needs no new save file version.
    """

    KINDS = (MarksSetting,)  # every kind of setting, in the order the player is offered them

    by_name: dict = field(default_factory=lambda: {kind.NAME: kind() for kind in Settings.KINDS})

    def of(self, kind):
        """Return the setting of that kind"""
        return self.by_name[kind.NAME]

    def options(self) -> list:
        """Return every setting's options, one setting after another"""
        return [option for kind in Settings.KINDS for option in self.of(kind).options()]

    def from_options(self, options) -> "Settings":
        """Return the settings the options describe, given as options() lists them"""
        by_name, start = {}, 0
        for kind in Settings.KINDS:
            count = len(self.of(kind).options())
            by_name[kind.NAME] = kind.from_options(options[start : start + count])
            start += count
        return Settings(by_name)

    def saved(self) -> dict:
        """Return every setting as plain data, by name, for the save file"""
        return {name: setting.saved() for name, setting in self.by_name.items()}

    def from_saved(saved) -> "Settings":
        """Return the settings saved by saved(); a setting that wasn't saved is its default"""
        return Settings({
            kind.NAME: kind.from_saved(saved[kind.NAME]) if kind.NAME in saved else kind() for kind in Settings.KINDS
        })
