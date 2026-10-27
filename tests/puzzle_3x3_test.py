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
from unittest.mock import patch

sys.path.insert(0, ".")

from commands import Commands
from display import Display
from display_attrs import DisplayAttrs
from puzzle import Puzzle
from puzzles.board_3x3 import Board3x3


class TestPuzzle3x3(TestCase):
    SIZE = 9
    ALL_VALUES = set(range(1, SIZE + 1))

    def setUp(self):
        with patch("display.Display.validate_screen_size"):
            self.puzzle = Puzzle(Board3x3())
        return super().setUp()

    def test_arrow_commands_move_the_selected_cell(self):
        self.puzzle.selected_cell = (4, 4)
        self.puzzle.up_()
        self.puzzle.left_()
        self.assertEqual(self.puzzle.selected_cell, (3, 3))
        self.puzzle.down_()
        self.puzzle.right_()
        self.assertEqual(self.puzzle.selected_cell, (4, 4))

    def test_arrow_commands_stop_at_the_top_left_edge(self):
        self.puzzle.selected_cell = (0, 0)
        self.puzzle.up_()
        self.puzzle.left_()
        self.assertEqual(self.puzzle.selected_cell, (0, 0))

    def test_arrow_commands_stop_at_the_bottom_right_edge(self):
        self.puzzle.selected_cell = (8, 8)
        self.puzzle.down_()
        self.puzzle.right_()
        self.assertEqual(self.puzzle.selected_cell, (8, 8))

    def test_setting_value_clears_all_possible_values_of_that_cell(self):
        self.__cell(4, 4).set(5)
        self.assertEqual(self.__cell(4, 4).possible_values(), set())

    def test_setting_value_removes_it_from_row_column_and_box(self):
        self.__cell(4, 4).set(5)
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if (row, col) != (4, 4) and self.__is_affected_by(row, col, 4, 4):
                    self.assertEqual(self.__cell(row, col).possible_values(), self.ALL_VALUES - {5})

    def test_setting_value_leaves_other_cells_unchanged(self):
        self.__cell(4, 4).set(5)
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if not self.__is_affected_by(row, col, 4, 4):
                    self.assertEqual(self.__cell(row, col).possible_values(), self.ALL_VALUES)

    def test_deleting_value_gives_it_back_to_row_column_and_box(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 4).set(None)
        self.__assert_all_cells_have_all_values()

    def test_changing_value_gives_old_value_back_and_removes_new_one(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 4).set(7)
        self.assertEqual(self.__cell(4, 0).possible_values(), self.ALL_VALUES - {7})
        self.assertEqual(self.__cell(4, 4).possible_values(), set())

    def test_deleted_value_stays_blocked_where_a_duplicate_still_holds_it(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.__cell(4, 0).set(None)
        self.assertNotIn(5, self.__cell(4, 8).possible_values())
        self.assertNotIn(5, self.__cell(4, 0).possible_values())
        self.assertIn(5, self.__cell(0, 0).possible_values())

    def test_emptied_cell_regains_only_values_not_held_by_related_cells(self):
        self.__cell(0, 0).set(3)
        self.__cell(4, 8).set(5)
        self.__cell(4, 0).set(9)
        self.__cell(4, 0).set(None)
        self.assertEqual(self.__cell(4, 0).possible_values(), self.ALL_VALUES - {3, 5})

    def test_undo_gives_value_back(self):
        self.puzzle.play_()
        self.puzzle.selected_cell = (4, 4)
        with patch("cell.Display"):
            self.puzzle.value_(5)
            self.puzzle.undo_()
        self.__assert_all_cells_have_all_values()

    def test_rewind_undoes_entries_back_to_the_most_recent_guess(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(0, 0, 1)
            self.__enter(1, 1, 2, guess=True)
            self.__enter(2, 2, 3)
            self.__enter(3, 3, 4)
            self.__rewind()
        self.assertEqual([self.__cell(i, i).value() for i in range(4)], [1, 2, None, None])
        self.assertEqual(self.puzzle.selected_cell, (1, 1))

    def test_rewind_again_goes_back_to_the_previous_guess(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(0, 0, 1, guess=True)
            self.__enter(1, 1, 2)
            self.__enter(2, 2, 3, guess=True)
            self.__enter(3, 3, 4)
            self.__rewind()
            self.assertEqual([self.__cell(i, i).value() for i in range(4)], [1, 2, 3, None])
            self.__rewind()
            self.assertEqual([self.__cell(i, i).value() for i in range(4)], [1, None, None, None])
            self.assertEqual(self.puzzle.selected_cell, (0, 0))
            self.__rewind()
        self.assertEqual([self.__cell(i, i).value() for i in range(4)], [None, None, None, None])

    def test_rewind_without_a_guess_undoes_everything(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(0, 0, 1)
            self.__enter(1, 1, 2)
            self.__rewind()
        self.assertEqual([self.__cell(i, i).value() for i in range(2)], [None, None])

    def test_rewind_keeps_the_guess_shading_while_the_guess_stays(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(1, 1, 2, guess=True)
            self.__enter(2, 2, 3)
            self.__rewind()
            self.__enter(4, 4, 5)
        self.assertEqual(self.__cell(4, 4).attr(), (dict(level=10),))

    def test_rewind_through_a_guess_removes_its_shading(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(1, 1, 2, guess=True)
            self.__rewind()
            self.__enter(4, 4, 5)
        self.assertEqual(self.__cell(4, 4).attr(), ())

    def test_rewind_with_nothing_to_undo_warns_without_asking(self):
        self.puzzle.play_()
        with patch("display.Display.warn") as warn, patch("display.Display.confirm") as confirm:
            self.puzzle.rewind_()
        warn.assert_called_once()
        confirm.assert_not_called()

    def test_rewind_does_nothing_unless_confirmed(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(1, 1, 2, guess=True)
            self.__enter(2, 2, 3)
            with patch("display.Display.confirm", return_value=False):
                self.puzzle.rewind_()
        self.assertEqual(self.__cell(2, 2).value(), 3)

    def test_quit_stops_playing_when_confirmed(self):
        with patch("display.Display.confirm", return_value=True):
            self.puzzle.quit_()
        self.assertFalse(self.puzzle.is_playing)

    def test_quit_keeps_playing_unless_confirmed(self):
        with patch("display.Display.confirm", return_value=False):
            self.puzzle.quit_()
        self.assertTrue(self.puzzle.is_playing)

    def test_force_quit_stops_playing_without_asking(self):
        with patch("display.Display.confirm") as confirm:
            self.puzzle.force_quit_()
        self.assertFalse(self.puzzle.is_playing)
        confirm.assert_not_called()

    def test_play_is_refused_while_there_are_conflicts(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        with patch("display.Display.warn") as warn:
            self.puzzle.play_()
        self.assertIn("Resolve the conflicts before playing", warn.call_args.args[0])
        self.assertTrue(self.puzzle._initializing)

    def test_play_is_refused_at_a_dead_end(self):
        self.__fill_row(0, 0, range(1, 9))
        self.__cell(5, 8).set(9)
        with patch("display.Display.warn") as warn:
            self.puzzle.play_()
        self.assertIn("no possible values left", warn.call_args.args[0])
        self.assertEqual(self.puzzle.selected_cell, (0, 8))
        self.assertTrue(self.puzzle._initializing)

    def test_play_commands_are_refused_in_setup_mode(self):
        self.__fill_row(0, 0, range(1, 9))
        for command in (self.puzzle.undo_, self.puzzle.rewind_, self.puzzle.auto_, self.puzzle.next_):
            with patch("cell.Display"), patch("display.Display.warn") as warn, patch("display.Display.confirm") as confirm:
                command()
            self.assertIn("only while playing", warn.call_args.args[0])
            confirm.assert_not_called()
        self.assertIsNone(self.__cell(0, 8).value())

    def test_first_next_moves_to_the_cell_and_shows_why_without_filling_it(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"), patch("puzzle.echo") as echo:
            self.puzzle.next_()
            self.puzzle.display_status()
        self.assertIsNone(self.__cell(0, 8).value())
        self.assertEqual(self.puzzle.selected_cell, (0, 8))
        self.assertIn("Only 9 fits here", echo.call_args.args[0])

    def test_third_next_shows_the_following_move(self):
        self.__fill_row(4, 0, range(1, 9))
        self.__fill_row(2, 1, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            for _ in range(3):
                self.puzzle.next_()
        self.assertEqual(self.__cell(2, 0).value(), 9)
        self.assertIsNone(self.__cell(4, 8).value())
        self.assertEqual(self.puzzle.selected_cell, (4, 8))

    def test_another_command_between_next_presses_cancels_the_move(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.next_()
            self.puzzle.command_received("down_")
            self.puzzle.down_()
            self.puzzle.next_()
            self.assertIsNone(self.__cell(0, 8).value())
            self.assertEqual(self.puzzle.selected_cell, (0, 8))
            self.puzzle.next_()
        self.assertEqual(self.__cell(0, 8).value(), 9)

    def test_next_command_itself_does_not_cancel_the_move(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.command_received("next_")
            self.puzzle.next_()
            self.puzzle.command_received("next_")
            self.puzzle.next_()
        self.assertEqual(self.__cell(0, 8).value(), 9)

    def test_status_line_is_blank_when_there_is_nothing_to_report(self):
        self.assertEqual(self.__status(), Display.term.clear_eol)

    def test_render_draws_the_setup_commands_beside_the_puzzle(self):
        with patch("display.Display.draw_command_panel") as draw, patch("display.Display.clear_screen"):
            with patch("cell.Display"), patch("puzzle.echo"):
                self.puzzle.render()
        draw.assert_called_once_with("SETUP", Commands.panel())

    def test_switching_modes_redraws_the_commands(self):
        with patch("display.Display.draw_command_panel") as draw, patch("puzzle.echo"):
            self.puzzle.play_()
            self.assertEqual(draw.call_args.args[0], "PLAY")
            self.puzzle.init_()
            self.assertEqual(draw.call_args.args[0], "SETUP")

    def test_stop_warnings_repeat_on_every_next(self):
        self.__fill_row(0, 0, range(1, 9))
        self.__cell(4, 8).set(5)
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.__enter(4, 0, 5)
            self.puzzle.next_()
            self.puzzle.next_()
        self.assertEqual(warn.call_count, 2)
        self.assertIsNone(self.__cell(0, 8).value())

    def test_next_fills_in_a_cell_with_a_single_possible_value(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.next_()
            self.puzzle.next_()
        self.assertEqual(self.__cell(0, 8).value(), 9)
        self.assertEqual(self.__cell(0, 8).attr(), (DisplayAttrs.SOLVED,))
        self.assertEqual(self.puzzle.selected_cell, (0, 8))

    def test_next_picks_the_first_single_value_cell_left_to_right_top_to_bottom(self):
        self.__fill_row(4, 0, range(1, 9))
        self.__fill_row(2, 1, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.next_()
            self.puzzle.next_()
        self.assertEqual(self.__cell(2, 0).value(), 9)
        self.assertIsNone(self.__cell(4, 8).value())

    def test_next_can_be_undone(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.next_()
            self.puzzle.next_()
            self.puzzle.undo_()
        self.assertIsNone(self.__cell(0, 8).value())

    def test_undo_restores_a_solved_value_that_was_typed_over(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.next_()
            self.puzzle.next_()
            self.__enter(0, 8, 5)
            self.puzzle.undo_()
        self.assertEqual(self.__cell(0, 8).value(), 9)
        self.assertEqual(self.__cell(0, 8).attr(), (DisplayAttrs.SOLVED,))

    def test_next_after_a_guess_keeps_the_guess_shading(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(8, 0, 9, guess=True)
            self.puzzle.next_()
            self.puzzle.next_()
        self.assertEqual(self.__cell(0, 8).attr(), (DisplayAttrs.SOLVED, dict(level=10)))

    def test_next_refuses_while_there_are_conflicts(self):
        self.__fill_row(0, 0, range(1, 9))
        self.__cell(4, 8).set(5)
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.__enter(4, 0, 5)
            self.puzzle.next_()
        self.assertIn("conflicts", warn.call_args.args[0])
        self.assertIsNone(self.__cell(0, 8).value())

    def test_next_stops_at_a_dead_end(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.__enter(5, 8, 9)
            self.puzzle.next_()
        self.assertIn("try undoing until this square shows at least one possible value", warn.call_args.args[0])
        self.assertEqual(self.puzzle.selected_cell, (0, 8))

    def test_next_with_no_obvious_move_says_to_guess(self):
        self.puzzle.play_()
        with patch("display.Display.warn") as warn:
            self.puzzle.next_()
        self.assertIn("No obvious next move. You'll have to make a guess.", warn.call_args.args[0])

    def test_auto_makes_moves_until_none_is_obvious(self):
        self.__fill_row(4, 0, range(1, 9))
        self.__fill_row(2, 1, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.puzzle.auto_()
        self.assertEqual(self.__cell(2, 0).value(), 9)
        self.assertEqual(self.__cell(4, 8).value(), 9)
        self.assertEqual(self.__cell(4, 8).attr(), (DisplayAttrs.SOLVED,))
        self.assertEqual(self.puzzle.selected_cell, (4, 8))
        self.assertIn("No obvious next move. You'll have to make a guess.", warn.call_args.args[0])

    def test_auto_moves_are_undone_one_at_a_time(self):
        self.__fill_row(4, 0, range(1, 9))
        self.__fill_row(2, 1, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn"):
            self.puzzle.auto_()
            self.puzzle.undo_()
        self.assertEqual(self.__cell(2, 0).value(), 9)
        self.assertIsNone(self.__cell(4, 8).value())

    def test_auto_stops_at_a_dead_end(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.__enter(5, 8, 9)
            self.puzzle.auto_()
        self.assertIn("try undoing until this square shows at least one possible value", warn.call_args.args[0])
        self.assertEqual(self.puzzle.selected_cell, (0, 8))

    def test_auto_refuses_while_there_are_conflicts(self):
        self.__fill_row(0, 0, range(1, 9))
        self.__cell(4, 8).set(5)
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.__enter(4, 0, 5)
            self.puzzle.auto_()
        self.assertIn("conflicts", warn.call_args.args[0])
        self.assertIsNone(self.__cell(0, 8).value())

    def test_auto_cancels_the_move_pointed_out_by_next(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn"), patch("puzzle.echo") as echo:
            self.puzzle.next_()
            self.puzzle.command_received("auto_")
            self.puzzle.auto_()
            self.puzzle.display_status()
        self.assertEqual(echo.call_args.args[0], Display.term.clear_eol)

    def test_status_reports_solved_once_the_last_value_is_entered(self):
        self.__fill_solution(skip=(8, 8))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(8, 8, self.__solution(8, 8))
        self.assertIn("solved", self.__status())

    def test_status_reports_completion_until_the_next_command(self):
        self.__fill_solution(skip=(8, 8))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(8, 8, self.__solution(8, 8))
        self.assertIn("solved", self.__status())
        self.puzzle.command_received("up_")
        self.assertEqual(self.__status(), Display.term.clear_eol)

    def test_status_reports_errors_when_complete_with_conflicts(self):
        self.__fill_solution()
        self.puzzle.play_()
        self.puzzle.command_received("value_")
        with patch("cell.Display"):
            self.__enter(0, 0, self.__solution(0, 1))
        self.assertIn("errors", self.__status())
        self.assertEqual(self.__cell(0, 0).value(), self.__solution(0, 1))

    def test_status_reports_solved_again_once_errors_are_fixed(self):
        self.__fill_solution()
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.command_received("value_")
            self.__enter(0, 0, self.__solution(0, 1))
            self.__status()
            self.puzzle.command_received("value_")
            self.__enter(0, 0, self.__solution(0, 0))
        self.assertIn("solved", self.__status())

    def test_status_reports_completion_again_after_undo_empties_a_cell(self):
        self.__fill_solution(skip=(8, 8))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.__enter(8, 8, self.__solution(8, 8))
            self.__status()
            self.puzzle.command_received("undo_")
            self.puzzle.undo_()
            self.assertEqual(self.__status(), Display.term.clear_eol)
            self.puzzle.command_received("value_")
            self.__enter(8, 8, self.__solution(8, 8))
        self.assertIn("solved", self.__status())

    def test_status_reports_no_completion_while_initializing(self):
        self.__fill_solution()
        self.assertEqual(self.__status(), Display.term.clear_eol)

    def test_next_on_a_solved_puzzle_warns_it_is_already_solved(self):
        self.__fill_solution()
        self.puzzle.play_()
        with patch("display.Display.warn") as warn:
            self.puzzle.next_()
        self.assertIn("already solved", warn.call_args.args[0])

    def test_auto_on_a_complete_puzzle_with_errors_says_to_undo_or_change_values(self):
        self.__fill_solution()
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.__enter(0, 0, self.__solution(0, 1))
            self.puzzle.auto_()
        self.assertIn("undo or change values", warn.call_args.args[0])

    def test_auto_filling_the_last_cell_ends_without_a_warning(self):
        self.__fill_solution(skip=(8, 8))
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.puzzle.auto_()
        self.assertEqual(self.__cell(8, 8).value(), self.__solution(8, 8))
        warn.assert_not_called()

    def test_guess_on_a_given_is_refused_without_deepening_the_shading(self):
        with patch("cell.Display"), patch("display.Display.warn"):
            self.__enter(0, 0, 5)
            self.puzzle.play_()
            self.__enter(0, 0, 3, guess=True)
            self.__enter(1, 1, 4)
        self.assertEqual(self.__cell(1, 1).attr(), ())

    def test_restore_brings_back_the_board_mode_and_cursor(self):
        self.__play_a_few_moves()
        restored = self.__restored_puzzle()
        self.assertFalse(restored._initializing)
        self.assertEqual(restored.selected_cell, (2, 2))
        for row, col in ((0, 0), (0, 1), (1, 1), (2, 2)):
            self.assertEqual(self.__cell_of(restored, row, col).value(), self.__cell(row, col).value())
            self.assertEqual(self.__cell_of(restored, row, col).attr(), self.__cell(row, col).attr())

    def test_restored_moves_can_be_undone(self):
        self.__play_a_few_moves()
        restored = self.__restored_puzzle()
        with patch("cell.Display"):
            restored.undo_()
            restored.undo_()
        self.assertIsNone(self.__cell_of(restored, 2, 2).value())
        self.assertIsNone(self.__cell_of(restored, 1, 1).value())
        self.assertEqual(self.__cell_of(restored, 0, 1).value(), 2)

    def test_restore_in_setup_mode_stays_in_setup_mode(self):
        with patch("cell.Display"):
            self.__enter(0, 0, 1)
        restored = self.__restored_puzzle()
        self.assertTrue(restored._initializing)
        self.assertEqual(self.__cell_of(restored, 0, 0).attr(), (DisplayAttrs.INITIAL,))

    def test_cell_already_holding_the_value_is_marked_conflicted(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.assertIn(DisplayAttrs.CONFLICTED, self.__cell(4, 4).attr())

    def test_unrelated_cell_holding_the_value_is_not_marked(self):
        self.__cell(0, 0).set(5)
        self.__cell(4, 4).set(5)
        self.assertNotIn(DisplayAttrs.CONFLICTED, self.__cell(0, 0).attr())

    def test_deleting_conflicting_value_clears_conflicted_mark(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.__cell(4, 0).set(None)
        self.assertEqual(self.__cell(4, 4).attr(), ())

    def test_deleting_conflicted_value_clears_conflicting_mark(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.__cell(4, 4).set(None)
        self.assertEqual(self.__cell(4, 0).attr(), ())

    def test_replacing_conflicting_value_clears_conflicted_mark(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.__cell(4, 0).set(7)
        self.assertEqual(self.__cell(4, 4).attr(), ())

    def test_cell_stays_conflicted_while_another_clash_remains(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.__cell(0, 4).set(5)
        self.__cell(4, 0).set(None)
        self.assertIn(DisplayAttrs.CONFLICTED, self.__cell(4, 4).attr())

    def test_undo_clears_conflict_marks(self):
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.selected_cell = (4, 4)
            self.puzzle.value_(5)
            self.puzzle.selected_cell = (4, 0)
            self.puzzle.value_(5)
            self.puzzle.undo_()
        self.assertEqual(self.__cell(4, 4).attr(), ())

    def test_value_already_in_row_is_conflicting(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.assertIn(DisplayAttrs.CONFLICTING, self.__cell(4, 0).attr())

    def test_value_already_in_column_is_conflicting(self):
        self.__cell(4, 4).set(5)
        self.__cell(0, 4).set(5)
        self.assertIn(DisplayAttrs.CONFLICTING, self.__cell(0, 4).attr())

    def test_value_already_in_box_is_conflicting(self):
        self.__cell(4, 4).set(5)
        self.__cell(3, 3).set(5)
        self.assertIn(DisplayAttrs.CONFLICTING, self.__cell(3, 3).attr())

    def test_value_directly_above_in_another_block_is_conflicting(self):
        self.__cell(0, 8).set(7)
        self.__cell(6, 8).set(7)
        self.assertIn(DisplayAttrs.CONFLICTING, self.__cell(6, 8).attr())

    def test_value_in_block_above_but_not_in_same_column_is_not_conflicting(self):
        self.__cell(0, 6).set(5)
        self.__cell(6, 8).set(5)
        self.assertNotIn(DisplayAttrs.CONFLICTING, self.__cell(6, 8).attr())

    def test_replacing_value_with_unused_value_is_not_conflicting(self):
        self.__cell(4, 4).set(3)
        self.__cell(4, 4).set(7)
        self.assertNotIn(DisplayAttrs.CONFLICTING, self.__cell(4, 4).attr())

    def test_replacing_conflicting_value_with_unused_value_clears_conflict(self):
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.__cell(4, 0).set(7)
        self.assertNotIn(DisplayAttrs.CONFLICTING, self.__cell(4, 0).attr())

    # Private functions

    def __cell(self, row, col):
        """The cell at a position on the puzzle's board"""
        return self.__cell_of(self.puzzle, row, col)

    def __is_affected_by(self, row, col, origin_row, origin_col) -> bool:
        same_box = row // 3 == origin_row // 3 and col // 3 == origin_col // 3
        return row == origin_row or col == origin_col or same_box

    def __assert_all_cells_have_all_values(self):
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                self.assertEqual(self.__cell(row, col).possible_values(), self.ALL_VALUES, (row, col))

    def __enter(self, row, col, value, guess=False):
        self.puzzle.selected_cell = (row, col)
        self.puzzle.value_(value, guess)

    def __status(self) -> str:
        """Show the status line and return what it shows"""
        with patch("puzzle.echo") as echo:
            self.puzzle.display_status()
        return echo.call_args.args[0]

    def __play_a_few_moves(self):
        """A given, then a typed value, a guess and a value after the guess, ending at (2, 2)"""
        with patch("cell.Display"):
            self.__enter(0, 0, 1)
            self.puzzle.play_()
            self.__enter(0, 1, 2)
            self.__enter(1, 1, 3, guess=True)
            self.__enter(2, 2, 4)

    def __restored_puzzle(self):
        """A new puzzle with this puzzle's saved state restored into it"""
        saved = self.puzzle.saved_state()
        with patch("display.Display.validate_screen_size"):
            restored = Puzzle(Board3x3())
        with patch("cell.Display"), patch.object(restored, "render"):
            restored.restore(saved)
        return restored

    def __cell_of(self, puzzle, row, col):
        """Access to the puzzle's private board"""
        return puzzle._Puzzle__board.cell(row, col)

    def __rewind(self):
        with patch("display.Display.confirm", return_value=True):
            self.puzzle.rewind_()

    def __fill_row(self, row, start_col, values):
        for col, value in enumerate(values, start_col):
            self.__cell(row, col).set(value)

    def __fill_solution(self, skip=None):
        """Fill every cell, except the skipped (row, col), with a valid solution"""
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                (row, col) == skip or self.__cell(row, col).set(self.__solution(row, col))

    def __solution(self, row, col) -> int:
        return (row * 3 + row // 3 + col) % self.SIZE + 1


if __name__ == "__main__":
    main()
