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

from unittest import main, TestCase
from unittest.mock import patch

from game.puzzle_catalog import PuzzleLayout
from game.puzzles.board_3x3 import Board3x3
from ui.android.catalog import Catalog


class TestCatalog(TestCase):
    LAYOUTS = [PuzzleLayout("bad.py"), PuzzleLayout(Board3x3.NAME, Board3x3)]

    def test_every_layout_is_listed_with_its_label_and_whether_it_can_be_picked(self):
        with patch("ui.android.catalog.PuzzleCatalog.available", return_value=self.LAYOUTS):
            listed = Catalog.layouts()
        self.assertEqual(listed, [("bad.py", "bad.py (broken: could not be loaded)", False), (Board3x3.NAME, Board3x3.NAME, True)])

    def test_the_real_catalog_lists_the_standard_board(self):
        self.assertIn((Board3x3.NAME, Board3x3.NAME, True), Catalog.layouts())

    def test_a_layout_named_gives_a_new_board_of_it(self):
        board = Catalog.board(Board3x3.NAME)
        self.assertIsInstance(board, Board3x3)
        self.assertIsNot(board, Catalog.board(Board3x3.NAME))

    def test_a_layout_the_catalog_does_not_have_is_refused(self):
        with self.assertRaises(KeyError):
            Catalog.board("No such layout")


if __name__ == "__main__":
    main()
