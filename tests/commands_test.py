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
        self.assertEqual(list(Commands.CMDS), list(Commands.PLAY_COMMANDS) + list(Commands.COMMON_CMDS))

    def test_initialization_commands_can_be_made_active_again(self):
        Commands.use(Commands.PLAY_COMMANDS)
        Commands.use(Commands.INIT_COMMANDS)
        self.assertEqual(list(Commands.CMDS), list(Commands.INIT_COMMANDS) + list(Commands.COMMON_CMDS))

    def test_save_and_open_are_available_in_both_modes(self):
        for mode_cmds in (Commands.INIT_COMMANDS, Commands.PLAY_COMMANDS):
            Commands.use(mode_cmds)
            self.assertIn("s", Commands.CMDS["save"]["keys"])
            self.assertIn("o", Commands.CMDS["open"]["keys"])

    def test_panel_lists_the_mode_commands_first_then_the_common_ones(self):
        Commands.use(Commands.PLAY_COMMANDS)
        panel = Commands.panel()
        self.assertEqual(panel[2:4], [("1-9", "value"), ("shift 1-9", "guess")])
        self.assertIn(("u", "undo"), panel)
        self.assertEqual(panel[-1], ("q CTRL-C", "quit"))

    def test_panel_in_setup_mode_has_no_guess_and_offers_play(self):
        Commands.use(Commands.INIT_COMMANDS)
        panel = Commands.panel()
        self.assertNotIn(("shift 1-9", "guess"), panel)
        self.assertIn(("ESC", "PLAY"), panel)

    def test_esc_then_help_head_the_panel_in_both_modes(self):
        for mode_cmds, name in ((Commands.INIT_COMMANDS, "PLAY"), (Commands.PLAY_COMMANDS, "SETUP")):
            Commands.use(mode_cmds)
            self.assertEqual(Commands.panel()[:2], [("ESC", name), ("?", "help")])

    def test_moves_come_right_after_the_values_in_both_modes(self):
        for mode_cmds in (Commands.INIT_COMMANDS, Commands.PLAY_COMMANDS):
            Commands.use(mode_cmds)
            keys = [keys for keys, name in Commands.panel()]
            last_value = max(i for i, key in enumerate(keys) if "1-9" in key)
            self.assertEqual(keys[last_value + 1 : last_value + 5], ["k ↑", "j ↓", "h ←", "l →"])

    def test_play_commands_are_hidden_in_setup_mode(self):
        Commands.use(Commands.INIT_COMMANDS)
        for name in ("undo", "rewind", "auto", "next"):
            self.assertEqual(Commands.CMDS[name]["panel"], [])
        self.assertIn("[hidden]", Commands.long_help())

    def test_commands_without_panel_lines_are_left_out(self):
        Commands.use(Commands.PLAY_COMMANDS)
        self.assertNotIn("Del", [keys for keys, name in Commands.panel()])


if __name__ == "__main__":
    main()
