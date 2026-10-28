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

import sys

from abc import abstractmethod

sys.path.insert(0, ".")

from game.house import House
from game.rules.rule import Move, Outcome, Rule


class IntersectionRule(Rule):
    """
    Where a box crosses a row or column: a value that can only go in the crossing, within one of the two houses
    (the source), can go nowhere else in the other one, so it is ruled out of the rest of it.

    Each subclass says which houses are its sources and how to say why a value is ruled out.  find() returns a
    single value or hidden single that only these eliminations leave, with a hint explaining both.
    """

    def find(self, puzzle) -> Move:
        ruled_out = self.eliminations(puzzle)
        if not ruled_out:
            return None
        cell = puzzle.first_cell_where(lambda cell: cell.forced_value(ruled_out) and not cell.forced_value())
        if cell is None:
            return None
        return self.__move_into(cell, ruled_out)

    def eliminations(self, puzzle) -> dict:
        ruled_out = {}
        for source in puzzle.houses():
            if self._is_source(source):
                for value in self.__values_left_in(source):
                    self.__rule_out(value, source, ruled_out)
        return ruled_out

    # Interface required from subclasses

    @abstractmethod
    def _is_source(self, house: House) -> bool:
        """Return True if the rule looks for values confined to a crossing within this house"""

    @abstractmethod
    def _reason(self, value, source: House, target: House) -> str:
        """Return why the value is ruled out of the rest of the target, such as: in one box, 4 can only go in one row"""

    # Private functions

    def __move_into(self, cell, ruled_out) -> Move:
        """Return the move filling in the value the eliminations force into the cell, explaining why"""
        candidates = cell.candidates(ruled_out)
        if len(candidates) == 1:
            value = next(iter(candidates))
            ruled = next(other for other in sorted(cell.possible_values()) if (cell, other) in ruled_out)
            hint = f"Only {value} fits here: {ruled_out[(cell, ruled)]}, which rules {ruled} out here."
        else:
            value, house = cell.hidden_single(ruled_out)
            reason = next(ruled_out[(other, value)] for other in house.cells if (other, value) in ruled_out)
            hint = f"{value} fits nowhere else in its {house.kind}: {reason}."
        return self._move(Outcome.MOVED, hint, cell, value)

    def __values_left_in(self, house) -> list:
        return sorted({value for cell in house.cells for value in cell.possible_values()})

    def __rule_out(self, value, source, ruled_out) -> None:
        """Rule the value out of the rest of a house of another kind that holds every place it has left in the source"""
        places = source.places(value)
        target = self.__house_holding(places, source) if len(places) > 1 else None
        if target is None:
            return
        for cell in target.places(value):
            if cell not in source.cells:
                ruled_out[(cell, value)] = self._reason(value, source, target)

    def __house_holding(self, places, source) -> House:
        """Return the house, of another kind than the source, that holds every one of the places; or None"""
        holds_all = lambda house: house.kind != source.kind and all(place in house.cells for place in places)
        return next((house for house in places[0].houses() if holds_all(house)), None)
