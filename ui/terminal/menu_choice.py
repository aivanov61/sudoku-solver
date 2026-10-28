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

sys.path.insert(0, ".")

from ui.terminal.menu_item import MenuItem


class MenuChoice(MenuItem):
    """
    A menu line offering choices, showing the one chosen and where it is among them, e.g. "Size ... large (3 of 3)".
    TAB or right moves to the next choice and Shift-TAB or left to the previous one, going round at either end.
    ENTER picks it, giving the index chosen as its value.
    """

    INDENT = "    "  # under its heading
    NAME_WIDTH = 20  # the name and its dots
    NEXT_KEYS = ("KEY_TAB", "KEY_RIGHT")
    PREVIOUS_KEYS = ("KEY_BTAB", "KEY_LEFT")

    def __init__(self, name, labels: list, chosen=0):
        self.chosen = chosen  # the index of the label chosen
        self.__name = name
        self.__labels = labels

    def text(self) -> str:
        position = f"({self.chosen + 1} of {len(self.__labels)})"
        return f"{self.__name + ' ':.<{self.NAME_WIDTH}} {self.__labels[self.chosen]} {position}"

    @property
    def value(self) -> int:
        return self.chosen

    def is_picked_by_enter(self) -> bool:
        return True

    def handle(self, key) -> None:
        if key in self.NEXT_KEYS + self.PREVIOUS_KEYS:
            step = 1 if key in self.NEXT_KEYS else -1
            self.chosen = (self.chosen + step) % len(self.__labels)
