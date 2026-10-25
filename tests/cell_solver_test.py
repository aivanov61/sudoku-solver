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

from cell_solver import CellSolver


class TestCellSolver(TestCase):
    MAX_VALUE = 10

    def setUp(self):
        self.__setup_parent()
        self.solver = CellSolver(self.parent)
        return super().setUp()

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        1. values() - range of legal values
        """
        self.parent = MagicMock()
        self.parent.values.return_value = range(1, self.MAX_VALUE)

    def test_all_values_are_initially_possible(self):
        self.assertEqual(self.solver.possible_values(), set(range(1, self.MAX_VALUE)))

    def test_remove_possible_removes_only_that_value(self):
        self.solver.remove_possible(5)
        self.assertEqual(self.solver.possible_values(), set(range(1, self.MAX_VALUE)) - {5})

    def test_remove_possible_ignores_value_already_removed(self):
        self.solver.remove_possible(5)
        self.solver.remove_possible(5)
        self.assertNotIn(5, self.solver.possible_values())

    def test_clear_possible_removes_all_values(self):
        self.solver.clear_possible()
        self.assertEqual(self.solver.possible_values(), set())


if __name__ == "__main__":
    main()
