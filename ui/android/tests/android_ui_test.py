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
    AUTO_SAVE_PATH = "files/autosave.json"
    SHADES = 3

    def setUp(self):
        self.screen = MagicMock()
        auto_save_patcher = patch("ui.android.android_ui.AutoSave")
        self.AutoSave = auto_save_patcher.start()
        self.addCleanup(auto_save_patcher.stop)
        self.auto_save = self.AutoSave.return_value
        self.ui = AndroidUI(self.screen, self.AUTO_SAVE_PATH, self.SHADES)
        self.done = []  # what a game whose UP opens a dialog did, in order (see __open_in_play)
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
        selected = [called.args[:2] for called in self.screen.showSelected.call_args_list]
        self.assertEqual(selected, [(0, 0), (2, 7), (2, 7)])

    def test_the_selected_cell_is_shown_with_its_related_cells_as_row_col_pairs(self):
        game = self.__game()
        game.related_cells.side_effect = lambda row, col: [(row, col + 1), (row + 1, col)]
        self.__play(game)
        self.screen.showSelected.assert_called_with(0, 0, [[0, 1], [1, 0]])

    def test_play_tells_the_screen_once_the_game_is_over(self):
        self.__play(self.__game())
        self.screen.gameOver.assert_called_once()

    def test_a_broken_action_is_reported_as_a_warning_to_be_seen_and_play_goes_on(self):
        game = self.__game(broken=Action.UP)
        self.ui.act("up")
        self.ui.answer(True)  # the OK to the warning
        with patch("ui.android.android_ui.ErrorLog.report_broken", return_value="it broke") as report:
            self.__play(game)
        self.assertEqual(report.call_args.args[0], "up")
        self.assertIsInstance(report.call_args.args[1], RuntimeError)
        self.screen.showInform.assert_called_once_with("it broke", MessageKind.WARNING.value)
        self.screen.questionAnswered.assert_called_once()
        self.assertEqual(game.handle.call_args_list[-1], call(Action.QUIT, None, None))

    def test_a_broken_quit_forces_the_game_to_stop(self):
        game = self.__game(broken=Action.QUIT)
        self.ui.act("quit")
        self.ui.answer(True)  # the OK to the warning
        with patch("ui.android.android_ui.ErrorLog.report_broken", return_value="it broke"):
            self.ui.play(game)
        game.force_quit_.assert_called_once()

    def test_a_forced_quit_ends_the_game_without_asking_and_forgets_the_saved_game(self):
        self.ui.act("force_quit")
        self.ui.play(Puzzle(Board3x3(), self.ui))
        self.screen.askConfirm.assert_not_called()
        self.auto_save.forget.assert_called_once()
        self.screen.gameOver.assert_called_once()

    # Auto-save

    def test_the_game_is_auto_saved_to_the_file_given(self):
        self.AutoSave.assert_called_once_with(self.AUTO_SAVE_PATH, self.ui)

    def test_play_restores_the_saved_game_once_the_game_is_shown(self):
        game = self.__game()
        game.render.side_effect = lambda: self.auto_save.restore.assert_not_called()
        self.__play(game)
        self.auto_save.restore.assert_called_once_with(game)

    def test_a_save_is_carried_out_in_turn_with_the_actions(self):
        game = self.__game()
        done = []
        game.handle.side_effect = self.__recording(game.handle.side_effect, done)
        self.auto_save.save.side_effect = lambda saved: done.append("save")
        self.ui.act("up")
        self.ui.save()
        self.ui.act("down")
        self.__play(game)
        self.assertEqual(done, [Action.UP, "save", Action.DOWN, Action.QUIT])
        self.auto_save.save.assert_called_once_with(game)

    def test_the_saved_game_is_forgotten_once_the_game_is_over_before_the_screen_hears_so(self):
        self.screen.gameOver.side_effect = lambda: self.auto_save.forget.assert_called_once()
        self.__play(self.__game())
        self.screen.gameOver.assert_called_once()

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
        self.screen.showCell.assert_called_with(0, 1, 0, "", "", 0, [1, 2, 3, 4, 6, 7, 8, 9], ["top"])

    def test_a_filled_cell_is_shown_with_its_value_kind_and_block_edges(self):
        board = Board3x3()
        Puzzle(board, RecordingUI())
        board.cell(0, 0).set(5, (CellAttrs.INITIAL,))
        self.ui.cell_changed(board.cell(0, 0))
        self.screen.showCell.assert_called_with(0, 0, 5, CellAttrs.INITIAL, "", 0, [], ["top", "left"])

    def test_a_cell_is_shown_with_its_conflict_and_guess_depth(self):
        board = Board3x3()
        Puzzle(board, RecordingUI())
        board.cell(8, 8).set(3, (CellAttrs.GUESS, CellAttrs.CONFLICTING, {"depth": 2}))
        self.ui.cell_changed(board.cell(8, 8))
        self.screen.showCell.assert_called_with(8, 8, 3, CellAttrs.GUESS, CellAttrs.CONFLICTING, 2, [], ["right", "bottom"])

    def test_a_cell_a_value_clashes_with_is_shown_as_conflicted(self):
        board = Board3x3()
        Puzzle(board, RecordingUI())
        board.cell(8, 8).set(3, (CellAttrs.CONFLICTED,))
        self.ui.cell_changed(board.cell(8, 8))
        self.assertEqual(self.screen.showCell.call_args.args[4], CellAttrs.CONFLICTED)

    def test_guesses_within_the_shades_of_gray_are_not_warned_of(self):
        for depth in range(self.SHADES + 1):
            self.ui.guess_depth_changed(depth)
        self.screen.showInform.assert_not_called()

    def test_guesses_deeper_than_the_last_shade_are_warned_of_once(self):
        self.__open_in_play(self.__guesses_to(*range(self.SHADES + 3)), lambda: self.ui.answer(True))
        self.screen.showInform.assert_called_once_with("No more shades of gray left - repeating last shade.", "warning")

    def test_guesses_that_go_back_within_the_shades_and_deeper_again_are_warned_of_again(self):
        deeper_twice = self.__guesses_to(self.SHADES, self.SHADES + 1, self.SHADES, self.SHADES + 1)
        self.__open_in_play(deeper_twice, lambda: self.ui.answer(True), lambda: self.ui.answer(True))
        self.assertEqual(self.screen.showInform.call_count, 2)

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

    # Dialogs

    def test_inform_has_the_screen_show_the_message_and_waits_until_the_player_has_seen_it(self):
        self.__open_in_play(lambda: self.ui.inform(Message("Cannot change an initial value", MessageKind.WARNING)), lambda: self.ui.answer(True))
        self.assertEqual(self.__dialog_calls(), [call.showInform("Cannot change an initial value", "warning"), call.questionAnswered()])

    def test_confirm_asks_the_screen_and_returns_the_players_answer(self):
        self.assertTrue(self.__open_in_play(self.__confirm, lambda: self.ui.answer(True)))
        self.screen.askConfirm.assert_called_once_with("Really quit?")

    def test_confirm_tells_the_screen_once_the_question_is_answered(self):
        self.__open_in_play(self.__confirm, lambda: self.ui.answer(True))
        self.assertEqual(self.__dialog_calls(), [call.askConfirm("Really quit?"), call.questionAnswered()])

    def test_confirm_returns_no_when_the_player_says_no(self):
        self.assertFalse(self.__open_in_play(self.__confirm, lambda: self.ui.answer(False)))

    def test_a_save_while_a_dialog_waits_is_carried_out_at_once(self):
        self.auto_save.save.side_effect = lambda game: self.done.append("save")
        self.__open_in_play(self.__confirm, self.ui.save, lambda: self.ui.answer(True))
        self.assertEqual(self.done, [Action.UP, "save", "answered", Action.QUIT])

    def test_actions_while_a_dialog_waits_are_carried_out_in_order_once_it_is_answered(self):
        self.__open_in_play(self.__confirm, lambda: self.ui.act("down"), lambda: self.ui.act("left"), lambda: self.ui.answer(True))
        self.assertEqual(self.done, [Action.UP, "answered", Action.DOWN, Action.LEFT, Action.QUIT])

    def test_an_answer_no_dialog_waits_for_is_dropped(self):
        self.ui.answer(True)
        self.assertFalse(self.__open_in_play(self.__confirm, lambda: self.ui.answer(False)))

    def test_a_dialog_opened_while_another_waits_is_answered_first(self):
        self.auto_save.save.side_effect = lambda game: self.ui.inform(Message("Cannot save", MessageKind.WARNING))
        self.assertFalse(self.__open_in_play(self.__confirm, self.ui.save, lambda: self.ui.answer(True), lambda: self.ui.answer(False)))
        self.assertEqual(self.__dialog_calls(), [call.askConfirm("Really quit?"), call.showInform("Cannot save", "warning"), call.questionAnswered(), call.questionAnswered()])

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
        game.related_cells.return_value = []

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

    @staticmethod
    def __recording(handle, done):
        """Wrap the stand-in game's handling of actions so that each action is also recorded in done"""

        def recorded(action, digit, position):
            done.append(action)
            handle(action, digit, position)

        return recorded

    def __play(self, game):
        """Play the actions queued so far, then quit"""
        self.ui.act("quit")
        self.ui.play(game)

    def __open_in_play(self, dialog, *requests):
        """
        Play a game whose UP opens the dialog, with the requests made after UP, then quit, recording in done each
        action as it starts and each answered dialog; return what the dialog returned
        """
        game = self.__game()
        returned = []
        handle = game.handle.side_effect

        def opening(action, digit, position):
            self.done.append(action)
            if action is Action.UP:
                returned.append(dialog())
            handle(action, digit, position)

        game.handle.side_effect = opening
        self.screen.questionAnswered.side_effect = lambda: self.done.append("answered")
        self.ui.act("up")
        for request in requests:
            request()
        self.__play(game)
        return returned[0]

    def __confirm(self):
        return self.ui.confirm("Really quit?")

    def __guesses_to(self, *depths):
        """What the game does when its guesses go to each of the depths in turn, for __open_in_play"""

        def deepen():
            for depth in depths:
                self.ui.guess_depth_changed(depth)

        return deepen

    def __dialog_calls(self):
        """The screen's calls that open or end a dialog, in order"""
        return [made for made in self.screen.method_calls if made[0] in ("showInform", "askConfirm", "questionAnswered")]


if __name__ == "__main__":
    main()
