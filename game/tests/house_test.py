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
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from game.house import House


class TestHouse(TestCase):
    def test_a_house_knows_its_kind_and_cells(self):
        cells = [self.__cell(set()), self.__cell({1})]
        house = House(House.ROW, cells)
        self.assertEqual((house.kind, house.cells), ("row", cells))

    def test_the_kinds_are_named_as_players_know_them(self):
        self.assertEqual((House.BOX, House.ROW, House.COLUMN), ("box", "row", "column"))

    def test_places_are_the_cells_that_can_still_hold_the_value_in_order(self):
        cells = [self.__cell({4, 5}), self.__cell({5}), self.__cell(set()), self.__cell({4})]
        self.assertEqual(House(House.BOX, cells).places(4), [cells[0], cells[3]])

    def test_a_value_with_no_place_left_has_no_places(self):
        cells = [self.__cell({5}), self.__cell(set())]
        self.assertEqual(House(House.COLUMN, cells).places(4), [])

    # Private functions

    def __cell(self, possible_values):
        cell = MagicMock()
        cell.possible_values.return_value = possible_values
        return cell


if __name__ == "__main__":
    main()
