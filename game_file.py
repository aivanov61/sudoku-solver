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

sys.path.insert(0, ".")

from display import Display
from save_file import SavedPuzzle, SaveFile, SaveFileError


class GameFile:
    """
    Save the puzzle to a file, or restore one saved before, asking the player for the file name.

    SaveFile writes and reads the file itself.  The puzzle provides layout_name(), has_values(),
    saved_state() and restore(saved).
    """

    DEFAULT_FILE_NAME = "sudoku.json"

    def __init__(self, puzzle):
        self.__puzzle = puzzle
        self.__file_name = self.DEFAULT_FILE_NAME  # the file name last saved or restored, as typed

    # Interface required for the puzzle

    def save(self) -> None:
        if not self.__puzzle.has_values():
            Display.warn("Nothing to save - the board is empty. ", wait=True)
            return
        name = Display.ask("Save to file:", self.__file_name)
        path = name and SaveFile.located(name)
        if not path or os.path.exists(path) and not Display.confirm(f"{path} already exists.  Replace it?"):
            return
        try:
            SaveFile.write(path, self.__puzzle.saved_state())
        except OSError as error:
            Display.warn(f"Cannot save to {path}: {error.strerror}. ", wait=True)
            return
        self.__file_name = name
        Display.warn(f"Saved to {path}. ", wait=True)

    def restore(self) -> None:
        """Replace the puzzle with one saved to a file, asking first if that would lose any values"""
        name = Display.ask("Restore from file:", self.__file_name)
        saved = name and self.__read(SaveFile.located(name))
        if not saved or self.__puzzle.has_values() and not Display.confirm("Restoring replaces every value.  Really restore?"):
            return
        self.__file_name = name
        self.__puzzle.restore(saved)

    # Private functions

    def __read(self, path) -> SavedPuzzle:
        """Return the puzzle saved in the file, or None after warning why it cannot be restored here"""
        try:
            saved = SaveFile.read(path)
        except SaveFileError as error:
            Display.warn(str(error), wait=True)
            return None
        if saved.layout != self.__puzzle.layout_name():
            Display.warn(f'{path} holds a "{saved.layout}" puzzle - rerun and choose that layout. ', wait=True)
            return None
        return saved
