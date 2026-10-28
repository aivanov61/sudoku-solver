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


class MenuEntry:
    """A menu line that ENTER picks, standing for a value; one that can't be picked is grayed out and skipped"""

    def __init__(self, label, value, can_pick=True):
        self.label = label
        self.value = value
        self.__can_pick = can_pick

    def is_selectable(self) -> bool:
        return self.__can_pick
