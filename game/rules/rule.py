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
from dataclasses import dataclass
from enum import Enum


class Outcome(Enum):
    MOVED = "moved"  # the move fills in a cell
    STOPPED = "stopped"  # the move is a warning about something that blocks solving


@dataclass(frozen=True)
class Move:
    """A move found by a rule: a value to fill in (MOVED), or a warning that stops solving (STOPPED)"""

    outcome: Outcome
    hint: str  # why this is the next move, or the warning that stops solving
    cell: object = None  # the cell to fill in or to point the player at, if any
    value: int = None  # the value to fill in (MOVED only)


class Rule(ABC):
    """
    A solving rule: it looks at the puzzle and returns at most one move, without making it.

    Rules use only the puzzle's interface for the solver (first_cell_where()); the solver and the
    puzzle make the move. Each rule has a NAME, which ends the hint of every move it finds, so the
    player learns which rule found it.
    """

    NAME = None  # shown in brackets after each hint, e.g. "[single value]"

    @abstractmethod
    def find(self, puzzle) -> Move:
        """Return this rule's move in the puzzle, or None if it has none"""

    # Interface required for subclasses

    def _move(self, outcome, hint, cell=None, value=None) -> Move:
        """Return a move whose hint ends with this rule's name"""
        return Move(outcome, f"{hint} [{self.NAME}] ", cell, value)
