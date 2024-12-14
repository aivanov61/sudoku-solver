# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
#
# See sudoku.py for full copyright notice.
# -----------------------------------------------------------------------------

import sys
sys.path.insert(0, '.')

from commands import Commands
from display import Display, echo
from rectangular_block import RectangularBlock

class Puzzle3x3:
    H_BLOCKS = 3
    V_BLOCKS = 3

    def __init__(self):
        Display.geometry({'h_cells': self.H_BLOCKS ** 2 , 'v_cells': self.V_BLOCKS ** 2})
        Display.validate_screen_size()

        self._blocks = [[None for _col in range(self.H_BLOCKS)] for _row in range(self.V_BLOCKS)]
        for block_row in range(self.H_BLOCKS):
            for block_col in range(self.V_BLOCKS):
                self._blocks[block_row][block_col] = RectangularBlock(self, row=block_row, col=block_col, rows=self.V_BLOCKS, cols=self.H_BLOCKS)

        self.selected_cell = (0,0) # row, col (NOT x, y)
        self.is_playing = True

    def render(self):
        Display.clear_screen()
        for block_row in range(self.H_BLOCKS):
            for block_col in range(self.V_BLOCKS):
                self._blocks[block_row][block_col].render()
        self.display_status()

    def block(self, row, col):
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
        echo('Hit any key to continue: ')
        try:
            with Display.term.cbreak():
                Display.term.inkey()
        except:
            pass
        self.render()

    def value(self, val, guess=False):
        row, col = self.selected_cell
        self.block(row, col).cell(row, col).update(val, guess)

    def up(self):
        row, col = self.selected_cell
        row = row - 1 if row > 0 else row
        self.selected_cell = (row, col)

    def down(self):
        row, col = self.selected_cell
        row = row + 1 if row < Display.geom['v_cells'] - 1 else row
        self.selected_cell = (row, col)

    def left(self):
        row, col = self.selected_cell
        col = col - 1 if col > 0 else col
        self.selected_cell = (row, col)

    def right(self):
        row, col = self.selected_cell
        col = col + 1 if col < Display.geom['h_cells'] - 1 else col
        self.selected_cell = (row, col)

    def play(self):
        Commands.CMDS = dict(list(Commands.COMMON_CMDS.items()) + list(Commands.PLAY_COMMANDS.items()))
        self.display_status()

    def init(self):
        Commands.CMDS = dict(list(Commands.COMMON_CMDS.items()) + list(Commands.INIT_COMMANDS.items()))
        self.display_status()
