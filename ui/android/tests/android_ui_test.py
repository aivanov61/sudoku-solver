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

from unittest import main, TestCase
from unittest.mock import call, MagicMock, patch

from game.actions import Action, Mode, OFFERED_ACTIONS
from game.cell_attrs import CellAttrs
from game.puzzle import Puzzle
from game.puzzles.board_3x3 import Board3x3
from game.tests.recording_ui import RecordingUI
from game.user_interface import Message, MessageKind
from ui.android.android_ui import AndroidUI


class TestAndroidUI(TestCase):
    def setUp(self):
        self.screen = MagicMock()
        self.ui = AndroidUI(self.screen)
        return super().setUp()

    # Playing

    def test_play_shows_the_game_then_hands_it_each_action_until_it_stops_playing(self):
        game = self.__game()
        self.ui.act("up")
        self.ui.act("value", digit=5)
        self.__play(game)
        self.assertEqual(game.handle.call_args_list, [call(Action.UP, None, None), call(Action.VALUE, 5, None), call(Action.QUIT, None, None)])
        game.render.assert_called_once()

    def test_a_tap_on_a_cell_hands_the_game_select_with_the_cells_position(self):
        game = self.__game()
        self.ui.act("select", row=2, col=7)
        self.__play(game)
        self.assertEqual(game.handle.call_args_list[0], call(Action.SELECT, None, (2, 7)))

    def test_play_shows_the_selected_cell_at_the_start_and_after_each_action(self):
        game = self.__game()
        self.ui.act("select", row=2, col=7)
        self.__play(game)
        self.assertEqual(self.screen.showSelected.call_args_list, [call(0, 0), call(2, 7), call(2, 7)])

    def test_play_tells_the_screen_once_the_game_is_over(self):
        self.__play(self.__game())
        self.screen.gameOver.assert_called_once()

    def test_a_broken_action_is_reported_on_the_status_line_and_play_goes_on(self):
        game = self.__game(broken=Action.UP)
        self.ui.act("up")
        with patch("ui.android.android_ui.ErrorLog.report_broken", return_value="it broke") as report:
            self.__play(game)
        self.assertEqual(report.call_args.args[0], "up")
        self.assertIsInstance(report.call_args.args[1], RuntimeError)
        self.screen.showStatus.assert_called_with("it broke", MessageKind.WARNING.value)
        self.assertEqual(game.handle.call_args_list[-1], call(Action.QUIT, None, None))

    def test_a_broken_quit_forces_the_game_to_stop(self):
        game = self.__game(broken=Action.QUIT)
        with patch("ui.android.android_ui.ErrorLog.report_broken", return_value="it broke"):
            self.__play(game)
        game.force_quit_.assert_called_once()

    # Showing the game

    def test_show_board_shows_every_cell(self):
        board = Board3x3()
        self.ui.show_board(board.cells())
        self.assertEqual(self.screen.showCell.call_count, 81)

    def test_an_empty_cell_is_shown_with_no_value_and_its_possible_values(self):
        board = Board3x3()
        Puzzle(board, RecordingUI())
        board.cell(0, 0).set(5, (CellAttrs.INITIAL,))
        self.ui.cell_changed(board.cell(0, 1))
        self.screen.showCell.assert_called_with(0, 1, 0, "", False, 0, [1, 2, 3, 4, 6, 7, 8, 9], ["top"])

    def test_a_filled_cell_is_shown_with_its_value_kind_and_block_edges(self):
        board = Board3x3()
        Puzzle(board, RecordingUI())
        board.cell(0, 0).set(5, (CellAttrs.INITIAL,))
        self.ui.cell_changed(board.cell(0, 0))
        self.screen.showCell.assert_called_with(0, 0, 5, CellAttrs.INITIAL, False, 0, [], ["top", "left"])

    def test_a_cell_is_shown_with_its_conflict_and_guess_depth(self):
        board = Board3x3()
        Puzzle(board, RecordingUI())
        board.cell(8, 8).set(3, (CellAttrs.GUESS, CellAttrs.CONFLICTING, {"depth": 2}))
        self.ui.cell_changed(board.cell(8, 8))
        self.screen.showCell.assert_called_with(8, 8, 3, CellAttrs.GUESS, True, 2, [], ["right", "bottom"])

    def test_mode_changed_passes_the_mode_and_its_actions_by_name(self):
        self.ui.mode_changed(Mode.SETUP, OFFERED_ACTIONS[Mode.SETUP])
        self.screen.modeChanged.assert_called_once_with("SETUP", [action.value for action in OFFERED_ACTIONS[Mode.SETUP]])

    # Messages

    def test_status_shows_the_message_with_its_kind(self):
        self.ui.status(Message("Well done", MessageKind.SUCCESS))
        self.screen.showStatus.assert_called_once_with("Well done", "success")

    def test_no_status_blanks_the_status_line(self):
        self.ui.status(None)
        self.screen.showStatus.assert_called_once_with("", "")

    def test_inform_shows_the_message_on_the_status_line_for_now(self):
        self.ui.inform(Message("Cannot change an initial value", MessageKind.WARNING))
        self.screen.showStatus.assert_called_once_with("Cannot change an initial value", "warning")

    # Dialogs

    def test_confirm_asks_the_screen_and_returns_the_players_answer(self):
        self.ui.answer(True)
        self.assertTrue(self.ui.confirm("Really quit?"))
        self.screen.askConfirm.assert_called_once_with("Really quit?")

    def test_confirm_tells_the_screen_once_the_question_is_answered(self):
        self.ui.answer(True)
        self.ui.confirm("Really quit?")
        self.assertEqual(self.screen.method_calls, [call.askConfirm("Really quit?"), call.questionAnswered()])

    def test_confirm_returns_no_when_the_player_says_no(self):
        self.ui.answer(False)
        self.assertFalse(self.ui.confirm("Really quit?"))

    def test_asking_for_a_file_name_cancels_for_now(self):
        self.assertIsNone(self.ui.ask_file_name("Save as", "puzzle", ".sudoku"))

    def test_configure_leaves_the_options_as_they_are_for_now(self):
        options = [MagicMock()]
        self.assertEqual(self.ui.configure(options), options)

    # Private functions

    def __game(self, broken=None):
        """A stand-in game that stops playing on QUIT or when forced to, and whose handling of the broken action fails"""
        game = MagicMock()
        game.is_playing = True
        game.selected_cell = (0, 0)

        def stop():
            game.is_playing = False

        def handle(action, digit, position):
            if action is broken:
                raise RuntimeError("broken")
            if action is Action.SELECT:
                game.selected_cell = position
            if action is Action.QUIT:
                stop()

        game.handle.side_effect = handle
        game.force_quit_.side_effect = stop
        return game

    def __play(self, game):
        """Play the actions queued so far, then quit"""
        self.ui.act("quit")
        self.ui.play(game)


if __name__ == "__main__":
    main()
