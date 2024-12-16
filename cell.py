# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

from display import Display, Border


class Cell:
    """
    A Cell is the basic building block of a Sudoku puzzle.

    Each cell has a parent which is the block of cells.  The block defines
    how the cell relates to the block and to other cells in the block.

    It is able to perform the following:
    1. Store and retrieve a value with set()/value()
    1. Honor legal values provided by the block
    1. Display itself on the terminal
    """

    def __init__(self, parent, row=0, col=0, borders=Border()):
        self._value = None
        self._parent = parent
        self.row = row
        self.col = col
        self.borders = borders

    def value(self):
        return self._value

    def set(self, value):
        if value not in self._parent.values():
            raise ValueError(f"Cell value must be in {self._parent.values()}")
        self._value = value

    def update(self, value, guess=False):
        # TODO: set color
        self.set(value)
        Display.draw_cell_value(self.row, self.col, self._value or " ")

    def render(self):
        Display.draw_cell(self.row, self.col, self.borders)
        Display.draw_cell_value(self.row, self.col, self._value or " ")
