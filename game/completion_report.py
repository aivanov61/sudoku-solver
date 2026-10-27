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

from game.user_interface import Message, MessageKind


class CompletionReport:
    """
    Tell the player once when the puzzle becomes complete - solved, or with errors - and again whenever that changes.

    The puzzle provides is_complete() and has_conflicts().
    """

    def __init__(self, puzzle):
        self.__puzzle = puzzle
        self.__reported = None  # the completion last reported
        self.__unseen = None  # a reported completion the player has not yet answered with a command

    # Interface required for the puzzle

    def message(self) -> Message:
        """Return the status line message for a newly changed completion until it is seen, otherwise None"""
        completion = self.__completion()
        if completion != self.__reported:
            self.__reported = completion
            self.__unseen = completion
        return {
            None: None,
            "solved": Message("The puzzle is solved. ", MessageKind.SUCCESS),
            "errors": Message("Complete, with errors - undo or change values to fix them. ", MessageKind.WARNING),
        }[self.__unseen]

    def seen(self) -> None:
        self.__unseen = None

    def reset(self) -> None:
        """Forget the last report, so the next completion is reported even if it is unchanged"""
        self.__reported = None

    def already_complete(self) -> Message:
        """Return the warning that the puzzle is already complete, solved or with errors"""
        return Message(
            "The puzzle is already complete, with errors - undo or change values to fix them. "
            if self.__puzzle.has_conflicts()
            else "The puzzle is already solved. ",
            MessageKind.WARNING,
        )

    # Private functions

    def __completion(self) -> str:
        """None until the puzzle is complete, then 'solved' or 'errors'"""
        if not self.__puzzle.is_complete():
            return None
        return "errors" if self.__puzzle.has_conflicts() else "solved"
