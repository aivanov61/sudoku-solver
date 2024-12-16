# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
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
