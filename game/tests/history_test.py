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

from game import history
from game.cell import Cell
from game.history import History

# Set up mock parent for Cell which has return_value() as a required interface
CELL_MAX_VALUE = 10
cell_parent = MagicMock()
cell_parent.values.return_value = range(1, CELL_MAX_VALUE)

class TestHistory(TestCase):
    def setUp(self):
        self.history = History()
        return super().setUp()

    def test_add_history_adds_entries_to_the_end_of_history(self):
        # Add first entry (a simple, normal value)
        c1 = Cell(cell_parent, 0, 0)
        v1 = 1
        e1 = history.Entry(c1, history.Entry.ValueInfo(v1))
        self.history.add(e1)

        self.assertEqual(self.history.entries(), [e1])
        self.assertEqual(e1.valueinfo.prim_attr, None)

        # Add second entry (a guessed value)
        c2 = Cell(cell_parent, 1, 1)
        t2 = history.Entry.ValueInfo.GUESS
        v2 = 2
        e2 = history.Entry(c2, history.Entry.ValueInfo(v2, t2))
        self.history.add(e2)

        # The first entry remains intact, before the second
        self.assertEqual(self.history.entries(), [e1, e2])
        self.assertEqual(e2.valueinfo.prim_attr, t2)

    def test_undo_history_removes_and_returns_the_last_entry(self):
        e1 = history.Entry(Cell(cell_parent, 0, 0), history.Entry.ValueInfo(1))
        e2 = history.Entry(Cell(cell_parent, 1, 1), history.Entry.ValueInfo(2))
        self.history.add(e1)
        self.history.add(e2)

        self.assertEqual(self.history.undo(), e2)
        self.assertEqual(self.history.entries(), [e1])

    def test_last_returns_the_last_entry_without_removing_it(self):
        e1 = history.Entry(Cell(cell_parent, 0, 0), history.Entry.ValueInfo(1))
        e2 = history.Entry(Cell(cell_parent, 1, 1), history.Entry.ValueInfo(2))
        self.history.add(e1)
        self.history.add(e2)

        self.assertEqual(self.history.last(), e2)
        self.assertEqual(self.history.entries(), [e1, e2])

    def test_entries_lists_the_entries_oldest_first_without_removing_them(self):
        e1 = history.Entry(Cell(cell_parent, 0, 0), history.Entry.ValueInfo(1))
        e2 = history.Entry(Cell(cell_parent, 1, 1), history.Entry.ValueInfo(2))
        self.history.add(e1)
        self.history.add(e2)

        self.assertEqual(self.history.entries(), [e1, e2])
        self.assertEqual(self.history.entries(), [e1, e2])

    def test_clear_removes_every_entry(self):
        self.history.add(history.Entry(Cell(cell_parent, 0, 0), history.Entry.ValueInfo(1)))
        self.history.clear()
        self.assertTrue(self.history.is_empty())

    def test_each_history_keeps_its_own_entries(self):
        self.history.add(history.Entry(Cell(cell_parent, 0, 0), history.Entry.ValueInfo(1)))
        self.assertTrue(History().is_empty())
        self.assertFalse(self.history.is_empty())


if __name__ == "__main__":
    main()
