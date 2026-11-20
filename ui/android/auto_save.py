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

import os

from game.game_file import GameFile
from game.puzzle import Puzzle
from game.save_file import SavedPuzzle, SaveFile, SaveFileError
from game.user_interface import Message, MessageKind, UserInterface


class AutoSave:
    """
    The game in progress, kept in one save file in the app's own storage, so that it survives the app being stopped
    and Android ending it: the app has it saved whenever it is stopped, the game is restored from it when it starts,
    and it is deleted once the game is over.  It is an ordinary save file, so the PC can read it.

    The file is the game's own once the game has restored it or written it.  A file the game couldn't restore is
    left alone: it is overwritten only once the player has something to save, and never deleted, so the player can
    still install a newer version to restore it, or copy it off the phone.
    """

    def __init__(self, path: str, ui: UserInterface) -> None:
        self.__path = path
        self.__ui = ui
        self.__is_own = False  # the file holds this game, restored or saved, so it may be replaced or deleted

    # Interface required for the app, before a game is started

    @staticmethod
    def saved_layout(path: str) -> str | None:
        """Return the layout of the game saved in the file, or None when there is no file or it can't be read"""
        try:
            return SaveFile.read(path).layout
        except SaveFileError:
            return None

    # Interface required for the user interface

    def restore(self, game: Puzzle) -> None:
        """Restore the game saved in the file, if there is one; warn when it can't be, leaving the game new"""
        if not os.path.exists(self.__path):
            return
        saved = self.__read(game)
        if saved is None:
            return
        game.restore(saved)
        self.__is_own = True
        if saved.ignored:
            self.__ui.inform(GameFile.ignored_warning(saved.ignored))

    def save(self, game: Puzzle) -> None:
        """Write the game to the file when its board has values; with none, delete the game saved before"""
        if game.has_values():
            self.__write(game)
        else:
            self.forget()

    def forget(self) -> None:
        """Delete the file, once the game is over, when it holds this game"""
        if self.__is_own:
            os.remove(self.__path)
            self.__is_own = False

    # Private functions

    def __read(self, game: Puzzle) -> SavedPuzzle | None:
        """Return the game saved in the file, or None after warning why it can't be restored into this game"""
        try:
            saved = SaveFile.read(self.__path)
        except SaveFileError as error:
            self.__warn(f"{error}A new puzzle is started. ")
            return None
        if saved.layout != game.layout_name():
            self.__warn(f'The saved game is a "{saved.layout}" puzzle, so a new puzzle is started. ')
            return None
        return saved

    def __write(self, game: Puzzle) -> None:
        try:
            SaveFile.write(self.__path, game.saved_state())
        except OSError as error:
            self.__warn(f"Cannot save the game: {error.strerror}. ")
            return
        self.__is_own = True

    def __warn(self, text: str) -> None:
        self.__ui.inform(Message(text, MessageKind.WARNING))
