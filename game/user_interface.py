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

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class MessageKind(Enum):
    """What a message is for, so that each user interface can show it in its own way"""

    INFO = "info"  # something the player may want to know, e.g. where a game was saved
    WARNING = "warning"  # something refused, blocked or wrong
    SUCCESS = "success"  # the puzzle is solved
    HINT = "hint"  # why the move "n" pointed out is right


@dataclass(frozen=True)
class Highlight:
    """What a message points at on the board: a house, the digits to show where they can still go, and where they can't"""

    house: object  # the House
    cells: dict  # {cell: digits} where the digits can still go, as far as it explains the message
    gone: dict  # {cell: digits} where the message rules them out, and the empty cells of its house they can't go in


@dataclass(frozen=True)
class Message:
    text: str
    kind: MessageKind
    missing: tuple = None  # (cell, value): a value with no place left, shown in the cell while the message is
    short: str = None  # a shorter text, shown instead when the whole text doesn't fit
    highlight: Highlight = None  # what the message points at, shown on the board while the message is


@dataclass(frozen=True)
class Step:
    """One step of an explanation the player walks through: the message, and the cell it is about"""

    cell: object
    message: Message


class UserInterface(Protocol):
    """
    The port through which the game talks to the player.  Each way of showing the game (today the
    terminal, TerminalUI) is an adapter implementing it, so the game never depends on how it is shown.

    Dialogs are synchronous: they return the player's answer.
    """

    def status(self, message) -> None:
        """Show the message (and its missing value, if any) until the next command; None leaves the status line blank"""

    def inform(self, message) -> None:
        """Show the message (and its missing value, if any) and wait until the player has seen it"""

    def confirm(self, question) -> bool:
        """Ask a yes/no question, returning True only for yes"""

    def ask_file_name(self, prompt, default, extension) -> str:
        """Ask for a file name, offering the default; the player doesn't type the extension, which is added to the
        name returned; return None if the player cancels"""

    def configure(self, options) -> list:
        """Let the player change the options (see ConfigOption), returning them as chosen; the game then shows the
        board afresh"""

    def walk_through(self, steps) -> None:
        """Let the player go back and forth through the steps (see Step), each shown with its cell, until done"""

    def guess_depth_changed(self, depth) -> None:
        """Hear that values are now entered depth guesses deep (0 when no guess is in play)"""

    def show_board(self, cells) -> None:
        """Show the whole board afresh: every cell, with its block edges (cell.borders)"""

    def cell_changed(self, cell) -> None:
        """Hear that the cell's value, attributes or possible values changed, to show it as it is now"""

    def mode_changed(self, mode, actions) -> None:
        """Hear that the puzzle is now in the mode (see actions.py), which offers these actions"""
