# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import sys
from unittest import main, TestCase

sys.path.insert(0, '.')

from input import Input

class TestInput(TestCase):
    def test_get_input(self):
        print('Hit a valid command key, like "?" or CTRL-C, to continue; timeout=2 seconds')
        cmd = Input.get_cmd(timeout=2.0)
        print(f'cmd="{cmd}"')

main()
