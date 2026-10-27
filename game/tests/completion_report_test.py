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

from game.completion_report import CompletionReport
from game.user_interface import MessageKind


class TestCompletionReport(TestCase):
    def setUp(self):
        self.puzzle = MagicMock()
        self.puzzle.is_complete.return_value = False
        self.puzzle.has_conflicts.return_value = False
        self.report = CompletionReport(self.puzzle)
        return super().setUp()

    def test_no_message_while_the_puzzle_is_not_complete(self):
        self.assertIsNone(self.report.message())

    def test_solved_puzzle_is_reported_until_it_is_seen(self):
        self.puzzle.is_complete.return_value = True
        self.assertIn("solved", self.report.message().text)
        self.assertEqual(self.report.message().kind, MessageKind.SUCCESS)
        self.report.seen()
        self.assertIsNone(self.report.message())

    def test_complete_puzzle_with_conflicts_is_reported_with_how_to_fix_it(self):
        self.puzzle.is_complete.return_value = True
        self.puzzle.has_conflicts.return_value = True
        self.assertIn("undo or change values", self.report.message().text)
        self.assertEqual(self.report.message().kind, MessageKind.WARNING)

    def test_completion_is_reported_again_when_it_changes(self):
        self.puzzle.is_complete.return_value = True
        self.puzzle.has_conflicts.return_value = True
        self.report.message()
        self.report.seen()
        self.puzzle.has_conflicts.return_value = False
        self.assertIn("solved", self.report.message().text)

    def test_completion_is_reported_again_after_being_unfinished(self):
        self.puzzle.is_complete.return_value = True
        self.report.message()
        self.report.seen()
        self.puzzle.is_complete.return_value = False
        self.report.message()
        self.puzzle.is_complete.return_value = True
        self.assertIn("solved", self.report.message().text)

    def test_completion_is_reported_again_after_a_reset(self):
        self.puzzle.is_complete.return_value = True
        self.report.message()
        self.report.seen()
        self.report.reset()
        self.assertIn("solved", self.report.message().text)

    def test_warning_about_an_already_solved_puzzle(self):
        self.assertIn("already solved", self.report.already_complete().text)
        self.assertEqual(self.report.already_complete().kind, MessageKind.WARNING)

    def test_warning_about_an_already_complete_puzzle_with_conflicts(self):
        self.puzzle.has_conflicts.return_value = True
        self.assertIn("undo or change values", self.report.already_complete().text)


if __name__ == "__main__":
    main()
