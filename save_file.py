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

import json

from dataclasses import asdict, dataclass


@dataclass
class SavedPuzzle:
    """Everything needed to restore a puzzle: the givens, then the moves made while playing, in order"""

    layout: str  # the layout's NAME
    initializing: bool
    selected_cell: tuple  # (row, col)
    givens: list  # (row, col, value) for each given
    moves: list  # (row, col, value, prim_attr) for each entry in the history, oldest first


class SaveFileError(Exception):
    """A save file that cannot be read; the message tells the player why"""


class SaveFile:
    """
    Writes a SavedPuzzle to a JSON file, stamped with the file format's version, and reads it back.

    When the format changes, raise VERSION and add an entry to UPGRADES that turns the state saved by
    the previous version into the new one, so files saved by older programs can still be read.
    """

    FORMAT = "sudoku-save"
    VERSION = 1
    UPGRADES = {}  # version: function returning that version's state converted to the next version

    def write(path, saved: SavedPuzzle) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump({"format": SaveFile.FORMAT, "version": SaveFile.VERSION, "state": asdict(saved)}, file, indent=1)

    def read(path) -> SavedPuzzle:
        """Return the puzzle saved in the file, upgraded to the current version; raise SaveFileError if it can't be"""
        data = SaveFile.__load(path)
        if data["version"] > SaveFile.VERSION:
            raise SaveFileError(
                f"{path} is from a newer version - update sudoku to restore this file. "
            )
        state = data["state"]
        for version in range(data["version"], SaveFile.VERSION):
            state = SaveFile.UPGRADES[version](state)
        return SaveFile.__saved_puzzle(path, state)

    # Private functions

    def __load(path) -> dict:
        try:
            with open(path, encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise SaveFileError(f"Cannot find {path}. ")
        except (OSError, ValueError):
            raise SaveFile.__damaged(path)
        is_save_file = isinstance(data, dict) and data.get("format") == SaveFile.FORMAT
        if not is_save_file or not isinstance(data.get("version"), int) or "state" not in data:
            raise SaveFile.__damaged(path)
        return data

    def __damaged(path) -> SaveFileError:
        return SaveFileError(f"Cannot restore {path} - it is not a saved puzzle, or it is damaged. ")

    def __saved_puzzle(path, state) -> SavedPuzzle:
        """Turn the saved state back into a SavedPuzzle, with tuples where JSON stored lists"""
        try:
            return SavedPuzzle(
                layout=state["layout"],
                initializing=state["initializing"],
                selected_cell=tuple(state["selected_cell"]),
                givens=[tuple(given) for given in state["givens"]],
                moves=[tuple(move) for move in state["moves"]],
            )
        except (KeyError, TypeError):
            raise SaveFile.__damaged(path)
