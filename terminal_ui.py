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

from display import Display, echo
from display_attrs import DisplayAttrs
from user_interface import MessageKind


class TerminalUI:
    """
    The user interface on a terminal: it shows the game's messages and asks its questions on the status line.
    """

    # Interface required for the game

    def status(self, message) -> None:
        Display.move_to_status_line()
        echo((self.__styled(message) if message else "") + Display.term.clear_eol)

    def inform(self, message) -> None:
        Display.show_on_status_line(self.__styled(message), wait=True)

    def confirm(self, question) -> bool:
        return Display.confirm(question)

    def ask_file_name(self, prompt, default) -> str:
        return Display.ask(prompt, default)

    # Private functions

    def __styled(self, message) -> str:
        """Successes and hints in the solved style (steel blue), everything else in yellow"""
        if message.kind in (MessageKind.SUCCESS, MessageKind.HINT):
            return Display.styled(message.text, (DisplayAttrs.SOLVED,))
        return Display.term.yellow(message.text)
