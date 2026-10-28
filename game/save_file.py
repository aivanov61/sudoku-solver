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
import os

from dataclasses import asdict, dataclass, fields

from game.settings import Settings


@dataclass
class SavedPuzzle:
    """Everything needed to restore a puzzle: the settings, the tags, the givens, then the moves made while playing"""

    layout: str  # the layout's NAME
    initializing: bool
    settings: Settings  # what the player configured, such as the "must be" marks
    selected_cell: tuple  # (row, col)
    tags: list  # (row, col) for each tagged cell
    givens: list  # (row, col, value) for each given
    moves: list  # (row, col, value, prim_attr) for each entry in the history, oldest first
    ignored: tuple = ()  # the entries in the file, from a newer version, that this one doesn't know; never saved


class SaveFileError(Exception):
    """A save file that cannot be read; the message tells the player why"""


class SaveFile:
    """
    Writes a SavedPuzzle to a JSON file, stamped with the file format's version, and reads it back.

    When the format changes, raise VERSION and add an entry to UPGRADES that turns the state saved by
    the previous version into the new one, so files saved by older programs can still be read.  Adding a setting
    needs neither: a setting missing from the file is read as its default (see Settings), and an older program
    reads the file without the entries it doesn't know, naming each by its path in SavedPuzzle.ignored.

    A file name without a folder means a file in FOLDER, which is created when needed.  Save files end in
    EXTENSION; the player is asked for a name without it.
    """

    FORMAT = "sudoku-save"
    VERSION = 1
    UPGRADES = {}  # version: function returning that version's state converted to the next version
    FOLDER = "saved_games"
    EXTENSION = ".json"

    def located(name) -> str:
        """Return the path for a file name: in FOLDER unless the name includes a folder of its own"""
        return name if os.path.dirname(name) else os.path.join(SaveFile.FOLDER, name)

    def write(path, saved: SavedPuzzle) -> None:
        if os.path.dirname(path) == SaveFile.FOLDER:
            os.makedirs(SaveFile.FOLDER, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            state = {**asdict(saved), "settings": saved.settings.saved()}
            del state["ignored"]
            json.dump({"format": SaveFile.FORMAT, "version": SaveFile.VERSION, "state": state}, file, indent=1)

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
        return SaveFile.__saved_puzzle(path, {**data, "state": state})

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

    def __saved_puzzle(path, data) -> SavedPuzzle:
        """Turn the file's saved state back into a SavedPuzzle, with tuples where JSON stored lists"""
        state = data["state"]
        try:
            return SavedPuzzle(
                layout=state["layout"],
                initializing=state["initializing"],
                settings=Settings.from_saved(state.get("settings", {})),
                selected_cell=tuple(state["selected_cell"]),
                tags=[tuple(tag) for tag in state.get("tags", [])],
                givens=[tuple(given) for given in state["givens"]],
                moves=[tuple(move) for move in state["moves"]],
                ignored=SaveFile.__unknown(data, SaveFile.__known_file()),
            )
        except (KeyError, TypeError, ValueError):
            raise SaveFile.__damaged(path)

    def __unknown(saved, known, path="") -> tuple:
        """
        Return the path (names joined by dots) of each entry saved that isn't among the known ones, walking into
        the entries that both hold as dictionaries
        """
        unknown = ()
        for name, value in saved.items():
            if name not in known:
                unknown += (path + name,)
            elif isinstance(value, dict) and isinstance(known[name], dict):
                unknown += SaveFile.__unknown(value, known[name], f"{path}{name}.")
        return unknown

    def __known_file() -> dict:
        """Return the entries this version writes to a file, with every setting as saved by default"""
        state = {**{field.name: None for field in fields(SavedPuzzle)}, "settings": Settings().saved()}
        return {"format": None, "version": None, "state": state}
