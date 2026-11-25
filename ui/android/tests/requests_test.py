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

from collections import deque
from unittest import main, TestCase
from unittest.mock import MagicMock

from ui.android.requests import Act, Answer, Save


class TestRequests(TestCase):
    def setUp(self):
        self.game = MagicMock()
        self.held = deque()
        return super().setUp()

    # Act

    def test_an_action_is_carried_out_in_play(self):
        carry_out = MagicMock()
        Act(carry_out).in_play(self.game)
        carry_out.assert_called_once_with(self.game)

    def test_an_action_is_held_while_a_dialog_waits(self):
        carry_out = MagicMock()
        act = Act(carry_out)
        self.assertIsNone(act.while_waiting(self.game, self.held))
        self.assertEqual(list(self.held), [act])
        carry_out.assert_not_called()

    # Save

    def test_a_save_is_carried_out_in_play(self):
        auto_save = MagicMock()
        Save(auto_save).in_play(self.game)
        auto_save.save.assert_called_once_with(self.game)

    def test_a_save_is_carried_out_at_once_while_a_dialog_waits(self):
        auto_save = MagicMock()
        self.assertIsNone(Save(auto_save).while_waiting(self.game, self.held))
        auto_save.save.assert_called_once_with(self.game)
        self.assertEqual(list(self.held), [])

    # Answer

    def test_an_answer_ends_the_wait_with_the_players_answer(self):
        self.assertIs(Answer(True).while_waiting(self.game, self.held), True)
        self.assertIs(Answer(False).while_waiting(self.game, self.held), False)
        self.assertEqual(list(self.held), [])

    def test_an_answer_no_dialog_waits_for_is_dropped(self):
        Answer(True).in_play(self.game)
        self.assertEqual(self.game.mock_calls, [])


if __name__ == "__main__":
    main()
