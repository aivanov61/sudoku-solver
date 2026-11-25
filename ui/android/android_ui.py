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

from collections.abc import Callable
from queue import Queue

from game.actions import Action, Mode
from game.border import Border
from game.cell import Cell
from game.cell_attrs import CellAttrs
from game.config_option import ConfigOption
from game.puzzle import Puzzle
from game.user_interface import Message, MessageKind, Step
from ui.android.auto_save import AutoSave
from ui.android.screen import Screen
from ui.error_log import ErrorLog


class AndroidUI:
    """
    The user interface on Android: the game's side of the app.  The game runs on its own thread in play(), taking
    requests from a queue that the screen (see Screen) fills: the player's actions through act(), and saves through
    save(), so a save never lands in the middle of an action.  Everything the game shows is passed on to the screen
    as plain values.  A question, or a message the player must see, blocks the game's thread until the screen gives
    the player's answer through answer(); the screen's own thread never waits.

    The game is auto-saved to the file given (see AutoSave): restored from it when play starts, and saved to it when
    the app asks.

    For now, while the app is a first try: saving to a file the player names, restoring one, configuring and walking
    through steps are not offered.
    """

    def __init__(self, screen: Screen, auto_save_path: str) -> None:
        self.__screen = screen
        self.__auto_save = AutoSave(auto_save_path, self)
        self.__requests: Queue[Callable[[Puzzle], None]] = Queue()  # each carried out on the game, in turn
        self.__answers: Queue[bool] = Queue()

    # Interface required for the screen

    def play(self, game: Puzzle) -> None:
        """
        Show the game, restored from the auto-save if there is one, then carry out each request, showing the selected
        cell after each, until the game is over, and then forget the auto-save; runs on the game's thread
        """
        game.render()
        self.__auto_save.restore(game)
        self.__screen.showSelected(*game.selected_cell)
        while game.is_playing:
            self.__requests.get()(game)
            self.__screen.showSelected(*game.selected_cell)
        self.__auto_save.forget()
        self.__screen.gameOver()

    def act(self, name: str, digit: int | None = None, row: int | None = None, col: int | None = None) -> None:
        """Pass the player's action on to the game: its name (an Action's value), with its digit or the cell it points at"""
        action = Action(name)
        position = None if row is None or col is None else (row, col)
        self.__requests.put(lambda game: self.__carry_out(game, action, digit, position))

    def save(self) -> None:
        """Have the game auto-saved, once the requests before it are carried out"""
        self.__requests.put(self.__auto_save.save)

    def answer(self, yes: bool) -> None:
        """Give the game the player's answer to the question it is waiting on"""
        self.__answers.put(yes)

    # Interface required for the game

    def status(self, message: Message | None) -> None:
        if message:
            self.__screen.showStatus(message.text, message.kind.value)
        else:
            self.__screen.showStatus("", "")

    def inform(self, message: Message) -> None:
        """Have the screen show the message, wait until the player has seen it, then tell the screen it is over"""
        self.__screen.showInform(message.text, message.kind.value)
        self.__wait_for_answer()

    def confirm(self, question: str) -> bool:
        """Have the screen ask the question, wait for the player's answer, then tell the screen the question is over"""
        self.__screen.askConfirm(question)
        return self.__wait_for_answer()

    def ask_file_name(self, prompt: str, default: str, extension: str) -> str | None:
        """Cancel, as saving and restoring are not offered yet"""
        return None

    def configure(self, options: list[ConfigOption]) -> list[ConfigOption]:
        """Leave the options as they are, as configuring is not offered yet"""
        return options

    def walk_through(self, steps: list[Step]) -> None:
        """Show nothing, as walking through steps is not offered yet"""

    def guess_depth_changed(self, depth: int) -> None:
        """Show nothing more: each cell comes with the guess depth it was entered at"""

    def show_board(self, cells: list[Cell]) -> None:
        for cell in cells:
            self.cell_changed(cell)

    def cell_changed(self, cell: Cell) -> None:
        attrs = cell.attr()
        kind = next((attr for attr in attrs if attr in CellAttrs.PRIMARY), "")
        conflicted = any(attr in CellAttrs.CONFLICT_ATTRS for attr in attrs)
        depth = next((attr["depth"] for attr in attrs if isinstance(attr, dict)), 0)
        possible = sorted(cell.shown_possible())
        self.__screen.showCell(cell.row, cell.col, cell.value() or 0, kind, conflicted, depth, possible, self.__edges(cell.borders))

    def mode_changed(self, mode: Mode, actions: tuple[Action, ...]) -> None:
        self.__screen.modeChanged(mode.value, [action.value for action in actions])

    # Private functions

    def __carry_out(self, game: Puzzle, action: Action, digit: int | None, position: tuple[int, int] | None) -> None:
        """Hand the action to the game, surviving an action that breaks: say so, and stop the game if it was a quit"""
        try:
            game.handle(action, digit, position)
        except Exception as error:
            self.inform(Message(ErrorLog.report_broken(action.value, error), MessageKind.WARNING))
            if action in (Action.QUIT, Action.FORCE_QUIT):
                game.force_quit_()

    def __wait_for_answer(self) -> bool:
        """Wait for the player's answer to what the screen shows, then tell the screen it has been answered"""
        yes = self.__answers.get()
        self.__screen.questionAnswered()
        return yes

    @staticmethod
    def __edges(borders: Border) -> list[str]:
        """The names of the cell's sides that are block edges"""
        sides = ((Border.TOP, borders.is_top()), (Border.LEFT, borders.is_left()), (Border.RIGHT, borders.is_right()), (Border.BOTTOM, borders.is_bottom()))
        return [name for name, is_edge in sides if is_edge]
