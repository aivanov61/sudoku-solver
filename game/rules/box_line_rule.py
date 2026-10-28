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

from game.house import House
from game.rules.intersection_rule import IntersectionRule


class BoxLineRule(IntersectionRule):
    """A value that can only go in one box of a row (or column) can go nowhere else in that box"""

    NAME = "box/line reduction"

    def _is_source(self, house: House) -> bool:
        return house.kind != House.BOX

    def _reason(self, value, source: House, target: House) -> str:
        return f"in one {source.kind}, {value} can only go in one box"
