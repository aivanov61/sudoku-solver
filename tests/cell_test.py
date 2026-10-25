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
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from cell import Cell
from display_attrs import DisplayAttrs


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
        2. is_conflicting() - whether another related cell already holds the value
        """
        self.parent = MagicMock()
        self.parent.values.return_value = range(1, self.MAX_VALUE)
        self.parent.is_conflicting.return_value = False

    def test_cell_initial_value_is_not_set(self):
        self.assertIsNone(self.cell.value())

    def test_cell_value_can_be_set(self):
        self.cell.set(8)
        self.assertEqual(self.cell.value(), 8)

    def test_cell_value_has_limits_set_by_parent(self):
        self.assertRaises(ValueError, self.cell.set, self.MAX_VALUE)

    def test_cell_clears_its_possible_values_when_value_is_set(self):
        self.cell.set(8)
        self.assertEqual(self.cell.possible_values(), set())

    def test_cell_value_is_conflicting_when_parent_reports_conflict(self):
        self.parent.is_conflicting.return_value = True
        self.cell.set(8)
        self.parent.is_conflicting.assert_called_once_with(0, 0, 8)
        self.assertIn(DisplayAttrs.CONFLICTING, self.cell.attr())

    def test_cell_value_is_not_conflicting_when_parent_reports_no_conflict(self):
        self.cell.set(8)
        self.assertNotIn(DisplayAttrs.CONFLICTING, self.cell.attr())

    def test_cell_remove_possible_updates_solver(self):
        self.cell.remove_possible(5)
        self.assertNotIn(5, self.cell.possible_values())

    def test_cell_clear_possible_updates_solver(self):
        self.cell.clear_possible()
        self.assertEqual(self.cell.possible_values(), set())

    @patch("cell.Display.draw_cell_possible_values")
    def test_cell_draws_possible_values_when_value_removed(self, draw):
        self.cell.remove_possible(5)
        draw.assert_called_once_with(0, 0, self.cell.possible_values(), self.cell.attr())

    @patch("cell.Display.draw_cell_possible_values")
    def test_cell_does_not_draw_when_removed_value_was_not_possible(self, draw):
        self.cell.remove_possible(5)
        draw.reset_mock()
        self.cell.remove_possible(5)
        draw.assert_not_called()

    @patch("cell.Display.draw_cell_possible_values")
    def test_cell_draws_possible_values_when_cleared(self, draw):
        self.cell.clear_possible()
        draw.assert_called_once_with(0, 0, set(), self.cell.attr())

    @patch("cell.Display.draw_cell_possible_values")
    def test_cell_does_not_draw_when_already_cleared(self, draw):
        self.cell.clear_possible()
        draw.reset_mock()
        self.cell.clear_possible()
        draw.assert_not_called()

    def test_cell_can_render(self):
        self.cell.render()


if __name__ == "__main__":
    main()
