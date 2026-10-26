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

from cell_solver import CellSolver
from copy import deepcopy
from display import Display, Border
from display_attrs import DisplayAttrs


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
        self._solver = CellSolver(parent)  # Use the Solver class
        self._attrs = tuple()
        self._parent = parent
        self.row = row
        self.col = col
        self.borders = borders

    def value(self) -> int:
        return self._value

    def attr(self) -> tuple:
        """Return the attributes."""
        return self._attrs

    def update(self, value, attrs=tuple()) -> None:
        """Update the cell value and display it"""
        prev_attr = deepcopy(self._attrs)
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
        self._attrs = attrs
        value != self._value and self.__smart_update(value)

    def add_possible(self, value) -> None:
        """Add back a possible value, unless the cell has a value or a related cell holds it"""
        if (
            not self._value
            and value not in self.possible_values()
            and not self._parent.is_held_by_related_cell(self.row, self.col, value)
        ):
            self._solver.add_possible(value)
            self.__draw_possible_values()

    def remove_possible(self, value) -> None:
        """Remove a possible value and redraw the possible values if they changed"""
        if value in self.possible_values():
            self._solver.remove_possible(value)
            self.__draw_possible_values()

    def clear_possible(self) -> None:
        """Remove all possible values and redraw the possible values if they changed"""
        if self.possible_values():
            self._solver.clear_possible()
            self.__draw_possible_values()

    def possible_values(self) -> set:
        return self._solver.possible_values()

    # Private functions

    def __draw_cell_values(self) -> None:
        Display.draw_cell_value(self.row, self.col, self._value or " ", self._attrs)
        self.__draw_possible_values()

    def __draw_possible_values(self) -> None:
        Display.draw_cell_possible_values(self.row, self.col, self.possible_values(), self._attrs)

    def __smart_update(self, value) -> None:
        """
        The brains of the cell.  It will update the cell taking into account any logic/analysis required.
        """
        if value and self._parent.is_held_by_related_cell(self.row, self.col, value):
            self._attrs = (*self._attrs, DisplayAttrs.CONFLICTING)
        old_value, self._value = self._value, value
        old_value and self._parent.add_possible(self.row, self.col, old_value)
        value and self._parent.remove_possible(self.row, self.col, value)
        value and self.clear_possible()
        value or self.__restore_possible()

    def __restore_possible(self) -> None:
        """Add back every value that no related cell holds"""
        for value in self._parent.values():
            self.add_possible(value)
