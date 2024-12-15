# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import random
import sys
sys.path.insert(0, '.')

from unittest import main, TestCase

from display import Display, Border

class TestDisplay(TestCase):
    Display.geometry({'h_cells': 9, 'v_cells': 9})

    def setUp(self):
        pass

    def test_screen_size_validation(self):
        Display.validate_screen_size()
        Display.term.inkey(timeout=1.0)

    def test_draw_puzzle(self):
        for row in range(3):
            for col in range(3):
                self.draw_block(row, col)
        self.fill_blocks()
        Display.term.inkey(timeout=1.0)

    def test_warn(self0):
        Display.warn("Testing - should be yellow")
        Display.term.inkey(timeout=1.0)

    def draw_block(self, block_row, block_col):
        Display.draw_cell(row=block_row*3 + 0, col=block_col*3 + 0, border=Border({'top','left'}))
        Display.draw_cell(row=block_row*3 + 0, col=block_col*3 + 1, border=Border({'top'}))
        Display.draw_cell(row=block_row*3 + 0, col=block_col*3 + 2, border=Border({'top','right'}))

        Display.draw_cell(row=block_row*3 + 1, col=block_col*3 + 0, border=Border({'left'}))
        Display.draw_cell(row=block_row*3 + 1, col=block_col*3 + 1, border=Border())
        Display.draw_cell(row=block_row*3 + 1, col=block_col*3 + 2, border=Border({'right'}))

        Display.draw_cell(row=block_row*3 + 2, col=block_col*3 + 0, border=Border({'left','bottom'}))
        Display.draw_cell(row=block_row*3 + 2, col=block_col*3 + 1, border=Border({'bottom'}))
        Display.draw_cell(row=block_row*3 + 2, col=block_col*3 + 2, border=Border({'right','bottom'}))

    def fill_blocks(self):
        for row in range(9):
            for col in range(9):
                Display.draw_cell_value(row, col, 1 + (row+col)//2)
                Display.draw_cell_possible_values(row, col, random.choices(range(1,10), k=random.randint(0,6)))
        Display.move_to_status_line()

main()
