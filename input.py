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

from commands import Commands
from display import Display


class Input:
    """
    Get input from the terminal and/or other connected input devices and decode it
    """

    def get_cmd(timeout=None):
        cmd = None
        while not cmd:
            try:
                with Display.term.cbreak():
                    cmd = Input.__decode_inkey(Display.term.inkey(timeout=timeout))
            except Exception as e:  # Any exception just quit
                return "quit"
            except:  # Everything else that is bad, including CTRL-C (KeyboardInterrupt), just quit
                return "quit"
        return cmd

    def __decode_inkey(keystroke):
        if keystroke == "":
            return "timeout"
        cmd_name = keystroke.name if keystroke.is_sequence else keystroke
        matching_cmds = [k for k in Commands.CMDS.keys() if cmd_name in Commands.CMDS[k]["keys"]]
        cmd = next(iter(matching_cmds), None)
        cmd = cmd_name if cmd == "#" else cmd
        return cmd
