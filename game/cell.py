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

from typing import TYPE_CHECKING

from game.border import Border
from game.cell_attrs import CellAttrs
from game.cell_solver import CellSolver
from game.house import House
from game.marks_setting import MarksSetting

if TYPE_CHECKING:
    from game.rectangular_block import RectangularBlock


class Cell:
    """
    A Cell is the basic building block of a Sudoku puzzle.

    Each cell has a parent which is the block of cells.  The block defines
    how the cell relates to the block and to other cells in the block.

    It is able to perform the following:
    1. Store and retrieve a value with set()/value()
    1. Keep the player's tag with set_tagged()/is_tagged(), whatever its value
    1. Honor legal values provided by the block
    1. Report every change to its value, attributes, possible values, marks or tag to its parent, so they can be shown
    1. Trigger recalculation of other puzzle cell values when this cell value changes
    """

    def __init__(self, parent: "RectangularBlock", row: int = 0, col: int = 0, borders: Border = Border()):
        self._value = None
        self._solver = CellSolver(parent)  # Use the Solver class
        self._attrs = tuple()
        self._marks = ()  # the "must be" marks (Snyder notation) the cell shows
        self._tagged = False  # tagged by the player, to pick the cell out
        self._parent = parent
        self.row = row
        self.col = col
        self.borders = borders

    def value(self) -> int:
        return self._value

    def attr(self) -> tuple:
        """Return the attributes."""
        return self._attrs

    def set(self, value, attrs=()) -> None:
        """Set the cell value and attributes, reporting any change"""
        if value and value not in self._parent.values():
            raise ValueError(f"Cell value must be in {self._parent.values()}")
        before = (self._value, self._attrs)
        self._attrs = attrs
        self.__mark_if_conflicting(value)
        if value != self._value:
            self.__smart_update(value)
        if (self._value, self._attrs) != before:
            self.__report_change()

    def possible_values(self) -> set:
        return self._solver.possible_values()

    def marks(self) -> tuple:
        """Return the "must be" marks (Snyder notation): possible values with few places left in the cell's houses"""
        return self._marks

    def is_tagged(self) -> bool:
        return self._tagged

    def set_tagged(self, tagged) -> None:
        """Tag the cell for the player, or untag it, reporting any change; the tag stays whatever the cell's value"""
        if tagged != self._tagged:
            self._tagged = tagged
            self.__report_change()

    # Interface required for blocks

    def single_possible_value(self) -> int:
        return self._solver.single_possible_value()

    def hidden_single(self) -> tuple:
        """
        Return (value, house) for the lowest value that can go nowhere else in one of the cell's houses,
        looking in its box first, then its row and column; or None if there is none
        """
        is_only_place = lambda house, value: house.places(value) == [self]
        return self.__first_in_houses(sorted(self.possible_values()), is_only_place)

    def unplaceable_value(self) -> tuple:
        """
        Return (value, house) for the lowest value missing from one of the empty cell's houses with no place left
        there, looking in its box first, then its row and column; or None if there is none or the cell has a value
        """
        if self._value:
            return None
        return self.__first_in_houses(self._parent.values(), House.has_no_place_for)

    def is_dead_end(self) -> bool:
        """Return True if the cell is empty but no value fits it"""
        return not self._value and not self.possible_values()

    def is_marked_in_conflict(self) -> bool:
        return any(attr in CellAttrs.CONFLICT_ATTRS for attr in self._attrs)

    # Interface required for the board

    def refresh_marks(self, setting: MarksSetting) -> None:
        """Show the marks the setting asks for, reporting any change"""
        marks = self.__must_be(setting.threshold, setting.kinds) if setting.is_on() else ()
        if marks != self._marks:
            self._marks = marks
            self.__report_change()

    # Interface required for related cells

    def add_possible(self, value) -> None:
        """Add back a possible value, unless the cell has a value or a related cell holds it"""
        if not self._value and value not in self.possible_values() and not self.__is_held_by_related_cell(value):
            self._solver.add_possible(value)
            self.__report_change()

    def remove_possible(self, value) -> None:
        """Remove a possible value, reporting the change if it was possible"""
        if value in self.possible_values():
            self._solver.remove_possible(value)
            self.__report_change()

    def mark_conflicted(self, value) -> None:
        """Mark the cell as conflicted if it holds the value just entered in a related cell"""
        if value == self._value and not self.is_marked_in_conflict():
            self.__add_attr(CellAttrs.CONFLICTED)
            self.__report_change()

    def clear_resolved_conflict(self, value) -> None:
        """Clear the cell's conflict mark if it holds the value and no related cell holds it any more"""
        if value == self._value and self.is_marked_in_conflict() and not self.__is_held_by_related_cell(value):
            self._attrs = tuple(attr for attr in self._attrs if attr not in CellAttrs.CONFLICT_ATTRS)
            self.__report_change()

    # Private functions

    def __mark_if_conflicting(self, value) -> None:
        if value and self.__is_held_by_related_cell(value):
            self.__add_attr(CellAttrs.CONFLICTING)

    def __is_held_by_related_cell(self, value) -> bool:
        return any(cell.value() == value for cell in self.__related_cells())

    def __related_cells(self):
        return self._parent.related_cells(self.row, self.col)

    def __add_attr(self, attr) -> None:
        self._attrs = (*self._attrs, attr)

    def __smart_update(self, value) -> None:
        """
        The brains of the cell.  It will update the cell taking into account any logic/analysis required.
        """
        old_value, self._value = self._value, value
        for cell in self.__related_cells():
            if old_value:
                cell.add_possible(old_value)
                cell.clear_resolved_conflict(old_value)
            if value:
                cell.remove_possible(value)
                cell.mark_conflicted(value)
        if value:
            self.__clear_possible()
        else:
            self.__restore_possible()

    def __clear_possible(self) -> None:
        """Remove all possible values, reporting the change if there were any"""
        if self.possible_values():
            self._solver.clear_possible()
            self.__report_change()

    def __restore_possible(self) -> None:
        """Add back every value that no related cell holds"""
        for value in self._parent.values():
            self.add_possible(value)

    def __report_change(self) -> None:
        self._parent.cell_changed(self)

    def __must_be(self, threshold, kinds) -> tuple:
        """Return, in order, the possible values with threshold places or fewer in a house of the kinds"""
        houses = [house for house in self._parent.houses_of(self.row, self.col) if house.kind in kinds]
        few_places = lambda value: any(len(house.places(value)) <= threshold for house in houses)
        return tuple(value for value in sorted(self.possible_values()) if few_places(value))

    def __first_in_houses(self, values, applies) -> tuple:
        """
        Return (value, house) for the first of the values for which applies(house, value) is true, going through
        the cell's houses in turn, box first; or None
        """
        for house in self._parent.houses_of(self.row, self.col):
            for value in values:
                if applies(house, value):
                    return value, house
        return None
