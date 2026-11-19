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
from textwrap import indent


class Copyright:
    """
    The GNU GPL notice, shown as the terminal's splash.  The text is in ui/copyright.txt, which the Android app shows
    on its splash screen too, so there is one copy of it.
    """

    FILE = Path(__file__).parent.parent / "copyright.txt"
    INDENT = " " * 8

    @staticmethod
    def splash() -> None:
        """Print the notice, indented, after a blank line"""
        print("\n" + indent(Copyright.FILE.read_text(encoding="utf-8"), Copyright.INDENT))
