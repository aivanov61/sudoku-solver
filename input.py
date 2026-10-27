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

from actions import Action
from commands import Commands
from display import Display


class Input:
    """
    Get keys from the terminal and decode them into commands (see Commands)
    """

    def get_cmd(offered, timeout=None) -> tuple:
        """Return (command, digit) for the next bound key, given the actions the mode offers; None after a timeout"""
        while True:
            try:
                with Display.term.cbreak():
                    keystroke = Display.term.inkey(timeout=timeout)
            except:  # Anything bad, including CTRL-C (KeyboardInterrupt), quits without asking
                return Action.FORCE_QUIT, None
            if keystroke == "":
                return None
            command = Commands.command_for(keystroke.name if keystroke.is_sequence else str(keystroke), offered)
            if command:
                return command
