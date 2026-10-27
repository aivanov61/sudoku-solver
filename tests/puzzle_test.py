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
from unittest import main, TestCase

sys.path.insert(0, ".")

from commands import Commands
from puzzle import Puzzle


class TestPuzzle(TestCase):
    def test_puzzle_has_a_method_for_every_command(self):
        all_commands = {**Commands.COMMON_CMDS, **Commands.INIT_COMMANDS, **Commands.PLAY_COMMANDS}
        missing = [command for command in all_commands if not hasattr(Puzzle, self.__method_name(command))]
        self.assertEqual(missing, [])

    # Private functions

    def __method_name(self, command) -> str:
        """Return the puzzle method for a command; digits ("#") are entered through value_()"""
        return "value_" if command == "#" else f"{command}_"


if __name__ == "__main__":
    main()
