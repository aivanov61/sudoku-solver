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

from dataclasses import dataclass
from typing import Any

from game.actions import Action
from game.config_option import ConfigOption
from game.house import House


@dataclass(frozen=True)
class MarksSetting:
    """
    Which "must be" marks (Snyder notation) cells show: each value that has at most threshold places left in one
    of the cell's houses of the given kinds (its box, or its box, row and column), shown in every empty cell of
    the whole puzzle, or in none.  Tagged cells show what they must be instead, whatever the setting (see Cell), and
    the whole puzzle can treat every cell as tagged.

    The player configures it through its options(): the kind of house, the threshold and the whole puzzle.
    """

    NAME = "marks"  # saved under this name (see Settings)
    GROUP = "Must-be marks (Snyder notation)"  # named so that players can look up the technique
    THRESHOLDS = (2, 3, 4, 5)
    BOX_ONLY = (House.BOX,)
    EVERY_HOUSE = (House.BOX, House.ROW, House.COLUMN)
    OFF = "off"  # the whole puzzle: only tagged cells show marks
    SNYDER = "snyder"  # the whole puzzle: Snyder marks in every empty cell that isn't tagged
    MUST_BE = "must be"  # the whole puzzle: every cell is treated as tagged
    WHOLE_PUZZLE_CHOICES = (("off", OFF), ("Snyder marks", SNYDER), ("must be", MUST_BE))
    WHOLE_PUZZLE_NOTES = (  # for each of the choices; {key} is the key that tags a cell
        "Only cells you tag with {key} show marks: what each one must be",
        "All other cells show Snyder marks; {key} still shows what a cell must be",
        "Every cell shows what it must be, as if you had tagged it with {key}",
    )

    threshold: int = 2
    kinds: tuple[str, ...] = BOX_ONLY
    whole_puzzle: str = OFF  # what the cells of the whole puzzle show, beyond those tagged

    def __post_init__(self) -> None:
        """Refuse a setting the options don't offer, such as one from a damaged save file"""
        if self.threshold not in MarksSetting.THRESHOLDS:
            raise ValueError(f"Unknown threshold for marks: {self.threshold}")
        if self.kinds not in (MarksSetting.BOX_ONLY, MarksSetting.EVERY_HOUSE):
            raise ValueError(f"Unknown kinds of house for marks: {self.kinds}")
        if self.whole_puzzle not in (MarksSetting.OFF, MarksSetting.SNYDER, MarksSetting.MUST_BE):
            raise ValueError(f"Unknown whole puzzle switch for marks: {self.whole_puzzle}")

    def shows_snyder_marks(self) -> bool:
        return self.whole_puzzle == MarksSetting.SNYDER

    def treats_every_cell_as_tagged(self) -> bool:
        return self.whole_puzzle == MarksSetting.MUST_BE

    def options(self) -> list[ConfigOption]:
        """Return the options the player can configure, as set now: the kind of house, the threshold, the whole puzzle"""
        kinds = (("box", MarksSetting.BOX_ONLY), ("box, row or column", MarksSetting.EVERY_HOUSE))
        thresholds = tuple((f"{threshold} or fewer places", threshold) for threshold in self.THRESHOLDS)
        return [
            ConfigOption(self.GROUP, "Kind of house", kinds, self.kinds),
            ConfigOption(self.GROUP, "Threshold", thresholds, self.threshold),
            ConfigOption(
                self.GROUP, "Whole puzzle", self.WHOLE_PUZZLE_CHOICES, self.whole_puzzle, self.WHOLE_PUZZLE_NOTES,
                Action.TAG,
            ),
        ]

    @staticmethod
    def from_options(options: list[ConfigOption]) -> "MarksSetting":
        """Return the setting the options describe, given as options() lists them"""
        kinds, threshold, whole_puzzle = (option.value for option in options)
        return MarksSetting(threshold, kinds, whole_puzzle)

    def saved(self) -> dict[str, Any]:
        """Return the setting as plain data for the save file"""
        return {"threshold": self.threshold, "kinds": list(self.kinds), "whole_puzzle": self.whole_puzzle}

    @staticmethod
    def from_saved(saved: dict[str, Any]) -> "MarksSetting":
        return MarksSetting(saved["threshold"], tuple(saved["kinds"]), saved["whole_puzzle"])
