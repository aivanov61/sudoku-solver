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

from game.actions import Action, Mode, OFFERED_ACTIONS
from ui.terminal.commands import Commands

SETUP = OFFERED_ACTIONS[Mode.SETUP]
PLAY = OFFERED_ACTIONS[Mode.PLAY]


class TestCommands(TestCase):
    # The command panel

    def test_panel_in_play_mode(self):
        self.assertEqual(
            Commands.panel(PLAY),
            [
                ("ESC", "SETUP"), ("?", "help"), ("1-9", "value"), ("shift 1-9", "guess"),
                ("k ↑", "up"), ("j ↓", "down"), ("h ←", "left"), ("l →", "right"),
                ("u", "undo"), ("r", "rewind"), ("a", "auto"), ("n", "next"), ("c", "config"),
                ("s", "save"), ("o", "open"), ("q CTRL-C", "quit"),
            ],
        )

    def test_panel_in_setup_mode(self):
        self.assertEqual(
            Commands.panel(SETUP),
            [
                ("ESC", "PLAY"), ("?", "help"), ("1-9", "value"),
                ("k ↑", "up"), ("j ↓", "down"), ("h ←", "left"), ("l →", "right"),
                ("Del", "clear"), ("c", "config"), ("s", "save"), ("o", "open"), ("q CTRL-C", "quit"),
            ],
        )

    # Keys

    def test_esc_starts_playing_in_setup_and_goes_back_to_setup_while_playing(self):
        self.assertEqual(Commands.command_for("KEY_ESCAPE", SETUP), (Action.PLAY, None))
        self.assertEqual(Commands.command_for("KEY_ESCAPE", PLAY), (Action.INIT, None))

    def test_digits_are_values_and_shifted_digits_are_guesses(self):
        for offered in (SETUP, PLAY):
            self.assertEqual(Commands.command_for("5", offered), (Action.VALUE, 5))
            self.assertEqual(Commands.command_for("%", offered), (Action.GUESS, 5))

    def test_a_key_maps_to_its_action_even_where_the_mode_does_not_offer_it(self):
        self.assertEqual(Commands.command_for("u", SETUP), (Action.UNDO, None))
        self.assertEqual(Commands.command_for("KEY_DELETE", PLAY), (Action.DEL, None))

    def test_both_cases_of_a_letter_work(self):
        self.assertEqual(Commands.command_for("N", PLAY), (Action.NEXT, None))

    def test_question_mark_is_the_terminals_own_help(self):
        self.assertEqual(Commands.command_for("?", SETUP), (Commands.HELP, None))

    def test_unknown_key_is_no_command(self):
        self.assertIsNone(Commands.command_for("x", PLAY))

    # Help

    def test_help_lists_only_what_the_mode_offers(self):
        self.assertNotIn("u", self.__help_keys(SETUP))
        self.assertIn("u", self.__help_keys(PLAY))
        self.assertNotIn("Del", self.__help_keys(PLAY))

    def test_help_lines_up_the_dashes_after_the_keys(self):
        for offered in (SETUP, PLAY):
            lines = Commands.long_help(offered).split("\n")
            self.assertEqual(len({line.index(" - ") for line in lines}), 1, lines)

    def test_help_lists_the_same_commands_as_the_panel(self):
        for offered in (SETUP, PLAY):
            self.assertEqual(self.__help_keys(offered), [keys for keys, name in Commands.panel(offered)])

    # Private functions

    def __help_keys(self, offered) -> list:
        """The keys at the start of each line of the help for the offered actions"""
        return [line.split(" - ")[0].rstrip() for line in Commands.long_help(offered).split("\n")]


if __name__ == "__main__":
    main()
