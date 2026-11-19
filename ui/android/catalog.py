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

from game.board import Board
from game.puzzle_catalog import PuzzleCatalog


class Catalog:
    """
    The puzzle layouts as the Android app sees them, in plain values: it plays the part Main plays for the terminal,
    listing the layouts to choose from and making the board of the one chosen.
    """

    @staticmethod
    def layouts() -> list[tuple[str, str, bool]]:
        """Return (name, label, whether it can be picked) for every layout, sorted by name; the label adds any notes"""
        return [(layout.name, layout.label(), not layout.is_broken()) for layout in PuzzleCatalog.available()]

    @staticmethod
    def board(name: str) -> Board:
        """Return a new board of the layout with the name, which must be one that can be picked"""
        layout = next((layout for layout in PuzzleCatalog.available() if layout.name == name), None)
        if layout is None:
            raise KeyError(f"no puzzle layout is named {name!r}")
        return layout.board()
