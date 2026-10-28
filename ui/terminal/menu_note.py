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

sys.path.insert(0, ".")

from ui.terminal.menu_choice import MenuChoice
from ui.terminal.menu_item import MenuItem


class MenuNote(MenuItem):
    """
    A grayed-out menu line under a choice, explaining the choice made; it follows the choice as it changes, and
    is blank for a choice without a note, so the lines below never move.  It is never selected.
    """

    INDENT = MenuChoice.INDENT + "  "  # under its choice

    def __init__(self, choice: MenuChoice, notes: list):
        self.__choice = choice
        self.__notes = notes  # the note for each of the choice's labels, "" for none

    def text(self) -> str:
        return self.__notes[self.__choice.chosen]

    def is_selectable(self) -> bool:
        return False

    def is_grayed_out(self) -> bool:
        return True
