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

from game.config_option import ConfigOption
from game.house import House


@dataclass(frozen=True)
class MarksSetting:
    """
    Which "must be" marks (Snyder notation) cells show: each value that has at most threshold places left in one
    of the cell's houses of the given kinds (its box, or its box, row and column), shown in every empty cell of
    the whole puzzle, or only in the cells the player tagged.

    The player configures it through its options(): the kind of house, the threshold and the whole puzzle.
    """

    NAME = "marks"  # saved under this name (see Settings)
    GROUP = "Must-be marks (Snyder notation)"  # named so that players can look up the technique
    THRESHOLDS = (2, 3, 4, 5)
    BOX_ONLY = (House.BOX,)
    EVERY_HOUSE = (House.BOX, House.ROW, House.COLUMN)

    threshold: int = 2
    kinds: tuple = BOX_ONLY
    whole_puzzle: bool = False  # True to show marks in every empty cell, False only in the tagged ones

    def __post_init__(self):
        """Refuse a setting the options don't offer, such as one from a damaged save file"""
        if self.threshold not in MarksSetting.THRESHOLDS:
            raise ValueError(f"Unknown threshold for marks: {self.threshold}")
        if self.kinds not in (MarksSetting.BOX_ONLY, MarksSetting.EVERY_HOUSE):
            raise ValueError(f"Unknown kinds of house for marks: {self.kinds}")
        if not isinstance(self.whole_puzzle, bool):
            raise ValueError(f"Unknown whole puzzle switch for marks: {self.whole_puzzle}")

    def shows_marks(self, tagged) -> bool:
        """Return True if a cell, tagged or not, shows its marks"""
        return self.whole_puzzle or tagged

    def options(self) -> list:
        """Return the options the player can configure, as set now: the kind of house, the threshold, the whole puzzle"""
        kinds = (("box", MarksSetting.BOX_ONLY), ("box, row or column", MarksSetting.EVERY_HOUSE))
        thresholds = tuple((f"{threshold} or fewer places", threshold) for threshold in self.THRESHOLDS)
        return [
            ConfigOption(self.GROUP, "Kind of house", kinds, self.kinds),
            ConfigOption(self.GROUP, "Threshold", thresholds, self.threshold),
            ConfigOption(self.GROUP, "Whole puzzle", (("off", False), ("on", True)), self.whole_puzzle),
        ]

    def from_options(options) -> "MarksSetting":
        """Return the setting the options describe, given as options() lists them"""
        kinds, threshold, whole_puzzle = (option.value for option in options)
        return MarksSetting(threshold, kinds, whole_puzzle)

    def saved(self) -> dict:
        """Return the setting as plain data for the save file"""
        return {"threshold": self.threshold, "kinds": list(self.kinds), "whole_puzzle": self.whole_puzzle}

    def from_saved(saved) -> "MarksSetting":
        return MarksSetting(saved["threshold"], tuple(saved["kinds"]), saved["whole_puzzle"])
