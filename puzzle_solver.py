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

sys.path.insert(0, ".")

from rules.order import RULES
from rules.rule import Outcome


class PuzzleSolver:
    """
    Find and make the next obvious move in a puzzle.

    The rules come from rules/order.py and are applied in that order.
    """

    def __init__(self, puzzle, rules=RULES):
        self.__puzzle = puzzle
        self.__rules = [rule() for rule in rules]

    def next_move(self) -> Outcome:
        """Apply the rules in order; return the outcome of the first one that acts, or Outcome.NONE"""
        for rule in self.__rules:
            outcome = rule.apply(self.__puzzle)
            if outcome is not Outcome.NONE:
                return outcome
        return Outcome.NONE
