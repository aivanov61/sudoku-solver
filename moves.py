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
from cell_attrs import CellAttrs
from history import History, Entry


class Moves:
    """
    Enter values into cells and record them in a History, so they can be undone.

    Values entered while the puzzle is set up are givens, which are not recorded.  While playing,
    each guess puts itself (and thus every value entered after it) one guess deeper.

    The puzzle provides is_initializing(); the user interface hears of every change of guess depth.
    """

    def __init__(self, puzzle, ui):
        self.__puzzle = puzzle
        self.__ui = ui
        self.__guess_depth = 0
        self.__history = History()

    # Interface required for the puzzle

    def enter(self, cell, value, prim_attr=None) -> None:
        """Enter a value with its primary attribute (None for a typed value) and record it while playing"""
        is_playing = not self.__puzzle.is_initializing()
        prim_attr == CellAttrs.GUESS and is_playing and self.__one_guess_deeper()
        attr = self.__attributes(prim_attr)
        is_playing and self.__record(cell, value, attr)
        cell.set(value, attr)

    def is_empty(self) -> bool:
        return self.__history.is_empty()

    def undo(self) -> Cell:
        """Undo the most recent move, putting back the cell's previous value, and return the cell"""
        entry = self.__history.undo()
        self.__is_guess(entry) and self.__one_guess_shallower()
        previous = entry.previous_valueinfo
        value, attr = (previous.value, self.__attributes(previous.prim_attr)) if previous else (None, ())
        entry.cell.set(value, attr)
        return entry.cell

    def rewind(self) -> Cell:
        """Undo moves until the most recent one is a guess (at least one) and return its cell, or the last cell undone"""
        cell = self.undo()
        while not self.__history.is_empty() and not self.__is_guess(self.__history.last()):
            cell = self.undo()
        return cell if self.__history.is_empty() else self.__history.last().cell

    def recorded(self) -> list:
        """Return every recorded move as (row, col, value, prim_attr), oldest first"""
        return [
            (entry.cell.row, entry.cell.col, entry.valueinfo.value, entry.valueinfo.prim_attr)
            for entry in self.__history.entries()
        ]

    def clear(self) -> None:
        self.__history.clear()
        self.__set_guess_depth(0)

    # Private functions

    def __one_guess_deeper(self) -> None:
        self.__set_guess_depth(self.__guess_depth + 1)

    def __set_guess_depth(self, depth) -> None:
        """Change the guess depth, telling the user interface if it changed"""
        depth != self.__guess_depth and self.__ui.guess_depth_changed(depth)
        self.__guess_depth = depth

    def __attributes(self, prim_attr) -> tuple:
        """Primary attribute: INITIAL while initializing, else prim_attr (if any); plus the guess depth"""
        attr = [CellAttrs.INITIAL] if self.__puzzle.is_initializing() else [prim_attr] if prim_attr else []
        attr += [dict(depth=self.__guess_depth)] if self.__guess_depth else []
        return tuple(attr)

    def __record(self, cell, value, attr) -> None:
        new_info = Entry.ValueInfo(value, self.__prim_attr(attr))
        prev_value = cell.value()
        prev_info = Entry.ValueInfo(prev_value, self.__prim_attr(cell.attr())) if prev_value else None
        self.__history.add(Entry(cell, new_info, prev_info))

    def __prim_attr(self, attr) -> str:
        return next((prim_attr for prim_attr in CellAttrs.PRIMARY if prim_attr in attr), None)

    def __is_guess(self, entry) -> bool:
        return entry.valueinfo.prim_attr == CellAttrs.GUESS

    def __one_guess_shallower(self) -> None:
        self.__set_guess_depth(max(self.__guess_depth - 1, 0))
