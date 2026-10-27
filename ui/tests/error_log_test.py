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

import os
import sys
import tempfile
from unittest import main, TestCase
from unittest.mock import patch

sys.path.insert(0, ".")

from ui.error_log import ErrorLog


class TestErrorLog(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "sudoku.log")
        return super().setUp()

    def tearDown(self):
        self.temp_dir.cleanup()
        return super().tearDown()

    def test_an_error_is_recorded_with_its_traceback(self):
        self.assertEqual(self.__record(self.__error("oops")), self.path)
        logged = self.__logged()
        self.assertIn("Traceback", logged)
        self.assertIn("ValueError: oops", logged)

    def test_each_error_is_added_after_the_ones_before(self):
        self.__record(self.__error("first"))
        self.__record(self.__error("second"))
        logged = self.__logged()
        self.assertLess(logged.index("ValueError: first"), logged.index("ValueError: second"))

    def test_each_error_is_followed_by_a_blank_line_to_set_it_apart_from_the_next(self):
        self.__record(self.__error("first"))
        self.__record(self.__error("second"))
        logged = self.__logged()
        self.assertTrue(logged.endswith("ValueError: second\n\n"))
        self.assertIn("ValueError: first\n\n---", logged)

    def test_an_error_that_cannot_be_recorded_gives_no_file(self):
        self.path = os.path.join(self.temp_dir.name, "missing", "sudoku.log")
        self.assertIsNone(self.__record(self.__error("oops")))

    def test_where_is_the_innermost_place_on_the_stack(self):
        where = ErrorLog.where(self.__error("oops"))
        self.assertRegex(where, r"error_log_test\.py:\d+ in __fail$")

    # Private functions

    def __error(self, text) -> Exception:
        """An error raised, so that it has a traceback"""
        try:
            self.__fail(text)
        except ValueError as error:
            return error

    def __fail(self, text):
        raise ValueError(text)

    def __record(self, error):
        with patch.object(ErrorLog, "FILE", self.path):
            return ErrorLog.record(error)

    def __logged(self) -> str:
        with open(self.path, encoding="utf-8") as log:
            return log.read()


if __name__ == "__main__":
    main()
