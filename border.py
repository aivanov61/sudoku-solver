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

class Border:
    """Which sides of a cell lie on the edge of its block: layout data, however the edges are drawn"""

    TOP = "top"
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"

    def __init__(self, borders=frozenset()):
        self.__borders = borders

    def is_top(self):
        return self.TOP in self.__borders

    def is_left(self):
        return self.LEFT in self.__borders

    def is_right(self):
        return self.RIGHT in self.__borders

    def is_bottom(self):
        return self.BOTTOM in self.__borders
