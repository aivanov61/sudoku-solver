# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
#
# See sudoku.py for full copyright notice.
# -----------------------------------------------------------------------------

import sys

sys.path.insert(0, ".")

from commands import Commands
from display import Display, echo
from display_attrs import DisplayAttrs
from rectangular_block import RectangularBlock


class Puzzle3x3:
    H_BLOCKS = 3
    V_BLOCKS = 3
    BG_LEVEL_DELTA = 10

    def __init__(self):
        Display.geometry({"h_cells": self.H_BLOCKS**2, "v_cells": self.V_BLOCKS**2})
        Display.validate_screen_size()

        self._blocks = [[None for _col in range(self.H_BLOCKS)] for _row in range(self.V_BLOCKS)]
        for block_row in range(self.H_BLOCKS):
            for block_col in range(self.V_BLOCKS):
                self._blocks[block_row][block_col] = RectangularBlock(
                    self, row=block_row, col=block_col, rows=self.V_BLOCKS, cols=self.H_BLOCKS
                )

        self.selected_cell = (0, 0)  # row, col (NOT x, y)
        self.is_playing = True
        self.initializing = True
        self.bg_level = 0

    def render(self):
        Display.clear_screen()
        for block_row in range(self.H_BLOCKS):
            for block_col in range(self.V_BLOCKS):
                self._blocks[block_row][block_col].render()
        self.display_status()

    def block(self, row, col) -> RectangularBlock:
        return self._blocks[row // self.V_BLOCKS][col // self.H_BLOCKS]

    def display_status(self):
        Display.move_to_status_line()
        echo(Commands.short_help() + Display.term.clear_eol)

    # Interface methods for commands (corresponding to commands in Commands)

    def quit(self):
        self.is_playing = False

    def help(self):
        Display.clear_screen()
        print(Commands.long_help())
        Display.hit_any_key_to_continue()
        self.render()

    def value(self, val, guess=False):
        row, col = self.selected_cell
        self.__increment_bg_level() if guess and not self.initializing else 0
        attr = [DisplayAttrs.INITIAL] if self.initializing else [DisplayAttrs.GUESS] if guess else []
        attr += [dict(level=self.bg_level)] if self.bg_level else []
        self.block(row, col).cell(row, col).update(val, tuple(attr))

    def up(self):
        row, col = self.selected_cell
        row = row - 1 if row > 0 else row
        self.selected_cell = (row, col)

    def down(self):
        row, col = self.selected_cell
        row = row + 1 if row < Display.geom["v_cells"] - 1 else row
        self.selected_cell = (row, col)

    def left(self):
        row, col = self.selected_cell
        col = col - 1 if col > 0 else col
        self.selected_cell = (row, col)

    def right(self):
        row, col = self.selected_cell
        col = col + 1 if col < Display.geom["h_cells"] - 1 else col
        self.selected_cell = (row, col)

    def play(self):
        self.initializing = False
        Commands.CMDS = dict(list(Commands.COMMON_CMDS.items()) + list(Commands.PLAY_COMMANDS.items()))
        self.display_status()

    def init(self):
        self.initializing = True
        Commands.CMDS = dict(list(Commands.COMMON_CMDS.items()) + list(Commands.INIT_COMMANDS.items()))
        self.display_status()

    def undo(self):
        new_level = self.bg_level - self.BG_LEVEL_DELTA
        self.bg_level = new_level if new_level >= 0 else 0

    def __increment_bg_level(self):
        new_level = self.bg_level + self.BG_LEVEL_DELTA
        if new_level > 100:
            Display.warn("No more shades of gray left - using last shade. ", wait=True)
        else:
            self.bg_level = new_level
