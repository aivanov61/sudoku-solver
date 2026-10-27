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

from cell import Cell
from display import Display
from display_attrs import DisplayAttrs
from history import History, Entry


class Moves:
    """
    Enter values into cells and record them in the History, so they can be undone.

    Values entered while the puzzle is set up are givens, which are not recorded.  While playing,
    each guess gives itself and every value entered after it a lighter shade of gray.

    The puzzle provides is_initializing().
    """

    SHADE_STEP = 10

    def __init__(self, puzzle):
        self.__puzzle = puzzle
        self.__shade = 0
        History.clear()

    # Interface required for the puzzle

    def enter(self, cell, value, prim_attr=None) -> None:
        """Enter a value with its primary attribute (None for a typed value) and record it while playing"""
        is_playing = not self.__puzzle.is_initializing()
        prim_attr == DisplayAttrs.GUESS and is_playing and self.__deepen_shade()
        attr = self.__attributes(prim_attr)
        is_playing and self.__record(cell, value, attr)
        cell.update(value, attr)

    def is_empty(self) -> bool:
        return History.is_empty()

    def undo(self) -> Cell:
        """Undo the most recent move, putting back the cell's previous value, and return the cell"""
        entry = History.undo()
        self.__is_guess(entry) and self.__lighten_shade()
        previous = entry.previous_valueinfo
        value, attr = (previous.value, self.__attributes(previous.prim_attr)) if previous else (None, ())
        entry.cell.update(value, attr)
        return entry.cell

    def rewind(self) -> Cell:
        """Undo moves until the most recent one is a guess (at least one) and return its cell, or the last cell undone"""
        cell = self.undo()
        while not History.is_empty() and not self.__is_guess(History.last()):
            cell = self.undo()
        return cell if History.is_empty() else History.last().cell

    def recorded(self) -> list:
        """Return every recorded move as (row, col, value, prim_attr), oldest first"""
        return [
            (entry.cell.row, entry.cell.col, entry.valueinfo.value, entry.valueinfo.prim_attr)
            for entry in History.entries()
        ]

    def clear(self) -> None:
        History.clear()
        self.__shade = 0

    # Private functions

    def __deepen_shade(self) -> None:
        self.__shade += self.SHADE_STEP
        self.__shade > DisplayAttrs.MAX_GRAY_LEVEL and Display.warn(
            "No more shades of gray left - repeating last shade. ", wait=True
        )

    def __attributes(self, prim_attr) -> tuple:
        """Primary attribute: INITIAL while initializing, else prim_attr (if any); plus the shading"""
        attr = [DisplayAttrs.INITIAL] if self.__puzzle.is_initializing() else [prim_attr] if prim_attr else []
        attr += [dict(level=self.__shade)] if self.__shade else []
        return tuple(attr)

    def __record(self, cell, value, attr) -> None:
        new_info = Entry.ValueInfo(value, self.__prim_attr(attr))
        prev_value = cell.value()
        prev_info = Entry.ValueInfo(prev_value, self.__prim_attr(cell.attr())) if prev_value else None
        History.add(Entry(cell, new_info, prev_info))

    def __prim_attr(self, attr) -> str:
        return next((prim_attr for prim_attr in DisplayAttrs.ATTRS_PRIMARY if prim_attr in attr), None)

    def __is_guess(self, entry) -> bool:
        return entry.valueinfo.prim_attr == DisplayAttrs.GUESS

    def __lighten_shade(self) -> None:
        self.__shade = max(self.__shade - self.SHADE_STEP, 0)
