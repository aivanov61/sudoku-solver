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
        self._attrs = ()
        self._parent = parent
        self.row = row
        self.col = col
        self.borders = borders

    def value(self):
        return self._value

    def set(self, value, attrs=()):
        if value not in self._parent.values():
            raise ValueError(f"Cell value must be in {self._parent.values()}")
        self._value = value
        self._attrs = attrs

    def update(self, value, attrs=()):
        prev_attr = self._attrs
        self.set(value, attrs)
        (
            Display.draw_cell_value(self.row, self.col, self._value or " ", self._attrs)
            if prev_attr == self._attrs
            else self.render()
        )

    def render(self):
        Display.draw_cell(self.row, self.col, self.borders, self._attrs)
        Display.draw_cell_value(self.row, self.col, self._value or " ", self._attrs)
