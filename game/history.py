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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.cell import Cell


@dataclass
class Entry:
    """Structure describing a single entry in the history and constants used in the entry"""

    @dataclass
    class ValueInfo:
        INITIAL = "initial"
        GUESS = "guess"

        value: int = 0
        prim_attr: str = None

    cell: "Cell"
    valueinfo: ValueInfo
    previous_valueinfo: ValueInfo = None


class History:
    """
    Keep and manage history of entries
    """

    def __init__(self):
        self.__entries: list[Entry] = []

    def clear(self):
        self.__entries.clear()

    def add(self, entry: Entry):
        self.__entries.append(entry)

    def undo(self) -> Entry:
        return self.__entries.pop()

    def last(self) -> Entry:
        return self.__entries[-1]

    def is_empty(self) -> bool:
        return len(self.__entries) == 0

    def entries(self) -> list[Entry]:
        """Return every entry, oldest first"""
        return list(self.__entries)
