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

from recording_ui import RecordingUI
from terminal_ui import TerminalUI
from user_interface import UserInterface


class TestUserInterface(TestCase):
    def test_every_user_interface_implements_the_port(self):
        port_methods = [name for name in vars(UserInterface) if not name.startswith("_")]
        for ui_class in (TerminalUI, RecordingUI):
            missing = [name for name in port_methods if not hasattr(ui_class, name)]
            self.assertEqual(missing, [], ui_class.__name__)


if __name__ == "__main__":
    main()
