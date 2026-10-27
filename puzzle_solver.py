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
from rules.rule import Move


class PuzzleSolver:
    """
    Find and make the next obvious move in a puzzle.

    The rules come from rules/order.py and are consulted in that order.
    """

    def __init__(self, puzzle, rules=RULES):
        self.__puzzle = puzzle
        self.__rules = [rule() for rule in rules]

    def find_move(self) -> Move:
        """Return the move of the first rule that has one, or None"""
        moves = (rule.find(self.__puzzle) for rule in self.__rules)
        return next((move for move in moves if move), None)

    def make_move(self, move) -> None:
        """Fill in the value of a move that fills a cell"""
        self.__puzzle.enter_solved_value(move.cell, move.value)
