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

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from game.house import House
from game.user_interface import Highlight

if TYPE_CHECKING:
    from game.cell import Cell, RuledOut
    from game.puzzle import Puzzle


class Outcome(Enum):
    MOVED = "moved"  # the move fills in a cell
    STOPPED = "stopped"  # the move is a warning about something that blocks solving


@dataclass(frozen=True)
class Move:
    """A move found by a rule: a value to fill in (MOVED), or a warning that stops solving (STOPPED)"""

    outcome: Outcome
    hint: str  # why this is the next move, or the warning that stops solving
    cell: "Cell | None" = None  # the cell to fill in or to point the player at, if any
    value: int | None = None  # the value to fill in (MOVED), or the value that has no place left (STOPPED)
    house: House | None = None  # the house the value has no place left in (STOPPED)
    highlight: Highlight | None = None  # what the hint points at on the board, if anything
    reasons: "Eliminations | None" = None  # {(cell, value): Elimination} for each removal the move needs, oldest first, if it comes with its own

    def missing(self) -> tuple["Cell", int] | None:
        """Return (cell, value) for a warning about a value with no place left, to show it in the cell; or None"""
        return (self.cell, self.value) if self.outcome is Outcome.STOPPED and self.cell and self.value else None


@dataclass(frozen=True)
class Elimination:
    """A value ruled out of a cell"""

    why: str  # why it is ruled out, such as: in box 2, 4 can only go in row 1
    rule: str  # the NAME of the rule that ruled it out
    relied_on: tuple[tuple["Cell", int], ...] = ()  # each (cell, value) that had to be ruled out first
    highlight: Highlight | None = None  # what the reason points at on the board, if anything

    @staticmethod
    def needed_for(removals: Iterable[tuple["Cell", int]], ruled_out: "Eliminations") -> "Eliminations":
        """Return {(cell, value): Elimination}, in the order found, for each of the removals and each one those rely on"""
        needed, to_follow = set(), list(removals)
        while to_follow:
            found = to_follow.pop()
            if found not in needed:
                needed.add(found)
                to_follow.extend(ruled_out[found].relied_on)
        return {found: why for found, why in ruled_out.items() if found in needed}


type Eliminations = dict[tuple[Cell, int], Elimination]  # {(cell, value): Elimination} for values ruled out of cells


class Rule(ABC):
    """
    A solving rule: it looks at the puzzle and returns at most one move, without making it.

    Rules use only the puzzle's interface for the solver (first_cell_where(), houses() and everything_ruled_out()); the solver and
    the puzzle make the move. Each rule has a NAME, which ends the hint of every move it finds, so the
    player learns which rule found it.  A rule can also rule values out of cells (eliminations()), which
    the puzzle never stores: tagged cells leave them out of what they must be.
    """

    NAME = ""  # shown in brackets after each hint, e.g. "[single value]"
    LEVEL = None  # the level of a rule that rules values out, which the player can choose to see removed

    @abstractmethod
    def find(self, puzzle: "Puzzle") -> Move | None:
        """Return this rule's move in the puzzle, or None if it has none"""

    def eliminations(self, puzzle: "Puzzle", ruled_out: "RuledOut" = frozenset()) -> Eliminations:
        """
        Return {(cell, value): Elimination} for each value this rule rules out of a cell now, once each (cell, value)
        in ruled_out is left out; most rules rule out none
        """
        return {}

    # Interface required for subclasses

    def _move(
        self, outcome: Outcome, hint: str, cell: "Cell | None" = None, value: int | None = None, house: House | None = None,
        highlight: Highlight | None = None, reasons: Eliminations | None = None,
    ) -> Move:
        """Return a move whose hint ends with this rule's name"""
        return Move(outcome, f"{hint} [{self.NAME}] ", cell, value, house, highlight, reasons)

    def _listed(self, items: Iterable[object]) -> str:
        """Return the items as the player reads them, such as: 4 and 7"""
        *rest, last = map(str, items)
        return f"{', '.join(rest)} and {last}" if rest else last

    def _named(self, cells: Iterable["Cell"]) -> str:
        """Return where the cells are, counted from 1, such as: (1,2) and (1,5)"""
        return self._listed(f"({cell.row + 1},{cell.col + 1})" for cell in cells)
