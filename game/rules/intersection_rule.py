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

from abc import abstractmethod
from typing import TYPE_CHECKING

from game.house import House
from game.rules.eliminating_rule import EliminatingRule
from game.rules.rule import Elimination, Eliminations
from game.user_interface import Highlight

if TYPE_CHECKING:
    from game.cell import Cell, RuledOut
    from game.puzzle import Puzzle


class IntersectionRule(EliminatingRule):
    """
    Where a box crosses a row or column: a value that can only go in the crossing, within one of the two houses
    (the source), can go nowhere else in the other one, so it is ruled out of the rest of it.

    Each subclass says which houses are its sources.
    """

    LEVEL = "intersections"

    def eliminations(self, puzzle: "Puzzle", ruled_out: "RuledOut" = frozenset()) -> Eliminations:
        found: Eliminations = {}
        for source in puzzle.houses():
            if self._is_source(source):
                for value in source.values_left():
                    self.__rule_out(value, source, ruled_out, found)
        return found

    # Interface required from subclasses

    @abstractmethod
    def _is_source(self, house: House) -> bool:
        """Return True if the rule looks for values confined to a crossing within this house"""

    # Private functions

    def __rule_out(self, value: int, source: House, ruled_out: "RuledOut", found: Eliminations) -> None:
        """Find the value ruled out of the rest of a house of another kind that holds every place it has left in the source"""
        places = source.places(value, ruled_out)
        target = self.__house_holding(places, source) if len(places) > 1 else None
        if target is None:
            return
        removed = [cell for cell in target.places(value, ruled_out) if cell not in source.cells]
        if removed:
            elimination = self.__elimination(value, source, target, places, removed, ruled_out)
            for cell in removed:
                self._keep_simplest(found, (cell, value), elimination)

    def __house_holding(self, places: list["Cell"], source: House) -> House | None:
        """Return the house, of another kind than the source, that holds every one of the places; or None"""
        holds_all = lambda house: house.kind != source.kind and all(place in house.cells for place in places)
        return next((house for house in places[0].houses() if holds_all(house)), None)

    def __elimination(
        self, value: int, source: House, target: House, places: list["Cell"], removed: list["Cell"], ruled_out: "RuledOut",
    ) -> Elimination:
        """Return why the value is out of the rest of the target, relying on what left it only in the crossing, its places"""
        why = f"in {source.name()}, {value} can only go in {target.name()}"
        gone = tuple(cell for cell in source.cells if (cell, value) in ruled_out and cell not in target.cells)
        box = source if source.kind == House.BOX else target
        still_can = dict.fromkeys([*places, *self.__only_places_left(value, removed, ruled_out)], (value,))
        blocked = (cell for cell in source.cells if not cell.value() and cell not in places)
        highlight = Highlight(box, still_can, dict.fromkeys((*removed, *blocked), (value,)))
        return Elimination(why, self.NAME, tuple((cell, value) for cell in gone), highlight)

    def __only_places_left(self, value: int, removed: list["Cell"], ruled_out: "RuledOut") -> list["Cell"]:
        """Return the one place the value has left in each box that losing it from the removed cells leaves with just one"""
        after = {*ruled_out, *((cell, value) for cell in removed)}
        boxes = (next(house for house in cell.houses() if house.kind == House.BOX) for cell in removed)
        left = (box.places(value, after) for box in boxes)
        return [places[0] for places in left if len(places) == 1]
