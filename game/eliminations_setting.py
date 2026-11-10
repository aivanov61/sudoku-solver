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

from game.config_option import ConfigOption
from game.rules.order import RULES
from game.rules.rule import Rule


@dataclass(frozen=True)
class EliminationsSetting:
    """
    How much of what the solving rules rule out is taken off the cells' possible values, as far as the player has
    chosen to see it: nothing, or everything up to a level.

    Each rule that rules values out names its LEVEL, and the levels come in the order of the rules, so a rule at a
    new level adds that level here.  A level also includes every level before it.  Levels are saved by name.
    """

    NAME = "eliminations"  # saved under this name (see Settings)
    GROUP = "Ruled-out values"
    NONE = "none"
    NONE_NOTE = "Cells keep every value their row, column and box allow"
    LEVEL_NOTE = "Cells lose values ruled out by {level} or simpler, cascading"

    level: str = NONE

    def __post_init__(self) -> None:
        """Refuse a level the options don't offer, such as one from a damaged save file"""
        if self.level not in EliminationsSetting.levels():
            raise ValueError(f"Unknown level for ruled-out values: {self.level}")

    @staticmethod
    def levels() -> tuple[str, ...]:
        """Return none, then each level the rules name, once, in the order of the rules"""
        return (EliminationsSetting.NONE, *dict.fromkeys(rule.LEVEL for rule in RULES if rule.LEVEL))

    def includes(self, rule: Rule) -> bool:
        """Return True if what the rule rules out is removed at this level: it names this level or one before it"""
        levels = EliminationsSetting.levels()
        return rule.LEVEL in levels[1 : levels.index(self.level) + 1]

    def options(self) -> list[ConfigOption]:
        """Return the option the player can configure, as set now: the level"""
        levels = EliminationsSetting.levels()
        notes = (self.NONE_NOTE, *(self.LEVEL_NOTE.format(level=level) for level in levels[1:]))
        return [ConfigOption(self.GROUP, "Remove from cells", tuple((level, level) for level in levels), self.level, notes)]

    @staticmethod
    def from_options(options: list[ConfigOption]) -> "EliminationsSetting":
        """Return the setting the options describe, given as options() lists them"""
        return EliminationsSetting(options[0].value)

    def saved(self) -> dict[str, Any]:
        """Return the setting as plain data for the save file"""
        return {"level": self.level}

    @staticmethod
    def from_saved(saved: dict[str, Any]) -> "EliminationsSetting":
        return EliminationsSetting(saved["level"])
