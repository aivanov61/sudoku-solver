# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import sys
from unittest import main, TestCase
from unittest.mock import MagicMock

sys.path.insert(0, '.')

from rectangular_block import RectangularBlock

class TestRectangularBlock(TestCase):

    def setUp(self):
        self.__setup_parent()

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        """
        self.parent = MagicMock()

    BLOCK_ROWS = 3
    BLOCK_COLS = 3

    def test_block_can_render(self):
        block1 = RectangularBlock(self.parent, 0, 0, self.BLOCK_ROWS, self.BLOCK_COLS)
        block2 = RectangularBlock(self.parent, 0, 2, self.BLOCK_ROWS, self.BLOCK_COLS)
        block1.render()
        block2.render()

main()
