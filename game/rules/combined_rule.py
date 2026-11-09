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

from game.rules.rule import Elimination, Move, Outcome, Rule

if TYPE_CHECKING:
    from game.puzzle import Puzzle


class CombinedRule(Rule):
    """
    The last resort: a value left to a cell only by what every rule rules out together, each building on the others,
    whatever the player chose to see removed.  Of the cells that leaves a value, the move is the one needing the fewest
    removals.  Its hint is short, and the move carries the removals it needs, for the player to walk through.
    """

    NAME = "combined rules"

    def find(self, puzzle: "Puzzle") -> Move:
        ruled_out = puzzle.everything_ruled_out()
        moves = [self.__move_into(cell, ruled_out) for cell in self.__newly_forced(puzzle, ruled_out)]
        return min(moves, key=lambda move: len(move.reasons), default=None)

    # Private functions

    def __newly_forced(self, puzzle: "Puzzle", ruled_out) -> list:
        """Return, left to right and top to bottom, each cell forced to hold a value only once the values are ruled out"""
        cells = {cell for house in puzzle.houses() for cell in house.cells}
        forced = [cell for cell in cells if cell.forced_value(ruled_out) and not cell.forced_value()]
        return sorted(forced, key=lambda cell: (cell.row, cell.col))

    def __move_into(self, cell, ruled_out) -> Move:
        """Return the move filling in the value the removals force into the cell"""
        candidates = cell.candidates(ruled_out)
        if len(candidates) == 1:
            value = next(iter(candidates))
            others = sorted(cell.possible_values() - candidates)
            verb = "are" if len(others) > 1 else "is"
            reason = f"Only {value} fits here once {self._listed(others)} {verb} ruled out"
            return self.__move(cell, value, reason, [(cell, other) for other in others], ruled_out)
        value, house = cell.hidden_single(ruled_out)
        others = [other for other in house.places(value) if other is not cell]
        reason = f"{value} fits nowhere else in its {house.kind} once it is ruled out of {self._named(others)}"
        return self.__move(cell, value, reason, [(other, value) for other in others], ruled_out)

    def __move(self, cell, value, reason, removals, ruled_out) -> Move:
        return self._move(Outcome.MOVED, f"{reason} (press w for why).", cell, value, reasons=Elimination.needed_for(removals, ruled_out))
