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

from game.rules.rule import Move, Outcome, Rule


class EliminatingRule(Rule):
    """
    A rule that rules values out of cells.  find() returns a single value or hidden single that only these
    eliminations leave, with a hint explaining both; each subclass says what it rules out.
    """

    def find(self, puzzle) -> Move:
        ruled_out = self.eliminations(puzzle)
        if not ruled_out:
            return None
        cell = puzzle.first_cell_where(lambda cell: cell.forced_value(ruled_out) and not cell.forced_value())
        if cell is None:
            return None
        return self.__move_into(cell, ruled_out)

    @abstractmethod
    def eliminations(self, puzzle, ruled_out=frozenset()) -> dict:
        """Return {(cell, value): Elimination} for each value ruled out of a cell, as in Rule.eliminations()"""

    # Interface required for subclasses

    def _listed(self, items) -> str:
        """Return the items as the player reads them, such as: 4 and 7"""
        *rest, last = map(str, items)
        return f"{', '.join(rest)} and {last}"

    def _named(self, cells) -> str:
        """Return where the cells are, counted from 1, such as: (1,2) and (1,5)"""
        return self._listed(f"({cell.row + 1},{cell.col + 1})" for cell in cells)

    # Private functions

    def __move_into(self, cell, ruled_out) -> Move:
        """Return the move filling in the value the eliminations force into the cell, explaining why"""
        candidates = cell.candidates(ruled_out)
        if len(candidates) == 1:
            value = next(iter(candidates))
            ruled = next(other for other in sorted(cell.possible_values()) if (cell, other) in ruled_out)
            elimination = ruled_out[(cell, ruled)]
            hint = f"Only {value} fits here: {elimination.why}, which rules {ruled} out here."
        else:
            value, house = cell.hidden_single(ruled_out)
            elimination = next(ruled_out[(other, value)] for other in house.cells if (other, value) in ruled_out)
            hint = f"{value} fits nowhere else in its {house.kind}: {elimination.why}."
        return self._move(Outcome.MOVED, hint, cell, value, highlight=elimination.highlight)
