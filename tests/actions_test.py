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

from actions import Action, Mode, OFFERED_ACTIONS


class TestActions(TestCase):
    def test_both_modes_offer_values_moves_save_open_and_quit(self):
        shared = (Action.VALUE, Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.SAVE, Action.OPEN, Action.QUIT)
        for mode in Mode:
            for action in shared:
                self.assertIn(action, OFFERED_ACTIONS[mode], (mode, action))

    def test_setup_offers_play_and_clearing_but_no_guesses_or_solving(self):
        setup = OFFERED_ACTIONS[Mode.SETUP]
        self.assertIn(Action.PLAY, setup)
        self.assertIn(Action.DEL, setup)
        for action in (Action.INIT, Action.GUESS, Action.UNDO, Action.REWIND, Action.AUTO, Action.NEXT):
            self.assertNotIn(action, setup)

    def test_play_offers_guesses_and_solving_but_no_clearing(self):
        play = OFFERED_ACTIONS[Mode.PLAY]
        for action in (Action.INIT, Action.GUESS, Action.UNDO, Action.REWIND, Action.AUTO, Action.NEXT):
            self.assertIn(action, play)
        self.assertNotIn(Action.PLAY, play)
        self.assertNotIn(Action.DEL, play)

    def test_forced_quit_is_never_offered_by_a_key(self):
        for mode in Mode:
            self.assertNotIn(Action.FORCE_QUIT, OFFERED_ACTIONS[mode])


if __name__ == "__main__":
    main()
