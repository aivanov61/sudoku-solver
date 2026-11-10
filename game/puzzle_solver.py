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

from collections.abc import Iterable
from typing import TYPE_CHECKING

from game.eliminations_setting import EliminationsSetting
from game.rules.order import RULES
from game.rules.rule import Elimination, Eliminations, Move, Outcome, Rule
from game.user_interface import Message, MessageKind, Step

if TYPE_CHECKING:
    from game.cell import Cell
    from game.puzzle import Puzzle


class PuzzleSolver:
    """
    Find and make the next obvious move in a puzzle: one at a time, explained first (next), or all of them (auto).

    The rules come from rules/order.py and are consulted in that order.  The puzzle provides the rules'
    first_cell_where(), plus select(), enter_solved_value() and is_complete().
    """

    def __init__(self, puzzle: "Puzzle", rules: Iterable[type[Rule]] = RULES) -> None:
        self.__puzzle = puzzle
        self.__rules = [rule() for rule in rules]
        self.__pending_move = None  # a move pointed out by next(), made by the following next()

    # Interface required for the puzzle

    def next(self) -> Message | None:
        """Point out the next move and why, the following next() making it; or return why there is no move"""
        if self.__pending_move:
            self.__make_pending_move(self.__pending_move)
            return None
        return self.__point_out_next_move()

    def auto(self) -> Message | None:
        """Make every obvious move, one after another; return why it stopped, or None once the puzzle is complete"""
        move = self.find_move()
        while move and move.outcome is Outcome.MOVED:
            self.__select_cell_of(move)
            self.make_move(move)
            move = self.find_move()
        return None if self.__puzzle.is_complete() else self.__why_solving_stopped(move)

    def pending_hint(self) -> Message | None:
        """Return why the move pointed out by next() is right, or None if there is none"""
        move = self.__pending_move
        return Message(move.hint, MessageKind.HINT, highlight=move.highlight) if move else None

    def cancel_pending_move(self) -> None:
        self.__pending_move = None

    def find_move(self) -> Move | None:
        """Return the move of the first rule that has one, or None"""
        moves = (rule.find(self.__puzzle) for rule in self.__rules)
        return next((move for move in moves if move), None)

    def ruled_out(self) -> Eliminations:
        """Return {(cell, value): Elimination} for every value the rules rule out of a cell now"""
        ruled_out: Eliminations = {}
        for rule in self.__rules:
            ruled_out.update(rule.eliminations(self.__puzzle))
        return ruled_out

    def removed(self, setting: EliminationsSetting) -> Eliminations:
        """
        Return {(cell, value): Elimination}, in the order found, for the values the setting takes off the cells: what its
        rules rule out, then what they rule out once those are gone, until they rule out nothing more
        """
        return self.__cascade([rule for rule in self.__rules if setting.includes(rule)])

    def everything_ruled_out(self) -> Eliminations:
        """Return {(cell, value): Elimination}, in the order found, for what all the rules rule out together, whatever the level"""
        return self.__cascade(self.__rules)

    def removal_steps(self, cell: "Cell", setting: EliminationsSetting) -> list[Step]:
        """
        Return the Steps explaining the move pointed out, if it comes with removals of its own, or else what the
        setting takes off the cell: every removal needed for it, oldest first
        """
        pending = self.__pending_move
        if pending and pending.reasons:
            return self.__steps(pending.reasons)
        removed = self.removed(setting)
        return self.__steps(Elimination.needed_for([found for found in removed if found[0] is cell], removed))

    def make_move(self, move: Move) -> None:
        """Fill in the value of a move that fills a cell"""
        assert move.cell and move.value, "a move that fills a cell names the cell and the value"
        self.__puzzle.enter_solved_value(move.cell, move.value)

    # Private functions

    def __make_pending_move(self, move: Move) -> None:
        self.__pending_move = None
        self.make_move(move)

    def __select_cell_of(self, move: Move) -> None:
        """Move to the cell of a move that fills one"""
        assert move.cell, "a move that fills a cell names the cell"
        self.__puzzle.select(move.cell)

    def __point_out_next_move(self) -> Message | None:
        """Move to the next move's cell and keep it as the pending move, or return why there is none"""
        move = self.find_move()
        if move and move.outcome is Outcome.MOVED:
            self.__select_cell_of(move)
            self.__pending_move = move
            return None
        return self.__why_solving_stopped(move)

    def __why_solving_stopped(self, move: Move | None) -> Message:
        """Return a STOPPED move's hint, moving to its cell if it has one; with no move, a guess is needed"""
        if move is None:
            return Message("No obvious next move. You'll have to make a guess. ", MessageKind.WARNING)
        if move.cell is not None:
            self.__puzzle.select(move.cell)
        return Message(move.hint, MessageKind.WARNING, move.missing())

    def __cascade(self, rules: list[Rule]) -> Eliminations:
        """Return {(cell, value): Elimination}, in the order found: what the rules rule out, then what they rule out once those are gone, and so on"""
        removed: Eliminations = {}
        count = None
        while count != len(removed):
            count = len(removed)
            for rule in rules:
                for found, why in rule.eliminations(self.__puzzle, removed).items():
                    removed.setdefault(found, why)
        return removed

    def __steps(self, reasons: Eliminations) -> list[Step]:
        """Return the Step for each of the {(cell, value): Elimination}, numbered in order"""
        numbers = {found: number for number, found in enumerate(reasons, 1)}
        return [self.__step(found, why, numbers) for found, why in reasons.items()]

    def __step(self, found: tuple["Cell", int], elimination: Elimination, numbers: dict[tuple["Cell", int], int]) -> Step:
        """Return the step for one removal, numbered among the others, its short text for a line too narrow for it all"""
        cell, value = found
        count = f"({numbers[found]}/{len(numbers)}) "
        reason = elimination.why + self.__see_steps(elimination.relied_on, numbers)
        text = f"{count}{value} is ruled out here: {reason} [{elimination.rule}] "
        short = f"{count}{value} ruled out: {reason}"
        return Step(cell, Message(text, MessageKind.INFO, short=short, highlight=elimination.highlight))

    def __see_steps(self, relied_on: tuple[tuple["Cell", int], ...], numbers: dict[tuple["Cell", int], int]) -> str:
        """Return which earlier steps the removals relied on come from, such as: (see steps 1, 2); or nothing if none"""
        if not relied_on:
            return ""
        steps = sorted(numbers[found] for found in relied_on)
        return f" (see step{'s' if len(steps) > 1 else ''} {', '.join(map(str, steps))})"
