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

from abc import ABC, abstractmethod

sys.path.insert(0, ".")

from history import History, Entry

from commands import Commands
from cell import Cell
from display import Display, echo
from display_attrs import DisplayAttrs
from puzzle_solver import PuzzleSolver
from rules.rule import Outcome


class Puzzle(ABC):
    """
    The generic Sudoku puzzle: everything that does not depend on how the blocks are laid out.

    A layout is a subclass (in the puzzles folder) that provides:
        NAME - the name shown to the player
        __init__() - calls super().__init__(v_cells, h_cells) with the overall size, then builds its blocks
        _blocks() - yield every block
        _block_at(row, col) - return the block holding the cell at a puzzle row and column

    Main relies on the following attributes:
        selected_cell - (row: int, col: int) - a tuple that represents the currently selected cell
        is_playing - bool - True if user is still playing the puzzle, False otherwise

    And the following methods:
        render() -
        display_status() -
        command_received(cmd) - called before each command is carried out
        force_quit_() - stop playing at once, without asking (CTRL-C)

    In addition, the puzzle should support all the commands available in commands.py.  Function
    names for commands have underscore (_) as a suffix to eliminate conflicts with reserved words.
    """

    BG_LEVEL_DELTA = 10

    def __init__(self, v_cells, h_cells):
        # Public attributes required for all puzzles
        self.selected_cell = (0, 0)  # row, col (NOT x, y)
        self.is_playing = True

        History.clear()
        Display.geometry({"h_cells": h_cells, "v_cells": v_cells})
        Display.validate_screen_size()

        self._initializing = True
        self._bg_level = 0
        self.__solver = PuzzleSolver(self)
        self.__pending_move = None  # a move shown as a hint by "n", made by the next "n"
        self.__reported_completion = None  # the completion last reported on the status line
        self.__unseen_completion = None  # a completion shown on the status line until the next command

    # Interface required for Main

    def render(self) -> None:
        Display.clear_screen()
        for block in self._blocks():
            block.render()
        self.display_status()

    def display_status(self) -> None:
        """Show a newly changed completion, or the pending move's hint, if any, otherwise the command summary"""
        Display.move_to_status_line()
        pending = self.__pending_move
        hint = Display.styled(pending.hint, (DisplayAttrs.SOLVED,)) if pending else None
        status = self.__completion_message() or hint or Commands.short_help()
        echo(status + Display.term.clear_eol)

    def command_received(self, cmd) -> None:
        """Any command ends the completion report; any command other than "n" cancels the move a previous "n" pointed out"""
        self.__unseen_completion = None
        if cmd != "next_":
            self.__pending_move = None

    def force_quit_(self) -> None:
        self.is_playing = False

    # Interface required for blocks

    def cells_in_row_or_col(self, row, col):
        """Yield the cells in the given row or column, as identified by each block"""
        for block in self._blocks():
            yield from block.cells_in_row_or_col(row, col)

    # Interface required for Main: one method per command in Commands

    def quit_(self) -> None:
        Display.confirm("Really quit?") and self.force_quit_()

    def help_(self) -> None:
        Display.clear_screen()
        print(Commands.long_help())
        Display.hit_any_key_to_continue()
        self.render()

    def value_(self, val, guess=False) -> None:
        guess and not self._initializing and self.__increment_bg_level()
        attr = self.__attributes(DisplayAttrs.GUESS if guess else None)
        cell = self.__selected_cell()
        (
            Display.warn("Cannot change an initial value while playing. ", wait=True)
            if not self._initializing and DisplayAttrs.INITIAL in cell.attr()
            else self.__accept_user_value(val, attr, cell)
        )

    def up_(self) -> None:
        self.__move(-1, 0)

    def down_(self) -> None:
        self.__move(1, 0)

    def left_(self) -> None:
        self.__move(0, -1)

    def right_(self) -> None:
        self.__move(0, 1)

    def play_(self) -> None:
        self._initializing = False
        Commands.use(Commands.PLAY_COMMANDS)
        self.display_status()

    def init_(self) -> None:
        if self.__check_for_active_play():
            return
        self._initializing = True
        Commands.use(Commands.INIT_COMMANDS)
        self.display_status()

    def del_(self) -> None:
        if not self._initializing:
            Display.warn("Deleting a cell value can only be done while initializing the puzzle. ", wait=True)
            return
        self.__selected_cell().update(None)

    def undo_(self) -> None:
        self.__undo_history() if not History.is_empty() else self.__warn_nothing_to_undo()

    def rewind_(self) -> None:
        if History.is_empty():
            self.__warn_nothing_to_undo()
        elif Display.confirm("Rewind cannot be undone.  Really rewind?"):
            self.__rewind_history()

    def next_(self) -> None:
        """Point out the next move and why; the next "n" makes it"""
        if self.__is_complete():
            self.__warn_already_complete()
        elif self.__pending_move:
            self.__make_pending_move()
        else:
            self.__point_out_next_move()

    def auto_(self) -> None:
        """Make every obvious move, one after another, until the puzzle is complete, a guess is needed or something blocks solving"""
        if self.__is_complete():
            self.__warn_already_complete()
            return
        move = self.__solver.find_move()
        while move and move.outcome is Outcome.MOVED:
            self.select(move.cell)
            self.__solver.make_move(move)
            move = self.__solver.find_move()
        self.__is_complete() or self.__warn_why_solving_stopped(move)

    # Interface required for the solver

    def first_cell_where(self, condition) -> Cell:
        """Return the first cell, left to right and top to bottom, for which condition(cell) is true, or None"""
        cells = (cell for block in self._blocks() for cell in block.cells_where(condition))
        return min(cells, key=lambda cell: (cell.row, cell.col), default=None)

    def select(self, cell) -> None:
        self.selected_cell = (cell.row, cell.col)

    def enter_solved_value(self, cell, value) -> None:
        """Enter a value found by the solver, the same way as a typed value but marked SOLVED"""
        self.__accept_user_value(value, self.__attributes(DisplayAttrs.SOLVED), cell)

    # Interface required from layout subclasses

    @abstractmethod
    def _blocks(self):
        """Yield every block of the layout"""

    @abstractmethod
    def _block_at(self, row, col):
        """Return the block that holds the cell at the given puzzle row and column"""

    # Private functions

    def __completion_message(self) -> str:
        """Report the puzzle's completion when it changes: solved in steel blue, or with errors in yellow"""
        completion = self.__completion()
        if completion != self.__reported_completion:
            self.__reported_completion = completion
            self.__unseen_completion = completion
        return {
            None: None,
            "solved": Display.styled("The puzzle is solved. ", (DisplayAttrs.SOLVED,)),
            "errors": Display.term.yellow(f"The puzzle is complete, with errors - {self.__how_to_fix_errors()}. "),
        }[self.__unseen_completion]

    def __completion(self) -> str:
        """None until the puzzle is complete, then 'solved' or 'errors'"""
        if not self.__is_complete():
            return None
        return "errors" if self.__has_errors() else "solved"

    def __is_complete(self) -> bool:
        """True while playing once every cell holds a value"""
        return not self._initializing and self.first_cell_where(lambda cell: cell.value() is None) is None

    def __has_errors(self) -> bool:
        return self.first_cell_where(Cell.is_marked_in_conflict) is not None

    def __how_to_fix_errors(self) -> str:
        """Values entered while playing can be undone or changed; with none entered, the errors are in the setup"""
        return "use ESC and then change values to fix them" if History.is_empty() else "undo or change values to fix them"

    def __increment_bg_level(self) -> None:
        self._bg_level += self.BG_LEVEL_DELTA
        self._bg_level > DisplayAttrs.MAX_GRAY_LEVEL and Display.warn(
            "No more shades of gray left - repeating last shade. ", wait=True
        )

    def __attributes(self, prim_attr) -> tuple:
        """Primary attribute: INITIAL while initializing, else prim_attr (if any); plus background shading"""
        attr = [DisplayAttrs.INITIAL] if self._initializing else [prim_attr] if prim_attr else []
        attr += [dict(level=self._bg_level)] if self._bg_level else []
        return tuple(attr)

    def __selected_cell(self) -> Cell:
        return self.__cell(*self.selected_cell)

    def __cell(self, row, col) -> Cell:
        return self._block_at(row, col).cell(row, col)

    def __accept_user_value(self, val, attr: tuple, cell: Cell) -> None:
        self._initializing or self.__add_history(cell, val, attr)
        cell.update(val, attr)

    def __add_history(self, cell, val, attr) -> None:
        new_info = Entry.ValueInfo(val, self.__prim_attr(attr))
        prev_val = cell.value()
        prev_info = Entry.ValueInfo(prev_val, self.__prim_attr(cell.attr())) if prev_val else None
        History.add(Entry(cell, new_info, prev_info))

    def __prim_attr(self, attr) -> str:
        return next((prim_attr for prim_attr in DisplayAttrs.ATTRS_PRIMARY if prim_attr in attr), None)

    def __move(self, d_row, d_col) -> None:
        """Move the selected cell, stopping at the edges of the puzzle"""
        row, col = self.selected_cell
        row = min(max(row + d_row, 0), Display.geom["v_cells"] - 1)
        col = min(max(col + d_col, 0), Display.geom["h_cells"] - 1)
        self.selected_cell = (row, col)

    def __check_for_active_play(self) -> bool:
        is_actively_playing = not History.is_empty()
        is_actively_playing and Display.warn(
            "Cannot initialize puzzle while playing - undo everything first. ", wait=True
        )
        return is_actively_playing

    def __undo_history(self) -> None:
        entry = History.undo()
        self.select(entry.cell)
        self.__is_guess(entry) and self.__decrement_bg_level()
        prev_val = entry.previous_valueinfo.value if entry.previous_valueinfo else None
        prev_attr = (
            self.__attributes(entry.previous_valueinfo.prim_attr)
            if entry.previous_valueinfo
            else ()
        )
        entry.cell.update(prev_val, prev_attr)

    def __is_guess(self, entry) -> bool:
        return entry.valueinfo.prim_attr == DisplayAttrs.GUESS

    def __decrement_bg_level(self) -> None:
        self._bg_level = max(self._bg_level - self.BG_LEVEL_DELTA, 0)

    def __warn_nothing_to_undo(self) -> None:
        Display.warn("Cannot undo initialized puzzle.  ESC will re-enter initialization mode. ", wait=True)

    def __rewind_history(self) -> None:
        """Undo at least one entry, then keep undoing until the most recent entry is a guess or none are left"""
        self.__undo_history()
        while not History.is_empty() and not self.__is_guess(History.last()):
            self.__undo_history()
        History.is_empty() or self.select(History.last().cell)

    def __warn_already_complete(self) -> None:
        Display.warn(
            f"The puzzle is already complete, with errors - {self.__how_to_fix_errors()}. "
            if self.__has_errors()
            else "The puzzle is already solved. ",
            wait=True,
        )

    def __make_pending_move(self) -> None:
        move, self.__pending_move = self.__pending_move, None
        self.__solver.make_move(move)

    def __point_out_next_move(self) -> None:
        """Move to the next move's cell and show its hint (made by the next "n"), or warn why there is none"""
        move = self.__solver.find_move()
        if move and move.outcome is Outcome.MOVED:
            self.select(move.cell)
            self.__pending_move = move
        else:
            self.__warn_why_solving_stopped(move)

    def __warn_why_solving_stopped(self, move) -> None:
        """Warn with a STOPPED move's hint, moving to its cell if it has one; with no move, a guess is needed"""
        if move is None:
            Display.warn("No obvious next move. You'll have to make a guess. ", wait=True)
            return
        move.cell is None or self.select(move.cell)
        Display.warn(move.hint, wait=True)
