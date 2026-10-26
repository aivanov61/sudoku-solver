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

from display_attrs import DisplayAttrs
from puzzle_3x3 import Puzzle3x3


class TestPuzzle3x3(TestCase):
    SIZE = 9
    ALL_VALUES = set(range(1, SIZE + 1))

    def setUp(self):
        with patch("display.Display.validate_screen_size"):
            self.puzzle = Puzzle3x3()
        return super().setUp()

    def __cell(self, row, col):
        """Access to the puzzle's private cell lookup"""
        return self.puzzle._Puzzle3x3__cell(row, col)

    def __is_affected_by(self, row, col, origin_row, origin_col) -> bool:
        same_box = row // 3 == origin_row // 3 and col // 3 == origin_col // 3
        return row == origin_row or col == origin_col or same_box

    def test_cell_returns_cell_at_puzzle_position(self):
        cell = self.__cell(4, 7)
        self.assertEqual((cell.row, cell.col), (4, 7))

    def test_cells_in_row_or_col_yields_each_cell_in_that_row_and_col_once(self):
        cells = list(self.puzzle.cells_in_row_or_col(4, 4))
        positions = [(cell.row, cell.col) for cell in cells]
        self.assertEqual(len(positions), len(set(positions)))
        self.assertEqual(set(positions), {(4, i) for i in range(self.SIZE)} | {(i, 4) for i in range(self.SIZE)})

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

    def __rewind(self):
        with patch("display.Display.confirm", return_value=True):
            self.puzzle.rewind_()

    def test_next_fills_in_a_cell_with_a_single_possible_value(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
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
        self.assertEqual(self.__cell(2, 0).value(), 9)
        self.assertIsNone(self.__cell(4, 8).value())

    def test_next_can_be_undone(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
            self.puzzle.next_()
            self.puzzle.undo_()
        self.assertIsNone(self.__cell(0, 8).value())

    def test_undo_restores_a_solved_value_that_was_typed_over(self):
        self.__fill_row(0, 0, range(1, 9))
        self.puzzle.play_()
        with patch("cell.Display"):
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
        self.assertEqual(self.__cell(0, 8).attr(), (DisplayAttrs.SOLVED, dict(level=10)))

    def test_next_refuses_while_there_are_conflicts(self):
        self.__fill_row(0, 0, range(1, 9))
        self.__cell(4, 4).set(5)
        self.__cell(4, 0).set(5)
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.puzzle.next_()
        self.assertIn("conflicts", warn.call_args.args[0])
        self.assertIsNone(self.__cell(0, 8).value())

    def test_next_stops_at_a_dead_end(self):
        self.__fill_row(0, 0, range(1, 9))
        self.__cell(5, 8).set(9)
        self.puzzle.play_()
        with patch("cell.Display"), patch("display.Display.warn") as warn:
            self.puzzle.next_()
        self.assertIn("try undoing until this square shows at least one possible value", warn.call_args.args[0])
        self.assertEqual(self.puzzle.selected_cell, (0, 8))

    def test_next_with_no_obvious_move_says_to_guess(self):
        self.puzzle.play_()
        with patch("display.Display.warn") as warn:
            self.puzzle.next_()
        self.assertIn("No obvious next move. You'll have to make a guess.", warn.call_args.args[0])

    def __fill_row(self, row, start_col, values):
        for col, value in enumerate(values, start_col):
            self.__cell(row, col).set(value)

    def __enter(self, row, col, value, guess=False):
        self.puzzle.selected_cell = (row, col)
        self.puzzle.value_(value, guess)

    def __assert_all_cells_have_all_values(self):
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                self.assertEqual(self.__cell(row, col).possible_values(), self.ALL_VALUES, (row, col))

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


if __name__ == "__main__":
    main()
