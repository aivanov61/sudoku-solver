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

from abc import ABC, abstractmethod


class MenuItem(ABC):
    """
    A line of a menu: the text it shows, whether it can be selected or picked, and what it does with the keys
    the menu leaves to the selected line.  Each kind of line is a subclass.
    """

    INDENT = "  "
    value = None  # what the menu returns when ENTER picks the item

    @abstractmethod
    def text(self) -> str:
        """Return the text shown on the item's line, after its INDENT"""

    def is_selectable(self) -> bool:
        return True

    def is_grayed_out(self) -> bool:
        return False

    def is_picked_by_enter(self) -> bool:
        return False

    def handle(self, key) -> None:
        """Act on a key the menu leaves to the selected item; most items ignore them"""
