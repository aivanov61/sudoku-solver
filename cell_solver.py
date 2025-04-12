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


class CellSolver:
    """
    The CellSolver class is responsible for managing and calculating the possible values
    for a Sudoku cell. It will also handle logic to determine if a cell must contain
    a specific value based on the state of the puzzle.

    For now, it only contains the `_possible_values` attribute.
    """

    def __init__(self, cell_parent):
        self._possible_values = set(sorted(cell_parent.values()))

    def possible_values(self) -> set:
        """Return the set of possible values for the cell."""
        return self._possible_values
