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
from enum import Enum


class Outcome(Enum):
    NONE = "none"  # the rule found nothing to do
    MOVED = "moved"  # the rule filled in a cell
    STOPPED = "stopped"  # the rule found something that blocks solving, and warned about it


class Rule(ABC):
    """
    A solving rule: it looks at the puzzle and makes at most one move.

    Rules use only the puzzle's interface for the solver: first_cell_where(), select() and
    enter_solved_value().
    """

    @abstractmethod
    def apply(self, puzzle) -> Outcome:
        """Look for this rule's move in the puzzle and make it, if any"""
