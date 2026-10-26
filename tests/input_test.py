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
from unittest.mock import patch

sys.path.insert(0, ".")

from display import Display
from input import Input


class TestInput(TestCase):
    def test_get_input(self):
        print('Hit a valid command key, like "?" or CTRL-C, to continue; timeout=2 seconds')
        cmd = Input.get_cmd(timeout=2.0)
        print(f'cmd="{cmd}"')


class TestInputForcedQuit(TestCase):
    def test_ctrl_c_is_a_forced_quit(self):
        with patch.object(Display, "term") as term:
            term.inkey.side_effect = KeyboardInterrupt()
            self.assertEqual(Input.get_cmd(), "force_quit_")

    def test_input_error_is_a_forced_quit(self):
        with patch.object(Display, "term") as term:
            term.inkey.side_effect = OSError()
            self.assertEqual(Input.get_cmd(), "force_quit_")


if __name__ == "__main__":
    main()
