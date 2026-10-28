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
    Which "must be" marks (Snyder notation) cells show: none, or each value that has at most threshold places
    left in one of the cell's houses of the given kinds (its box, or its box, row and column).

    The player configures it through its options(): the kind of house and the threshold, which can be off.
    """

    NAME = "marks"  # saved under this name (see Settings)
    GROUP = "Must-be marks (Snyder notation)"  # named so that players can look up the technique
    THRESHOLDS = (2, 3, 4, 5)
    BOX_ONLY = (House.BOX,)
    EVERY_HOUSE = (House.BOX, House.ROW, House.COLUMN)

    threshold: int = None  # None while marks are off
    kinds: tuple = BOX_ONLY

    def __post_init__(self):
        """Refuse a setting the options don't offer, such as one from a damaged save file"""
        if self.threshold not in (None, *MarksSetting.THRESHOLDS):
            raise ValueError(f"Unknown threshold for marks: {self.threshold}")
        if self.kinds not in (MarksSetting.BOX_ONLY, MarksSetting.EVERY_HOUSE):
            raise ValueError(f"Unknown kinds of house for marks: {self.kinds}")

    def is_on(self) -> bool:
        return self.threshold is not None

    def options(self) -> list:
        """Return the options the player can configure, as set now: the kind of house, then the threshold"""
        kinds = (("box", MarksSetting.BOX_ONLY), ("box, row or column", MarksSetting.EVERY_HOUSE))
        thresholds = (("off", None), *((f"{threshold} or fewer places", threshold) for threshold in self.THRESHOLDS))
        return [
            ConfigOption(self.GROUP, "Kind of house", kinds, self.kinds),
            ConfigOption(self.GROUP, "Threshold", thresholds, self.threshold),
        ]

    def from_options(options) -> "MarksSetting":
        """Return the setting the options describe, given as options() lists them"""
        kinds, threshold = (option.value for option in options)
        return MarksSetting(threshold, kinds)

    def saved(self) -> dict:
        """Return the setting as plain data for the save file"""
        return {"threshold": self.threshold, "kinds": list(self.kinds)}

    def from_saved(saved) -> "MarksSetting":
        return MarksSetting(saved["threshold"], tuple(saved["kinds"]))
