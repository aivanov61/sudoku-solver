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
    1. Trigger recalculation of other puzzle cell values when this cell value changes
    """

    def __init__(self, parent, row=0, col=0, borders=Border()):
        self._value = None
        self._possible_values = set(sorted(parent.values()))
        self._attrs = ()
        self._parent = parent
        self.row = row
        self.col = col
        self.borders = borders

    def value(self) -> int:
        return self._value

    def attr(self) -> tuple:
        return self._attrs

    def update(self, value, attrs=()) -> None:
        """Update the cell value and display it"""
        prev_attr = self._attrs
        self.set(value, attrs)
        self.__draw_cell_values() if prev_attr == self._attrs else self.render()

    def render(self) -> None:
        """Draw the cell and its current value"""
        Display.draw_cell(self.row, self.col, self.borders, self._attrs)
        self.__draw_cell_values()

    def set(self, value, attrs=()) -> None:
        """Set the cell value but not the display"""
        if value and value not in self._parent.values():
            raise ValueError(f"Cell value must be in {self._parent.values()}")
        value != self._value and self.__update_value(value)
        self._attrs = attrs

    # Private functions

    def __draw_cell_values(self) -> None:
        Display.draw_cell_value(self.row, self.col, self._value or " ", self._attrs)
        Display.draw_cell_possible_values(self.row, self.col, self._possible_values, self._attrs)

    def __update_value(self, value):
        self.__add_old_value_back_to_possible_values()
        self._value = value
        value and self._parent.remove_possible(self.row, self.col, value)

    def __add_old_value_back_to_possible_values(self) -> None:
        old_value = self._value
        self._value = None
        old_value and self._parent.add_possible(self.row, self.col, old_value)
