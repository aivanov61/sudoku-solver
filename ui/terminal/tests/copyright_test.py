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

from pathlib import Path
from unittest import main, TestCase
from unittest.mock import patch

from ui.terminal.copyright import Copyright


class TestCopyright(TestCase):
    SHARED = Path("ui") / "copyright.txt"  # the notice the Android app shows too

    def test_the_splash_shows_the_notice_shared_with_the_android_app(self):
        shown = self.__splash()
        lines = [line for line in self.SHARED.read_text(encoding="utf-8").splitlines() if line]
        self.assertGreater(len(lines), 0)
        for line in lines:
            self.assertIn(line, shown)

    def test_the_splash_indents_the_notice_after_a_blank_line(self):
        shown = self.__splash()
        self.assertTrue(shown.startswith("\n        Copyright (c) by Anton Ivanov."))

    # Private functions

    def __splash(self) -> str:
        """The text the splash prints"""
        with patch("builtins.print") as printed:
            Copyright.splash()
        return printed.call_args.args[0]


if __name__ == "__main__":
    main()
