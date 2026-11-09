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

from game.eliminations_setting import EliminationsSetting
from game.rules.order import RULES
from game.rules.rule import Move, Outcome
from game.user_interface import Message, MessageKind, Step

if TYPE_CHECKING:
    from game.puzzle import Puzzle


class PuzzleSolver:
    """
    Find and make the next obvious move in a puzzle: one at a time, explained first (next), or all of them (auto).

    The rules come from rules/order.py and are consulted in that order.  The puzzle provides the rules'
    first_cell_where(), plus select(), enter_solved_value() and is_complete().
    """

    def __init__(self, puzzle: "Puzzle", rules=RULES):
        self.__puzzle = puzzle
        self.__rules = [rule() for rule in rules]
        self.__pending_move = None  # a move pointed out by next(), made by the following next()

    # Interface required for the puzzle

    def next(self) -> Message:
        """Point out the next move and why, the following next() making it; or return why there is no move"""
        if self.__pending_move:
            self.__make_pending_move()
            return None
        return self.__point_out_next_move()

    def auto(self) -> Message:
        """Make every obvious move, one after another; return why it stopped, or None once the puzzle is complete"""
        move = self.find_move()
        while move and move.outcome is Outcome.MOVED:
            self.__puzzle.select(move.cell)
            self.make_move(move)
            move = self.find_move()
        return None if self.__puzzle.is_complete() else self.__why_solving_stopped(move)

    def pending_hint(self) -> Message:
        """Return why the move pointed out by next() is right, or None if there is none"""
        move = self.__pending_move
        return Message(move.hint, MessageKind.HINT, highlight=move.highlight) if move else None

    def cancel_pending_move(self) -> None:
        self.__pending_move = None

    def find_move(self) -> Move:
        """Return the move of the first rule that has one, or None"""
        moves = (rule.find(self.__puzzle) for rule in self.__rules)
        return next((move for move in moves if move), None)

    def ruled_out(self) -> dict:
        """Return {(cell, value): Elimination} for every value the rules rule out of a cell now"""
        ruled_out = {}
        for rule in self.__rules:
            ruled_out.update(rule.eliminations(self.__puzzle))
        return ruled_out

    def removed(self, setting: EliminationsSetting) -> dict:
        """
        Return {(cell, value): Elimination}, in the order found, for the values the setting takes off the cells: what its
        rules rule out, then what they rule out once those are gone, until they rule out nothing more
        """
        rules = [rule for rule in self.__rules if setting.includes(rule)]
        removed, count = {}, None
        while count != len(removed):
            count = len(removed)
            for rule in rules:
                for found, why in rule.eliminations(self.__puzzle, removed).items():
                    removed.setdefault(found, why)
        return removed

    def removal_steps(self, cell, setting: EliminationsSetting) -> list:
        """Return the Steps explaining what the setting takes off the cell: every removal needed for it, oldest first"""
        removed = self.removed(setting)
        chain = self.__chain_of(cell, removed)
        numbers = {found: number for number, found in enumerate(chain, 1)}
        return [self.__step(found, removed[found], numbers) for found in chain]

    def make_move(self, move) -> None:
        """Fill in the value of a move that fills a cell"""
        self.__puzzle.enter_solved_value(move.cell, move.value)

    # Private functions

    def __make_pending_move(self) -> None:
        move, self.__pending_move = self.__pending_move, None
        self.make_move(move)

    def __point_out_next_move(self) -> Message:
        """Move to the next move's cell and keep it as the pending move, or return why there is none"""
        move = self.find_move()
        if move and move.outcome is Outcome.MOVED:
            self.__puzzle.select(move.cell)
            self.__pending_move = move
            return None
        return self.__why_solving_stopped(move)

    def __why_solving_stopped(self, move) -> Message:
        """Return a STOPPED move's hint, moving to its cell if it has one; with no move, a guess is needed"""
        if move is None:
            return Message("No obvious next move. You'll have to make a guess. ", MessageKind.WARNING)
        if move.cell is not None:
            self.__puzzle.select(move.cell)
        return Message(move.hint, MessageKind.WARNING, move.missing())

    def __chain_of(self, cell, removed) -> list:
        """Return, in the order found, each (cell, value) removed from the cell and each one those rely on"""
        needed, to_follow = set(), [found for found in removed if found[0] is cell]
        while to_follow:
            found = to_follow.pop()
            if found not in needed:
                needed.add(found)
                to_follow.extend(removed[found].relied_on)
        return [found for found in removed if found in needed]

    def __step(self, found, elimination, numbers) -> Step:
        """Return the step for one removal, numbered among the others, its short text for a line too narrow for it all"""
        cell, value = found
        count = f"({numbers[found]}/{len(numbers)}) "
        reason = elimination.why + self.__see_steps(elimination.relied_on, numbers)
        text = f"{count}{value} is ruled out here: {reason} [{elimination.rule}] "
        short = f"{count}{value} ruled out: {reason}"
        return Step(cell, Message(text, MessageKind.INFO, short=short, highlight=elimination.highlight))

    def __see_steps(self, relied_on, numbers) -> str:
        """Return which earlier steps the removals relied on come from, such as: (see steps 1, 2); or nothing if none"""
        if not relied_on:
            return ""
        steps = sorted(numbers[found] for found in relied_on)
        return f" (see step{'s' if len(steps) > 1 else ''} {', '.join(map(str, steps))})"
