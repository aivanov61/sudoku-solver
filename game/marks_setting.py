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

from dataclasses import dataclass

sys.path.insert(0, ".")

from game.house import House


@dataclass(frozen=True)
class MarksSetting:
    """
    Which "must be" marks (Snyder notation) cells show: none, or each value that has at most threshold places
    left in one of the cell's houses of the given kinds (its box, or its box, row and column).

    next() steps through every setting in turn: off, each threshold for boxes, each for every house, then off.
    """

    THRESHOLDS = (2, 3, 4, 5)
    BOX_ONLY = (House.BOX,)
    EVERY_HOUSE = (House.BOX, House.ROW, House.COLUMN)

    threshold: int = None  # None while marks are off
    kinds: tuple = BOX_ONLY

    def __post_init__(self):
        """Refuse a setting next() would never reach, such as one from a damaged save file"""
        if self.threshold not in (None, *MarksSetting.THRESHOLDS):
            raise ValueError(f"Unknown threshold for marks: {self.threshold}")
        if self.kinds not in (MarksSetting.BOX_ONLY, MarksSetting.EVERY_HOUSE):
            raise ValueError(f"Unknown kinds of house for marks: {self.kinds}")

    def is_on(self) -> bool:
        return self.threshold is not None

    def next(self) -> "MarksSetting":
        settings = MarksSetting.__in_turn()
        return settings[(settings.index(self) + 1) % len(settings)]

    def description(self) -> str:
        """Say which of the settings that show marks this is, and what it marks, for the status line"""
        if not self.is_on():
            return "Must-be marks off. "
        settings = MarksSetting.__in_turn()
        config = f"config {settings.index(self)} of {len(settings) - 1}"
        houses = "box" if self.kinds == MarksSetting.BOX_ONLY else "box, row or column"
        return f"Must-be marks ({config}): {self.threshold} or fewer 'must be' values in their {houses}. "

    # Private functions

    def __in_turn() -> list:
        """Return every setting, in the order next() steps through them"""
        kinds_in_turn = (MarksSetting.BOX_ONLY, MarksSetting.EVERY_HOUSE)
        return [MarksSetting()] + [
            MarksSetting(threshold, kinds) for kinds in kinds_in_turn for threshold in MarksSetting.THRESHOLDS
        ]
