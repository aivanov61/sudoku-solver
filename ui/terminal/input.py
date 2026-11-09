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

from game.actions import Action
from ui.terminal.commands import Commands
from ui.terminal.display import Display


class Input:
    """
    Get keys from the display's terminal and decode them into commands (see Commands)
    """

    def __init__(self, display: Display):
        self.__display = display

    def get_cmd(self, offered, timeout=None) -> tuple:
        """Return (command, digit) for the next bound key, given the actions the mode offers; None after a timeout"""
        while True:
            try:
                key = self.__read_key(timeout)
            except (KeyboardInterrupt, Exception):  # CTRL-C, or anything wrong with the terminal, quits without asking
                return Action.FORCE_QUIT, None
            if key == "":
                return None
            command = Commands.command_for(key, offered)
            if command:
                return command

    def get_key_of(self, keys) -> str:
        """Return the next key that is one of the keys; None after CTRL-C or anything wrong with the terminal"""
        while True:
            try:
                key = self.__read_key()
            except (KeyboardInterrupt, Exception):
                return None
            if key in keys:
                return key

    # Private functions

    def __read_key(self, timeout=None) -> str:
        """Return the key pressed: its name (e.g. KEY_ENTER) for special keys, else the character; "" after a timeout"""
        term = self.__display.term
        with term.cbreak():
            keystroke = term.inkey(timeout=timeout)
        return keystroke.name if keystroke.is_sequence else str(keystroke)
