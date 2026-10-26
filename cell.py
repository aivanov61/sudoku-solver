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
        self.__mark_if_conflicting(value)
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

    def possible_values(self) -> set:
        return self._solver.possible_values()

    def single_possible_value(self) -> int:
        return self._solver.single_possible_value()

    def is_dead_end(self) -> bool:
        """Return True if the cell is empty but no value fits it"""
        return not self._value and not self.possible_values()

    def mark_conflicted(self, value) -> None:
        """Mark the cell as conflicted if it holds the value just entered in a related cell"""
        if value == self._value and not self.is_marked_in_conflict():
            self.__add_attr(DisplayAttrs.CONFLICTED)
            self.render()

    def is_marked_in_conflict(self) -> bool:
        return any(attr in DisplayAttrs.CONFLICT_ATTRS for attr in self._attrs)

    def clear_resolved_conflict(self, value) -> None:
        """Clear the cell's conflict mark if it holds the value and no related cell holds it any more"""
        if (
            value == self._value
            and self.is_marked_in_conflict()
            and not self._parent.is_held_by_related_cell(self.row, self.col, value)
        ):
            self._attrs = tuple(attr for attr in self._attrs if attr not in DisplayAttrs.CONFLICT_ATTRS)
            self.render()

    # Private functions

    def __draw_cell_values(self) -> None:
        Display.draw_cell_value(self.row, self.col, self._value or " ", self._attrs)
        self.__draw_possible_values()

    def __draw_possible_values(self) -> None:
        Display.draw_cell_possible_values(self.row, self.col, self.possible_values(), self._attrs)

    def __mark_if_conflicting(self, value) -> None:
        if value and self._parent.is_held_by_related_cell(self.row, self.col, value):
            self.__add_attr(DisplayAttrs.CONFLICTING)

    def __add_attr(self, attr) -> None:
        self._attrs = (*self._attrs, attr)

    def __smart_update(self, value) -> None:
        """
        The brains of the cell.  It will update the cell taking into account any logic/analysis required.
        """
        old_value, self._value = self._value, value
        old_value and self._parent.add_possible(self.row, self.col, old_value)
        old_value and self._parent.clear_resolved_conflicts(self.row, self.col, old_value)
        value and self._parent.remove_possible(self.row, self.col, value)
        value and self._parent.mark_conflicted(self.row, self.col, value)
        value and self.__clear_possible()
        value or self.__restore_possible()

    def __clear_possible(self) -> None:
        """Remove all possible values and redraw the possible values if they changed"""
        if self.possible_values():
            self._solver.clear_possible()
            self.__draw_possible_values()

    def __restore_possible(self) -> None:
        """Add back every value that no related cell holds"""
        for value in self._parent.values():
            self.add_possible(value)
