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
import sys

from typing import TYPE_CHECKING

sys.path.insert(0, ".")

from game.save_file import SavedPuzzle, SaveFile, SaveFileError
from game.user_interface import Message, MessageKind, UserInterface

if TYPE_CHECKING:
    from game.puzzle import Puzzle


class GameFile:
    """
    Save the puzzle to a file, or restore one saved before, asking the player for the file name.

    SaveFile writes and reads the file itself.  The puzzle provides layout_name(), has_values(),
    saved_state() and restore(saved); the user interface asks the player and shows the outcome.
    """

    DEFAULT_FILE_NAME = "sudoku"

    def __init__(self, puzzle: "Puzzle", ui: UserInterface):
        self.__puzzle = puzzle
        self.__ui = ui
        self.__file_name = self.DEFAULT_FILE_NAME  # the file name last saved or restored, as typed, without its extension

    # Interface required for the puzzle

    def save(self) -> None:
        if not self.__puzzle.has_values():
            self.__warn("Nothing to save - the board is empty. ")
            return
        name = self.__ui.ask_file_name("Save to file:", self.__file_name, SaveFile.EXTENSION)
        path = name and SaveFile.located(name)
        if not path or os.path.exists(path) and not self.__ui.confirm(f"{path} already exists.  Replace it?"):
            return
        try:
            SaveFile.write(path, self.__puzzle.saved_state())
        except OSError as error:
            self.__warn(f"Cannot save to {path}: {error.strerror}. ")
            return
        self.__remember(name)
        self.__ui.inform(Message(f"Saved to {path}. ", MessageKind.INFO))

    def restore(self) -> None:
        """Replace the puzzle with one saved to a file, asking first if that would lose any values"""
        name = self.__ui.ask_file_name("Restore from file:", self.__file_name, SaveFile.EXTENSION)
        saved = name and self.__read(SaveFile.located(name))
        if not saved or self.__puzzle.has_values() and not self.__ui.confirm("Restoring replaces every value.  Really restore?"):
            return
        self.__remember(name)
        self.__puzzle.restore(saved)
        if saved.ignored:
            self.__warn_ignored(saved.ignored)

    # Private functions

    def __warn(self, text) -> None:
        self.__ui.inform(Message(text, MessageKind.WARNING))

    def __warn_ignored(self, ignored) -> None:
        """Name the entries ignored, or only count them where the names don't fit"""
        entries = "entry" if len(ignored) == 1 else "entries"
        text = f"Ignored {entries} from a newer sudoku: {', '.join(ignored)}. "
        short = f"Ignored {len(ignored)} {entries} from a newer sudoku. "
        self.__ui.inform(Message(text, MessageKind.WARNING, short=short))

    def __remember(self, name) -> None:
        """Offer the name next time, without its extension"""
        self.__file_name = name.removesuffix(SaveFile.EXTENSION)

    def __read(self, path) -> SavedPuzzle:
        """Return the puzzle saved in the file, or None after warning why it cannot be restored here"""
        try:
            saved = SaveFile.read(path)
        except SaveFileError as error:
            self.__warn(str(error))
            return None
        if saved.layout != self.__puzzle.layout_name():
            self.__warn(f'{path} holds a "{saved.layout}" puzzle - rerun and choose that layout. ')
            return None
        return saved
