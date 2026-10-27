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

from display_attrs import DisplayAttrs
from moves import Moves


class TestMoves(TestCase):
    def setUp(self):
        self.puzzle = MagicMock()
        self.puzzle.is_initializing.return_value = False
        self.moves = Moves(self.puzzle)
        return super().setUp()

    def test_typed_value_while_playing_is_entered_and_recorded(self):
        cell = self.__cell(1, 2)
        self.moves.enter(cell, 5)
        cell.update.assert_called_with(5, ())
        self.assertEqual(self.moves.recorded(), [(1, 2, 5, None)])

    def test_value_entered_during_setup_is_a_given_and_not_recorded(self):
        self.puzzle.is_initializing.return_value = True
        cell = self.__cell()
        self.moves.enter(cell, 5)
        cell.update.assert_called_with(5, (DisplayAttrs.INITIAL,))
        self.assertTrue(self.moves.is_empty())

    def test_guess_shades_itself_and_every_value_entered_after_it(self):
        guess, later = self.__cell(0, 0), self.__cell(0, 1)
        self.moves.enter(guess, 3, DisplayAttrs.GUESS)
        self.moves.enter(later, 4)
        guess.update.assert_called_with(3, (DisplayAttrs.GUESS, dict(level=Moves.SHADE_STEP)))
        later.update.assert_called_with(4, (dict(level=Moves.SHADE_STEP),))

    def test_undo_restores_the_previous_value_and_returns_its_cell(self):
        cell = self.__cell(value=7, attr=(DisplayAttrs.SOLVED,))
        self.moves.enter(cell, 5)
        self.assertIs(self.moves.undo(), cell)
        cell.update.assert_called_with(7, (DisplayAttrs.SOLVED,))
        self.assertTrue(self.moves.is_empty())

    def test_undoing_a_guess_lightens_the_shading_again(self):
        self.moves.enter(self.__cell(0, 0), 3, DisplayAttrs.GUESS)
        self.moves.undo()
        later = self.__cell(0, 1)
        self.moves.enter(later, 4)
        later.update.assert_called_with(4, ())

    def test_rewind_undoes_back_to_the_most_recent_guess_and_returns_its_cell(self):
        guess = self.__cell(0, 0)
        self.moves.enter(self.__cell(5, 5), 1)
        self.moves.enter(guess, 3, DisplayAttrs.GUESS)
        self.moves.enter(self.__cell(0, 1), 4)
        self.moves.enter(self.__cell(0, 2), 5)
        self.assertIs(self.moves.rewind(), guess)
        self.assertEqual(self.moves.recorded(), [(5, 5, 1, None), (0, 0, 3, DisplayAttrs.GUESS)])

    def test_rewind_without_a_guess_undoes_everything_and_returns_the_first_cell(self):
        first = self.__cell(0, 0)
        self.moves.enter(first, 1)
        self.moves.enter(self.__cell(0, 1), 2)
        self.assertIs(self.moves.rewind(), first)
        self.assertTrue(self.moves.is_empty())

    def test_clear_forgets_the_moves_and_the_shading(self):
        self.moves.enter(self.__cell(0, 0), 3, DisplayAttrs.GUESS)
        self.moves.clear()
        later = self.__cell(0, 1)
        self.moves.enter(later, 4)
        self.assertEqual(self.moves.recorded(), [(0, 1, 4, None)])
        later.update.assert_called_with(4, ())

    def test_each_moves_keeps_its_own_history(self):
        self.moves.enter(self.__cell(), 1)
        self.assertTrue(Moves(self.puzzle).is_empty())
        self.assertFalse(self.moves.is_empty())

    # Private functions

    def __cell(self, row=0, col=0, value=None, attr=()):
        cell = MagicMock(row=row, col=col)
        cell.value.return_value = value
        cell.attr.return_value = attr
        return cell


if __name__ == "__main__":
    main()
