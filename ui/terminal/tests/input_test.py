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

from unittest import main, TestCase
from unittest.mock import MagicMock

from blessed.keyboard import Keystroke

from game.actions import Action, Mode, OFFERED_ACTIONS
from ui.terminal.display import Display
from ui.terminal.input import Input

PLAY = OFFERED_ACTIONS[Mode.PLAY]


class TestInput(TestCase):
    def test_get_input(self):
        print('Hit a valid command key, like "?" or CTRL-C, to continue; timeout=2 seconds')
        cmd = Input(Display()).get_cmd(PLAY, timeout=2.0)
        print(f'cmd="{cmd}"')


class TestInputDecoding(TestCase):
    def test_keys_that_are_not_bound_are_skipped(self):
        self.assertEqual(self.__get_cmd_with([Keystroke("x"), Keystroke("u")]), (Action.UNDO, None))

    def test_special_keys_are_decoded_by_name(self):
        self.assertEqual(self.__get_cmd_with([Keystroke("\x1b[A", code=1, name="KEY_UP")]), (Action.UP, None))

    def test_a_timeout_is_no_command(self):
        self.assertIsNone(self.__get_cmd_with([Keystroke("")]))

    def test_ctrl_c_is_a_forced_quit(self):
        self.assertEqual(self.__get_cmd_with(KeyboardInterrupt()), (Action.FORCE_QUIT, None))

    def test_input_error_is_a_forced_quit(self):
        self.assertEqual(self.__get_cmd_with(OSError()), (Action.FORCE_QUIT, None))

    def test_get_key_of_skips_other_keys_and_returns_the_key_by_name(self):
        keys = [Keystroke("x"), Keystroke("\x1b[A", code=1, name="KEY_UP")]
        self.assertEqual(self.__get_key_of_with(keys), "KEY_UP")

    def test_get_key_of_returns_a_character_as_it_is(self):
        self.assertEqual(self.__get_key_of_with([Keystroke("w")]), "w")

    def test_get_key_of_returns_none_after_ctrl_c(self):
        self.assertIsNone(self.__get_key_of_with(KeyboardInterrupt()))

    def test_get_key_of_returns_none_after_an_input_error(self):
        self.assertIsNone(self.__get_key_of_with(OSError()))

    # Private functions

    def __get_key_of_with(self, keys):
        display = MagicMock()
        display.term.inkey.side_effect = keys
        return Input(display).get_key_of(("w", "KEY_UP"))

    def __get_cmd_with(self, keys):
        display = MagicMock()
        display.term.inkey.side_effect = keys
        return Input(display).get_cmd(PLAY)


if __name__ == "__main__":
    main()
