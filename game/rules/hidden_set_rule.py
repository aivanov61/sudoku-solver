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

from itertools import combinations

from game.house import House
from game.rules.eliminating_rule import EliminatingRule
from game.rules.rule import Elimination
from game.user_interface import Highlight


class HiddenSetRule(EliminatingRule):
    """
    A set of values that between them can only go in as many cells of a house as there are values take every other
    value from those cells.  Each subclass says how many: its SIZE.
    """

    SIZE = None  # how many values share that many cells

    def eliminations(self, puzzle, ruled_out=frozenset()) -> dict:
        found = {}
        for house in puzzle.houses():
            for values in combinations(self.__values_with_few_places(house, ruled_out), self.SIZE):
                cells = [cell for cell in house.cells if cell.candidates(ruled_out).intersection(values)]
                if len(cells) == self.SIZE:
                    self.__rule_out(values, cells, house, ruled_out, found)
        return found

    # Private functions

    def __values_with_few_places(self, house: House, ruled_out) -> list:
        return [value for value in house.values_left() if 2 <= len(house.places(value, ruled_out)) <= self.SIZE]

    def __rule_out(self, values, cells, house: House, ruled_out, found) -> None:
        """Find every other value ruled out of the cells"""
        removed = [(cell, value) for cell in cells for value in sorted(cell.candidates(ruled_out)) if value not in values]
        if removed:
            elimination = self.__elimination(values, cells, house, ruled_out)
            for found_value in removed:
                self._keep_simplest(found, found_value, elimination)

    def __elimination(self, values, cells, house: House, ruled_out) -> Elimination:
        """Return why the other values are out of the cells, relying on what left the values only there"""
        why = f"in {house.name()}, {self._listed(values)} can only go in {self._named(cells)}"
        outside = [cell for cell in house.cells if cell not in cells]
        relied_on = tuple((cell, value) for cell in outside for value in values if (cell, value) in ruled_out)
        kept = {cell: tuple(value for value in values if value in cell.candidates(ruled_out)) for cell in cells}
        gone = dict.fromkeys((cell for cell in outside if not cell.value()), values)
        return Elimination(why, self.NAME, relied_on, Highlight(house, kept, gone))
