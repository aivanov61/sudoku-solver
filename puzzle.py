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

from commands import Commands
from cell import Cell
from completion_report import CompletionReport
from display import Display, echo
from display_attrs import DisplayAttrs
from game_file import GameFile
from moves import Moves
from puzzle_solver import PuzzleSolver
from rules.dead_end_rule import DeadEndRule
from save_file import SavedPuzzle


class Puzzle:
    """
    The game played on a board: the commands, the setup and play modes, the cursor and the screen.

    The board (a layout's Board subclass, from the puzzles folder) holds the cells; the puzzle reaches
    them only through it.

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

    The puzzle hands parts of its work to helpers: Moves (entering values, undo and guess shading),
    PuzzleSolver (next and auto), CompletionReport (telling the player the puzzle is complete) and
    GameFile (save and restore).
    """

    def __init__(self, board):
        # Public attributes required for all puzzles
        self.selected_cell = (0, 0)  # row, col (NOT x, y)
        self.is_playing = True

        Display.geometry({"h_cells": board.h_cells, "v_cells": board.v_cells})
        Display.validate_screen_size()

        self._initializing = True
        self.__notice = None  # a warning shown on the status line until the next command
        self.__board = board
        self.__moves = Moves(self)
        self.__solver = PuzzleSolver(self)
        self.__report = CompletionReport(self)
        self.__game_file = GameFile(self)

    # Interface required for Main

    def render(self) -> None:
        Display.clear_screen()
        self.__board.render()
        self.__draw_commands()
        self.display_status()

    def display_status(self) -> None:
        """Show a notice, a newly changed completion, or why the move "n" pointed out is right, if any; otherwise leave it blank"""
        Display.move_to_status_line()
        hint = self.__solver.pending_hint()
        status = self.__notice or self.__report.message() or (Display.styled(hint, (DisplayAttrs.SOLVED,)) if hint else "")
        echo(status + Display.term.clear_eol)

    def command_received(self, cmd) -> None:
        """Any command ends the notice and the completion report; any command other than "n" cancels the move a previous "n" pointed out"""
        self.__notice = None
        self.__report.seen()
        cmd == "next_" or self.__solver.cancel_pending_move()

    def force_quit_(self) -> None:
        self.is_playing = False

    # Interface required for Main: one method per command in Commands

    def quit_(self) -> None:
        Display.confirm("Really quit?") and self.force_quit_()

    def help_(self) -> None:
        Display.clear_screen()
        print(Commands.long_help())
        Display.hit_any_key_to_continue()
        self.render()

    def value_(self, val, guess=False) -> None:
        """Enter the value in the selected cell, then point out any dead end"""
        cell = self.__selected_cell()
        if not self._initializing and DisplayAttrs.INITIAL in cell.attr():
            Display.warn("Cannot change an initial value while playing. ", wait=True)
            return
        self.__moves.enter(cell, val, DisplayAttrs.GUESS if guess else None)
        self.__found_dead_end()

    def up_(self) -> None:
        self.__move(-1, 0)

    def down_(self) -> None:
        self.__move(1, 0)

    def left_(self) -> None:
        self.__move(0, -1)

    def right_(self) -> None:
        self.__move(0, 1)

    def play_(self) -> None:
        self.__setup_blocks_playing() or self.__switch_mode(initializing=False)

    def init_(self) -> None:
        self.__check_for_active_play() or self.__switch_mode(initializing=True)

    def del_(self) -> None:
        if not self._initializing:
            Display.warn("Deleting a cell value can only be done while initializing the puzzle. ", wait=True)
            return
        self.__selected_cell().update(None)

    def undo_(self) -> None:
        if self.__refused_while_initializing():
            return
        self.select(self.__moves.undo()) if not self.__moves.is_empty() else self.__warn_nothing_to_undo()

    def rewind_(self) -> None:
        if self.__refused_while_initializing():
            return
        if self.__moves.is_empty():
            self.__warn_nothing_to_undo()
        elif Display.confirm("Rewind cannot be undone.  Really rewind?"):
            self.select(self.__moves.rewind())

    def next_(self) -> None:
        """Point out the next move and why; the next "n" makes it"""
        self.__solving_refused() or self.__solver.next()

    def auto_(self) -> None:
        """Make every obvious move, one after another, until the puzzle is complete, a guess is needed or something blocks solving"""
        self.__solving_refused() or self.__solver.auto()

    def save_(self) -> None:
        self.__game_file.save()

    def open_(self) -> None:
        self.__game_file.restore()

    # Interface required for the solver and the other helpers

    def first_cell_where(self, condition) -> Cell:
        """Return the first cell, left to right and top to bottom, for which condition(cell) is true, or None"""
        return self.__board.first_cell_where(condition)

    def select(self, cell) -> None:
        self.selected_cell = (cell.row, cell.col)

    def enter_solved_value(self, cell, value) -> None:
        """Enter a value found by the solver, the same way as a typed value but marked SOLVED"""
        self.__moves.enter(cell, value, DisplayAttrs.SOLVED)

    def is_initializing(self) -> bool:
        return self._initializing

    def is_complete(self) -> bool:
        """True while playing once every cell holds a value"""
        return not self._initializing and self.__board.is_full()

    def has_conflicts(self) -> bool:
        return self.__board.has_conflicts()

    def has_values(self) -> bool:
        return self.__board.has_values()

    def layout_name(self) -> str:
        return self.__board.NAME

    def saved_state(self) -> SavedPuzzle:
        """Everything needed to restore the puzzle: its layout, mode, cursor, givens and recorded moves"""
        board = self.__board
        return SavedPuzzle(board.NAME, self._initializing, self.selected_cell, board.givens(), self.__moves.recorded())

    def restore(self, saved) -> None:
        """Empty the board, enter the givens in setup mode, replay the moves in the saved mode, then point out any dead end"""
        self.__clear_board()
        for row, col, value in saved.givens:
            self.__moves.enter(self.__board.cell(row, col), value)
        self.__use_mode(saved.initializing)
        for row, col, value, prim_attr in saved.moves:
            self.__moves.enter(self.__board.cell(row, col), value, prim_attr)
        self.selected_cell = saved.selected_cell
        self.render()
        self.__found_dead_end()

    # Private functions

    def __draw_commands(self) -> None:
        Display.draw_command_panel("SETUP" if self._initializing else "PLAY", Commands.panel())

    def __selected_cell(self) -> Cell:
        return self.__board.cell(*self.selected_cell)

    def __found_dead_end(self) -> bool:
        """Point out the first dead end, if any, moving to it without waiting; return whether there was one"""
        dead_end = self.__board.first_dead_end()
        if dead_end is None:
            return False
        self.select(dead_end)
        self.__notice = Display.term.yellow(
            "This square has no possible values left - change the setup before playing. "
            if self._initializing
            else DeadEndRule.WARNING
        )
        return True

    def __move(self, d_row, d_col) -> None:
        """Move the selected cell, stopping at the edges of the board"""
        row, col = self.selected_cell
        row = min(max(row + d_row, 0), self.__board.v_cells - 1)
        col = min(max(col + d_col, 0), self.__board.h_cells - 1)
        self.selected_cell = (row, col)

    def __setup_blocks_playing(self) -> bool:
        """Warn if the setup has conflicts, or a dead end (moving to it), which would block solving"""
        if self.__board.has_conflicts():
            Display.warn("Resolve the conflicts before playing. ", wait=True)
            return True
        return self.__found_dead_end()

    def __switch_mode(self, initializing) -> None:
        self.__use_mode(initializing)
        self.__draw_commands()
        self.display_status()

    def __use_mode(self, initializing) -> None:
        self._initializing = initializing
        Commands.use(Commands.INIT_COMMANDS if initializing else Commands.PLAY_COMMANDS)

    def __check_for_active_play(self) -> bool:
        is_actively_playing = not self.__moves.is_empty()
        is_actively_playing and Display.warn(
            "Cannot initialize puzzle while playing - undo everything first. ", wait=True
        )
        return is_actively_playing

    def __refused_while_initializing(self) -> bool:
        """Warn that a play command was used in setup mode, returning whether it was"""
        self._initializing and Display.warn("This works only while playing - ESC starts playing. ", wait=True)
        return self._initializing

    def __warn_nothing_to_undo(self) -> None:
        Display.warn("Cannot undo initialized puzzle.  ESC will re-enter initialization mode. ", wait=True)

    def __solving_refused(self) -> bool:
        """Warn, returning True, if "n" or "a" cannot solve: in setup mode, or once the puzzle is complete"""
        if self.__refused_while_initializing():
            return True
        is_complete = self.is_complete()
        is_complete and self.__report.warn_already_complete()
        return is_complete

    def __clear_board(self) -> None:
        """Empty every cell and forget the moves and the last completion report, back in setup mode"""
        self.__board.clear()
        self.__moves.clear()
        self.__report.reset()
        self._initializing = True
