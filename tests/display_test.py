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

import random
import sys

sys.path.insert(0, ".")

from unittest import main, TestCase

from display import Display, Border


class TestDisplay(TestCase):
    Display.geometry({"h_cells": 9, "v_cells": 9})

    def setUp(self):
        return super().setUp()

    def tearDown(self):
        Display.term.inkey(timeout=1.0)
        return super().tearDown()

    def test_screen_size_validation(self):
        Display.validate_screen_size()

    def test_draw_puzzle(self):
        for row in range(3):
            for col in range(3):
                self.draw_block(row, col)
        self.fill_blocks()

    def test_warn(self0):
        Display.warn("Testing - this line should be yellow")

    def draw_block(self, block_row, block_col):
        Display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 0, border=Border({Border.TOP, Border.LEFT}))
        Display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 1, border=Border({Border.TOP}))
        Display.draw_cell(row=block_row * 3 + 0, col=block_col * 3 + 2, border=Border({Border.TOP, Border.RIGHT}))

        Display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 0, border=Border({Border.LEFT}))
        Display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 1, border=Border())
        Display.draw_cell(row=block_row * 3 + 1, col=block_col * 3 + 2, border=Border({Border.RIGHT}))

        Display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 0, border=Border({Border.LEFT, Border.BOTTOM}))
        Display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 1, border=Border({Border.BOTTOM}))
        Display.draw_cell(row=block_row * 3 + 2, col=block_col * 3 + 2, border=Border({Border.RIGHT, Border.BOTTOM}))

    def fill_blocks(self):
        for row in range(9):
            for col in range(9):
                Display.draw_cell_value(row, col, 1 + (row + col) // 2)
                Display.draw_cell_possible_values(row, col, random.choices(range(1, 10), k=random.randint(0, 6)))
        Display.move_to_status_line()


if __name__ == "__main__":
    main()
