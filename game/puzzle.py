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

from game.actions import Action, Mode, OFFERED_ACTIONS
from game.board import Board
from game.cell import Cell
from game.cell_attrs import CellAttrs
from game.completion_report import CompletionReport
from game.game_file import GameFile
from game.marks_setting import MarksSetting
from game.moves import Moves
from game.puzzle_solver import PuzzleSolver
from game.rules.dead_end_rule import DeadEndRule
from game.save_file import SavedPuzzle
from game.user_interface import Message, MessageKind, UserInterface


class Puzzle:
    """
    The game played on a board: the commands, the setup and play modes, the cursor and the screen.

    The board (a layout's Board subclass, from the puzzles folder) holds the cells; the puzzle reaches
    them only through it.

    A user interface runs the game with the following attributes:
        selected_cell - (row: int, col: int) - a tuple that represents the currently selected cell
        is_playing - bool - True if user is still playing the puzzle, False otherwise

    And the following methods:
        render() - show the whole game afresh
        handle(action, digit) - carry out one action from the player
        force_quit_() - stop playing at once, without asking (e.g. when an action breaks)

    handle() calls the puzzle's method for the Action (see actions.py): the action's value with an
    underscore (_) as a suffix, to avoid conflicts with reserved words.

    The puzzle hands parts of its work to helpers: Moves (entering values, undo and guess shading),
    PuzzleSolver (next and auto), CompletionReport (telling the player the puzzle is complete) and
    GameFile (save and restore).  It shows messages and asks questions only through its user
    interface (see user_interface.py).
    """

    def __init__(self, board: Board, ui: UserInterface):
        # Public attributes required for all puzzles
        self.selected_cell = (0, 0)  # row, col (NOT x, y)
        self.is_playing = True

        self.__notice = None  # a warning or a new setting, shown on the status line until the next command
        self.__marks = MarksSetting()  # which "must be" marks to show while playing
        self.__board = board
        self.__ui = ui
        board.report_changes_to(ui.cell_changed)
        self.__use_mode(initializing=True)
        self.__moves = Moves(self, ui)
        self.__solver = PuzzleSolver(self)
        self.__report = CompletionReport(self)
        self.__game_file = GameFile(self, ui)

    # Interface required for user interfaces

    def render(self) -> None:
        self.__ui.show_board(self.__board.cells())
        self.display_status()

    def display_status(self) -> None:
        """Show a notice, a newly changed completion, or why the move "n" pointed out is right, if any; otherwise leave it blank"""
        self.__ui.status(self.__notice or self.__report.message() or self.__pending_hint())

    def handle(self, action, digit=None) -> None:
        """Carry out the player's action (with its digit, for values and guesses), then show the status"""
        self.__action_received(action)
        getattr(self, f"{action.value}_")(*([] if digit is None else [digit]))
        self.__refresh_marks()
        self.display_status()

    def force_quit_(self) -> None:
        self.is_playing = False

    # Interface required for handle(): one method per Action

    def quit_(self) -> None:
        if self.__ui.confirm("Really quit?"):
            self.force_quit_()

    def value_(self, val) -> None:
        self.__enter(val, None)

    def guess_(self, val) -> None:
        """Enter the value as a guess, which rewind can go back to; only while playing"""
        if not self.__refused_while_initializing():
            self.__enter(val, CellAttrs.GUESS)

    def up_(self) -> None:
        self.__move(-1, 0)

    def down_(self) -> None:
        self.__move(1, 0)

    def left_(self) -> None:
        self.__move(0, -1)

    def right_(self) -> None:
        self.__move(0, 1)

    def play_(self) -> None:
        if not self.__setup_blocks_playing():
            self.__switch_mode(initializing=False)

    def init_(self) -> None:
        if not self.__check_for_active_play():
            self.__switch_mode(initializing=True)

    def del_(self) -> None:
        if not self._initializing:
            self.__warn("Deleting a cell value can only be done while initializing the puzzle. ")
            return
        self.__selected_cell().set(None)

    def undo_(self) -> None:
        if self.__refused_while_initializing():
            return
        if self.__moves.is_empty():
            self.__warn_nothing_to_undo()
        else:
            self.select(self.__moves.undo())

    def rewind_(self) -> None:
        if self.__refused_while_initializing():
            return
        if self.__moves.is_empty():
            self.__warn_nothing_to_undo()
        elif self.__ui.confirm("Rewind cannot be undone.  Really rewind?"):
            self.select(self.__moves.rewind())

    def next_(self) -> None:
        """Point out the next move and why; the next "n" makes it"""
        if not self.__solving_refused():
            self.__inform(self.__solver.next())

    def auto_(self) -> None:
        """Make every obvious move, one after another, until the puzzle is complete, a guess is needed or something blocks solving"""
        if not self.__solving_refused():
            self.__inform(self.__solver.auto())

    def marks_(self) -> None:
        """Show the next kind of "must be" marks (Snyder notation), saying which"""
        if self.__refused_while_initializing():
            return
        self.__marks = self.__marks.next()
        self.__notice = Message(self.__marks.description(), MessageKind.INFO)

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
        self.__moves.enter(cell, value, CellAttrs.SOLVED)

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
        """Everything needed to restore the puzzle: layout, mode, marks setting, cursor, givens and recorded moves"""
        board = self.__board
        return SavedPuzzle(
            board.NAME, self._initializing, self.__marks, self.selected_cell, board.givens(), self.__moves.recorded()
        )

    def restore(self, saved) -> None:
        """Empty the board, enter the givens in setup mode, replay the moves in the saved mode, then point out any dead end"""
        self.__clear_board()
        for row, col, value in saved.givens:
            self.__moves.enter(self.__board.cell(row, col), value)
        self.__use_mode(saved.initializing)
        for row, col, value, prim_attr in saved.moves:
            self.__moves.enter(self.__board.cell(row, col), value, prim_attr)
        self.selected_cell = saved.selected_cell
        self.__marks = saved.marks
        self.render()
        self.__found_dead_end()

    # Private functions

    def __use_mode(self, initializing) -> None:
        """Enter setup or play mode, announcing it and the actions it offers to the user interface"""
        self._initializing = initializing
        mode = Mode.SETUP if initializing else Mode.PLAY
        self.__ui.mode_changed(mode, OFFERED_ACTIONS[mode])

    def __pending_hint(self) -> Message:
        """Return why the move "n" pointed out is right, or None if there is none"""
        hint = self.__solver.pending_hint()
        return Message(hint, MessageKind.HINT) if hint else None

    def __refresh_marks(self) -> None:
        """Have the cells show the marks of the setting while playing, and none in setup"""
        self.__board.refresh_marks(MarksSetting() if self._initializing else self.__marks)

    def __action_received(self, action) -> None:
        """Any action ends the notice and the completion report; any action but "n" cancels the move a previous "n" pointed out"""
        self.__notice = None
        self.__report.seen()
        if action is not Action.NEXT:
            self.__solver.cancel_pending_move()

    def __enter(self, val, prim_attr) -> None:
        """Enter the value in the selected cell, with its primary attribute, then point out any dead end"""
        cell = self.__selected_cell()
        if not self._initializing and CellAttrs.INITIAL in cell.attr():
            self.__warn("Cannot change an initial value while playing. ")
            return
        self.__moves.enter(cell, val, prim_attr)
        self.__found_dead_end()

    def __selected_cell(self) -> Cell:
        return self.__board.cell(*self.selected_cell)

    def __warn(self, text) -> None:
        self.__ui.inform(Message(text, MessageKind.WARNING))

    def __found_dead_end(self) -> bool:
        """Point out the first dead end, if any, moving to it without waiting; return whether there was one"""
        dead_end = DeadEndRule().find(self)
        if dead_end is None:
            return False
        self.select(dead_end.cell)
        text = self.__setup_dead_end_warning(dead_end) if self._initializing else dead_end.hint
        self.__notice = Message(text, MessageKind.WARNING, dead_end.missing())
        return True

    def __setup_dead_end_warning(self, dead_end) -> str:
        """Say why the setup leads to the dead end, and to change it"""
        if dead_end.house:
            reason = f"{dead_end.value} has no place left in this {dead_end.house.kind}"
        else:
            reason = "This square has no possible values left"
        return f"{reason} - change the setup before playing. "

    def __refused_while_initializing(self) -> bool:
        """Warn that a play command was used in setup mode, returning whether it was"""
        if self._initializing:
            self.__warn("This works only while playing - ESC starts playing. ")
        return self._initializing

    def __move(self, d_row, d_col) -> None:
        """Move the selected cell, stopping at the edges of the board"""
        row, col = self.selected_cell
        row = min(max(row + d_row, 0), self.__board.v_cells - 1)
        col = min(max(col + d_col, 0), self.__board.h_cells - 1)
        self.selected_cell = (row, col)

    def __setup_blocks_playing(self) -> bool:
        """Warn if the setup has conflicts, or a dead end (moving to it), which would block solving"""
        if self.__board.has_conflicts():
            self.__warn("Resolve the conflicts before playing. ")
            return True
        return self.__found_dead_end()

    def __switch_mode(self, initializing) -> None:
        self.__use_mode(initializing)
        self.display_status()

    def __check_for_active_play(self) -> bool:
        is_actively_playing = not self.__moves.is_empty()
        if is_actively_playing:
            self.__warn("Cannot initialize puzzle while playing - undo everything first. ")
        return is_actively_playing

    def __warn_nothing_to_undo(self) -> None:
        self.__warn("Cannot undo initialized puzzle.  ESC will re-enter initialization mode. ")

    def __solving_refused(self) -> bool:
        """Warn, returning True, if "n" or "a" cannot solve: in setup mode, or once the puzzle is complete"""
        if self.__refused_while_initializing():
            return True
        is_complete = self.is_complete()
        if is_complete:
            self.__ui.inform(self.__report.already_complete())
        return is_complete

    def __inform(self, message) -> None:
        """Show the message, if there is one, until the player has seen it"""
        if message:
            self.__ui.inform(message)

    def __clear_board(self) -> None:
        """Empty every cell and forget the moves and the last completion report, back in setup mode"""
        self.__board.clear()
        self.__moves.clear()
        self.__report.reset()
        self._initializing = True
