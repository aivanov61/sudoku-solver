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

import history
from history import History

# Set up mock parent for Cell which has return_value() as a required interface
CELL_MAX_VALUE = 10
cell_parent = MagicMock()
cell_parent.values.return_value = range(1, CELL_MAX_VALUE)

class TestHistory(TestCase):
    def setUp(self):
        History.clear()
        return super().setUp()

    def test_add_history_adds_entries_to_the_end_of_history(self):
        _h = History._history

        # Add first entry (a simple, normal value)
        c1 = history.Cell(cell_parent, 0, 0)
        v1 = 1
        e1 = history.Entry(c1, history.Entry.ValueInfo(v1))
        History.add(e1)

        self.assertEqual(len(_h), 1)
        self.assertEqual(_h[-1].cell, c1)
        self.assertEqual(_h[-1].valueinfo.value, v1)
        self.assertEqual(_h[-1].valueinfo.prim_attr, None)

        # Add second entry (a guessed value)
        c2 = history.Cell(cell_parent, 1, 1)
        t2 = history.Entry.ValueInfo.GUESS
        v2 = 2
        e2 = history.Entry(c2, history.Entry.ValueInfo(v2, t2))
        History.add(e2)

        self.assertEqual(len(_h), 2)
        self.assertEqual(_h[-1].cell, c2)
        self.assertEqual(_h[-1].valueinfo.value, v2)
        self.assertEqual(_h[-1].valueinfo.prim_attr, t2)

        # Make sure first entry remains intact
        self.assertEqual(_h[0].cell, c1)
        self.assertEqual(_h[0].valueinfo.value, v1)
        self.assertEqual(_h[0].valueinfo.prim_attr, None)

    def test_undo_history_removes_and_returns_the_last_entry(self):
        _h = History._history

        c1 = history.Cell(cell_parent, 0, 0)
        v1 = 1
        e1 = history.Entry(c1, history.Entry.ValueInfo(v1))
        History.add(e1)

        c2 = history.Cell(cell_parent, 1, 1)
        v2 = 2
        e2 = history.Entry(c2, history.Entry.ValueInfo(v2))
        History.add(e2)

        u2 = History.undo()
        self.assertEqual(len(_h), 1)
        self.assertEqual(u2, e2)


if __name__ == "__main__":
    main()
