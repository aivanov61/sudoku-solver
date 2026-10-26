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


class TestCommands(TestCase):
    def setUp(self):
        self.saved_cmds = Commands.CMDS
        return super().setUp()

    def tearDown(self):
        Commands.CMDS = self.saved_cmds
        return super().tearDown()

    def test_play_commands_can_be_made_active(self):
        Commands.use(Commands.PLAY_COMMANDS)
        self.assertEqual(list(Commands.CMDS), list(Commands.COMMON_CMDS) + list(Commands.PLAY_COMMANDS))

    def test_initialization_commands_can_be_made_active_again(self):
        Commands.use(Commands.PLAY_COMMANDS)
        Commands.use(Commands.INIT_COMMANDS)
        self.assertEqual(list(Commands.CMDS), list(Commands.COMMON_CMDS) + list(Commands.INIT_COMMANDS))


if __name__ == "__main__":
    main()
