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

from cell import Cell


class TestCell(TestCase):
    MAX_VALUE = 10

    def setUp(self):
        self.__setup_parent()
        self.cell = Cell(self.parent, **self.x())
        return super().setUp()

    def x(self):
        return {"row": 0, "col": 0}

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        1. values() - range of legal values
        """
        self.parent = MagicMock()
        self.parent.values.return_value = range(1, self.MAX_VALUE)

    def test_cell_initial_value_is_not_set(self):
        self.assertIsNone(self.cell.value())

    def test_cell_value_can_be_set(self):
        self.cell.set(8)
        self.assertEqual(self.cell.value(), 8)

    def test_cell_value_has_limits_set_by_parent(self):
        self.assertRaises(ValueError, self.cell.set, self.MAX_VALUE)

    def test_cell_can_render(self):
        self.cell.render()


main()
