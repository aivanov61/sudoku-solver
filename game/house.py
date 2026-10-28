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


class House:
    """
    A group of cells that must hold every value exactly once: a box, a row or a column.

    Blocks give a cell its houses (houses_of); the kind names the house in hints.
    """

    BOX = "box"
    ROW = "row"
    COLUMN = "column"

    def __init__(self, kind: str, cells: list):
        self.kind = kind
        self.cells = cells

    def places(self, value, ruled_out=frozenset()) -> list:
        """Return the cells, in order, that can still hold the value, leaving out each (cell, value) ruled out"""
        return [cell for cell in self.cells if value in cell.possible_values() and (cell, value) not in ruled_out]

    def has_no_place_for(self, value) -> bool:
        """Return True if no cell holds the value and none can any more"""
        return not self.places(value) and all(cell.value() != value for cell in self.cells)
