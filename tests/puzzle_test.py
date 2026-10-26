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

sys.path.insert(0, ".")

from puzzle import Puzzle


class TestPuzzle(TestCase):
    def test_puzzle_itself_cannot_be_created(self):
        with self.assertRaises(TypeError):
            Puzzle(9, 9)

    def test_layout_missing_a_hook_cannot_be_created(self):
        class MissingBlockAt(Puzzle):
            def _blocks(self):
                return iter(())

        with self.assertRaises(TypeError):
            MissingBlockAt(9, 9)


if __name__ == "__main__":
    main()
