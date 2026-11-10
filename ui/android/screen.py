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

from typing import Protocol


class Screen(Protocol):
    """
    The app's screen, written in Kotlin (PythonScreen in android/), as AndroidUI sees it.  Its names are Kotlin's.

    It is called on the game's thread, and takes only plain values (lists arrive as Kotlin arrays), so it
    never holds on to the game's objects; it turns each call into a typed event for the app's view model.
    """

    def showCell(self, row: int, col: int, value: int, kind: str, conflicted: bool, depth: int, possible: list[int], edges: list[str]) -> None:
        """
        Show the cell as it is now: its value (0 for none), how the value got there (a CellAttrs primary attribute,
        "" for a typed value or none), whether it is in conflict, the guess depth it was entered at (0 for none),
        the possible values it shows, and which of its sides are block edges (Border's names)
        """
        ...

    def showSelected(self, row: int, col: int) -> None:
        """Show which cell is selected: the one values go into"""
        ...

    def showStatus(self, text: str, kind: str) -> None:
        """Show the text, of the MessageKind's value, on the status line; "" for both blanks it"""
        ...

    def askConfirm(self, question: str) -> None:
        """Ask the yes/no question, and give the answer to AndroidUI.answer()"""
        ...

    def modeChanged(self, mode: str, actions: list[str]) -> None:
        """Hear that the puzzle is now in the mode (a Mode's value), which offers these actions (Action values)"""
        ...

    def gameOver(self) -> None:
        """Hear that the game is over, so the app can close"""
        ...
