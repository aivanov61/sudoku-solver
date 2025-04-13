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

from history import History, Entry

from commands import Commands
from cell import Cell
from display import Display, echo
from display_attrs import DisplayAttrs
from rectangular_block import RectangularBlock


class Puzzle3x3:
    """
    Implement a 3x3 puzzle.

    All puzzles are required to have a minimum interface consisting of the following attributes:
        selected_cell - (row: int, col: int) - a tuple that represents the currently selected cell
        is_playing - bool - True if user is still playing the puzzle, False otherwise

    And the following methods:
        render() -
        display_status() -

    In addition, the puzzle should support all the commands available in commands.py.  Function
    names for commands have underscore (_) as a suffix to eliminate conflicts with reserved words.

    """

    H_BLOCKS = 3
    V_BLOCKS = 3
    BG_LEVEL_DELTA = 10

    def __init__(self):
        # Public attributes required for all puzzles
        self.selected_cell = (0, 0)  # row, col (NOT x, y)
        self.is_playing = True

        History.clear()
        Display.geometry({"h_cells": self.H_BLOCKS**2, "v_cells": self.V_BLOCKS**2})
        Display.validate_screen_size()

        self._blocks = [[None for _col in range(self.H_BLOCKS)] for _row in range(self.V_BLOCKS)]
        for block_row in range(self.H_BLOCKS):
            for block_col in range(self.V_BLOCKS):
                self._blocks[block_row][block_col] = RectangularBlock(
                    self, row=block_row, col=block_col, rows=self.V_BLOCKS, cols=self.H_BLOCKS
                )

        self._initializing = True
        self._bg_level = 0

    # Required public interface methods

    def render(self) -> None:
        Display.clear_screen()
        for block_row in range(self.H_BLOCKS):
            for block_col in range(self.V_BLOCKS):
                self._blocks[block_row][block_col].render()
        self.display_status()

    def display_status(self) -> None:
        Display.move_to_status_line()
        echo(Commands.short_help() + Display.term.clear_eol)

    # Interface methods for commands (corresponding to commands in Commands)

    def quit_(self) -> None:
        self.is_playing = False

    def help_(self) -> None:
        Display.clear_screen()
        print(Commands.long_help())
        Display.hit_any_key_to_continue()
        self.render()

    def value_(self, val, guess=False) -> None:
        guess and not self._initializing and self.__increment_bg_level()
        attr = self.__attributes(guess)
        cell = self.__selected_cell()
        (
            Display.warn("Cannot change an initial value while playing. ", wait=True)
            if not self._initializing and DisplayAttrs.INITIAL in cell.attr()
            else self.__accept_user_value(val, attr, cell)
        )

    def up_(self) -> None:
        row, col = self.selected_cell
        row = row - 1 if row > 0 else row
        self.selected_cell = (row, col)

    def down_(self) -> None:
        row, col = self.selected_cell
        row = row + 1 if row < Display.geom["v_cells"] - 1 else row
        self.selected_cell = (row, col)

    def left_(self) -> None:
        row, col = self.selected_cell
        col = col - 1 if col > 0 else col
        self.selected_cell = (row, col)

    def right_(self) -> None:
        row, col = self.selected_cell
        col = col + 1 if col < Display.geom["h_cells"] - 1 else col
        self.selected_cell = (row, col)

    def play_(self) -> None:
        self._initializing = False
        Commands.CMDS = dict(list(Commands.COMMON_CMDS.items()) + list(Commands.PLAY_COMMANDS.items()))
        self.display_status()

    def init_(self) -> None:
        if self.__check_for_active_play():
            return
        self._initializing = True
        Commands.CMDS = dict(list(Commands.COMMON_CMDS.items()) + list(Commands.INIT_COMMANDS.items()))
        self.display_status()

    def del_(self) -> None:
        if not self._initializing:
            Display.warn("Deleting a cell value can only be done while initializing the puzzle. ", wait=True)
            return
        self.__selected_cell().update(None)

    def undo_(self) -> None:
        (
            self.__undo_history()
            if not History.is_empty()
            else Display.warn("Cannot undo initialized puzzle.  ESC will re-enter initialization mode. ", wait=True)
        )

    # Private functions

    def __increment_bg_level(self) -> None:
        self._bg_level += self.BG_LEVEL_DELTA
        self._bg_level > DisplayAttrs.MAX_GRAY_LEVEL and Display.warn(
            "No more shades of gray left - repeating last shade. ", wait=True
        )

    def __attributes(self, guess) -> set:
        """Determine primary attribute(s): INITIAL or GUESS (or normal) plus background shading"""
        attr = [DisplayAttrs.INITIAL] if self._initializing else [DisplayAttrs.GUESS] if guess else []
        attr += [dict(level=self._bg_level)] if self._bg_level else []
        return set(attr)

    def __selected_cell(self) -> Cell:
        row, col = self.selected_cell
        return self.__block(row, col).cell(row, col)

    def __accept_user_value(self, val, attr: set, cell: Cell) -> None:
        self._initializing or self.__add_history(cell, val, attr)
        cell.update(val, attr)

    def __block(self, row, col) -> RectangularBlock:
        return self._blocks[row // self.V_BLOCKS][col // self.H_BLOCKS]

    def __add_history(self, cell, val, attr) -> None:
        new_info = Entry.ValueInfo(val, self.__prim_attr(attr))
        prev_val = cell.value()
        prev_info = Entry.ValueInfo(prev_val, self.__prim_attr(cell.attr())) if prev_val else None
        History.add(Entry(cell, new_info, prev_info))

    def __prim_attr(self, attr) -> str:
        prim_attr = DisplayAttrs.INITIAL if DisplayAttrs.INITIAL in attr else None
        prim_attr = prim_attr or (DisplayAttrs.GUESS if DisplayAttrs.GUESS in attr else None)
        return prim_attr

    def __check_for_active_play(self) -> bool:
        is_actively_playing = not History.is_empty()
        is_actively_playing and Display.warn(
            "Cannot initialize puzzle while playing - undo everything first. ", wait=True
        )
        return is_actively_playing

    def __undo_history(self) -> None:
        entry = History.undo()
        self.selected_cell = (entry.cell.row, entry.cell.col)
        entry.valueinfo.prim_attr == DisplayAttrs.GUESS and self.__decrement_bg_level()
        prev_val = entry.previous_valueinfo.value if entry.previous_valueinfo else None
        prev_attr = (
            self.__attributes(entry.previous_valueinfo.prim_attr == DisplayAttrs.GUESS)
            if entry.previous_valueinfo
            else ()
        )
        entry.cell.update(prev_val, prev_attr)

    def __decrement_bg_level(self) -> None:
        self._bg_level = max(self._bg_level - self.BG_LEVEL_DELTA, 0)
