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
from typing import TYPE_CHECKING

from game.house import House
from game.rules.eliminating_rule import EliminatingRule
from game.rules.rule import Elimination, Eliminations
from game.user_interface import Highlight

if TYPE_CHECKING:
    from game.cell import Cell, RuledOut
    from game.puzzle import Puzzle


class NakedSetRule(EliminatingRule):
    """
    A set of cells of a house that between them can only hold as many values as there are cells take those values
    from the rest of the house.  Each subclass says how many: its SIZE.
    """

    SIZE: int  # how many cells share that many values, set by each subclass

    def eliminations(self, puzzle: "Puzzle", ruled_out: "RuledOut" = frozenset()) -> Eliminations:
        found: Eliminations = {}
        for house in puzzle.houses():
            for cells in combinations(self.__cells_with_few_values(house, ruled_out), self.SIZE):
                values = sorted(set().union(*(cell.candidates(ruled_out) for cell in cells)))
                if len(values) == self.SIZE:
                    self.__rule_out(values, cells, house, ruled_out, found)
        return found

    # Private functions

    def __cells_with_few_values(self, house: House, ruled_out: "RuledOut") -> list["Cell"]:
        return [cell for cell in house.cells if 2 <= len(cell.candidates(ruled_out)) <= self.SIZE]

    def __rule_out(self, values: list[int], cells: tuple["Cell", ...], house: House, ruled_out: "RuledOut", found: Eliminations) -> None:
        """Find the values ruled out of the rest of the house"""
        lost = {other: tuple(v for v in values if v in other.candidates(ruled_out)) for other in house.cells if other not in cells}
        gone = {cell: digits for cell, digits in lost.items() if digits}
        elimination = self.__elimination(values, cells, house, gone, ruled_out)
        for cell, digits in gone.items():
            for value in digits:
                self._keep_simplest(found, (cell, value), elimination)

    def __elimination(
        self, values: list[int], cells: tuple["Cell", ...], house: House, gone: dict["Cell", tuple[int, ...]], ruled_out: "RuledOut",
    ) -> Elimination:
        """Return why the values are out of the rest of the house, relying on what left the cells with only those values"""
        why = f"in {house.name()}, {self._named(cells)} can only hold {self._listed(values)}"
        relied_on = tuple((cell, value) for cell in cells for value in sorted(cell.possible_values()) if (cell, value) in ruled_out)
        kept = {cell: tuple(sorted(cell.candidates(ruled_out))) for cell in cells}
        return Elimination(why, self.NAME, relied_on, Highlight(house, kept, gone))
