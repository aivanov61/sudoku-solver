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

from display import Display
from rules.order import RULES
from rules.rule import Move, Outcome


class PuzzleSolver:
    """
    Find and make the next obvious move in a puzzle: one at a time, explained first (next), or all of them (auto).

    The rules come from rules/order.py and are consulted in that order.  The puzzle provides the rules'
    first_cell_where(), plus select(), enter_solved_value() and is_complete().
    """

    def __init__(self, puzzle, rules=RULES):
        self.__puzzle = puzzle
        self.__rules = [rule() for rule in rules]
        self.__pending_move = None  # a move pointed out by next(), made by the following next()

    # Interface required for the puzzle

    def next(self) -> None:
        """Point out the next move and why; the following next() makes it"""
        if self.__pending_move:
            self.__make_pending_move()
        else:
            self.__point_out_next_move()

    def auto(self) -> None:
        """Make every obvious move, one after another, until the puzzle is complete, a guess is needed or something blocks solving"""
        move = self.find_move()
        while move and move.outcome is Outcome.MOVED:
            self.__puzzle.select(move.cell)
            self.make_move(move)
            move = self.find_move()
        self.__puzzle.is_complete() or self.__warn_why_solving_stopped(move)

    def pending_hint(self) -> str:
        """Return why the move pointed out by next() is right, or None if there is none"""
        return self.__pending_move.hint if self.__pending_move else None

    def cancel_pending_move(self) -> None:
        self.__pending_move = None

    def find_move(self) -> Move:
        """Return the move of the first rule that has one, or None"""
        moves = (rule.find(self.__puzzle) for rule in self.__rules)
        return next((move for move in moves if move), None)

    def make_move(self, move) -> None:
        """Fill in the value of a move that fills a cell"""
        self.__puzzle.enter_solved_value(move.cell, move.value)

    # Private functions

    def __make_pending_move(self) -> None:
        move, self.__pending_move = self.__pending_move, None
        self.make_move(move)

    def __point_out_next_move(self) -> None:
        """Move to the next move's cell and keep it as the pending move, or warn why there is none"""
        move = self.find_move()
        if move and move.outcome is Outcome.MOVED:
            self.__puzzle.select(move.cell)
            self.__pending_move = move
        else:
            self.__warn_why_solving_stopped(move)

    def __warn_why_solving_stopped(self, move) -> None:
        """Warn with a STOPPED move's hint, moving to its cell if it has one; with no move, a guess is needed"""
        if move is None:
            Display.warn("No obvious next move. You'll have to make a guess. ", wait=True)
            return
        move.cell is None or self.__puzzle.select(move.cell)
        Display.warn(move.hint, wait=True)
