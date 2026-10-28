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

from game.cell import Cell
from game.cell_attrs import CellAttrs
from game.house import House
from game.marks_setting import MarksSetting


class TestCell(TestCase):
    MAX_VALUE = 10

    def setUp(self):
        self.__setup_parent()
        self.cell = Cell(self.parent, **self.x())
        return super().setUp()

    def x(self):
        return {"row": 0, "col": 0}

    # Values

    def test_cell_initial_value_is_not_set(self):
        self.assertIsNone(self.cell.value())

    def test_cell_value_can_be_set(self):
        self.cell.set(8)
        self.assertEqual(self.cell.value(), 8)

    def test_cell_value_has_limits_set_by_parent(self):
        self.assertRaises(ValueError, self.cell.set, self.MAX_VALUE)

    def test_cell_clears_its_possible_values_when_value_is_set(self):
        self.cell.set(8)
        self.assertEqual(self.cell.possible_values(), set())

    # Possible values

    def test_cell_new_value_is_removed_from_related_cells(self):
        related = self.__related_cell()
        self.cell.set(8)
        related.remove_possible.assert_called_once_with(8)

    def test_cell_changing_value_gives_old_value_back_to_related_cells(self):
        related = self.__related_cell()
        self.cell.set(8)
        self.cell.set(4)
        related.add_possible.assert_called_once_with(8)

    def test_cell_emptied_cell_regains_values_not_held_by_related_cells(self):
        self.__related_cell(value=3)
        self.cell.set(8)
        self.cell.set(None)
        self.assertEqual(self.cell.possible_values(), set(range(1, self.MAX_VALUE)) - {3})

    def test_cell_add_possible_restores_value(self):
        self.cell.remove_possible(5)
        self.cell.add_possible(5)
        self.assertIn(5, self.cell.possible_values())

    def test_cell_add_possible_ignores_value_held_by_related_cell(self):
        self.cell.remove_possible(5)
        self.__related_cell(value=5)
        self.cell.add_possible(5)
        self.assertNotIn(5, self.cell.possible_values())

    def test_cell_add_possible_ignores_value_when_cell_has_a_value(self):
        self.cell.set(8)
        self.cell.add_possible(5)
        self.assertEqual(self.cell.possible_values(), set())

    def test_cell_remove_possible_updates_solver(self):
        self.cell.remove_possible(5)
        self.assertNotIn(5, self.cell.possible_values())

    # Changes

    def test_cell_reports_a_change_when_a_possible_value_is_added_back(self):
        self.cell.remove_possible(5)
        self.parent.cell_changed.reset_mock()
        self.cell.add_possible(5)
        self.parent.cell_changed.assert_called_once_with(self.cell)

    def test_cell_reports_no_change_when_added_value_was_already_possible(self):
        self.cell.add_possible(5)
        self.parent.cell_changed.assert_not_called()

    def test_cell_reports_a_change_when_a_possible_value_is_removed(self):
        self.cell.remove_possible(5)
        self.parent.cell_changed.assert_called_once_with(self.cell)

    def test_cell_reports_no_change_when_removed_value_was_not_possible(self):
        self.cell.remove_possible(5)
        self.parent.cell_changed.reset_mock()
        self.cell.remove_possible(5)
        self.parent.cell_changed.assert_not_called()

    def test_cell_reports_a_change_when_its_value_changes(self):
        self.cell.set(8)
        self.parent.cell_changed.reset_mock()
        self.cell.set(4)
        self.parent.cell_changed.assert_called_once_with(self.cell)

    def test_cell_reports_a_change_when_its_attributes_change(self):
        self.cell.set(8)
        self.parent.cell_changed.reset_mock()
        self.cell.set(8, (CellAttrs.GUESS,))
        self.parent.cell_changed.assert_called_once_with(self.cell)

    def test_cell_reports_no_change_when_set_to_what_it_already_holds(self):
        self.cell.set(8, (CellAttrs.GUESS,))
        self.parent.cell_changed.reset_mock()
        self.cell.set(8, (CellAttrs.GUESS,))
        self.parent.cell_changed.assert_not_called()

    # Conflicts

    def test_cell_value_is_conflicting_when_a_related_cell_holds_it(self):
        self.__related_cell(value=8)
        self.cell.set(8)
        self.parent.related_cells.assert_called_with(0, 0)
        self.assertIn(CellAttrs.CONFLICTING, self.cell.attr())

    def test_cell_value_is_not_conflicting_when_no_related_cell_holds_it(self):
        self.cell.set(8)
        self.assertNotIn(CellAttrs.CONFLICTING, self.cell.attr())

    def test_cell_re_entering_same_value_keeps_it_conflicting(self):
        self.__related_cell(value=8)
        self.cell.set(8)
        self.cell.set(8)
        self.assertIn(CellAttrs.CONFLICTING, self.cell.attr())

    def test_cell_new_value_marks_related_cells_conflicted(self):
        related = self.__related_cell()
        self.cell.set(8)
        related.mark_conflicted.assert_called_once_with(8)

    def test_cell_changing_value_clears_resolved_conflicts_of_related_cells(self):
        related = self.__related_cell()
        self.cell.set(8)
        self.cell.set(4)
        related.clear_resolved_conflict.assert_called_once_with(8)

    def test_cell_mark_conflicted_marks_cell_holding_the_value(self):
        self.cell.set(8, (CellAttrs.INITIAL,))
        self.parent.cell_changed.reset_mock()
        self.cell.mark_conflicted(8)
        self.assertEqual(self.cell.attr(), (CellAttrs.INITIAL, CellAttrs.CONFLICTED))
        self.parent.cell_changed.assert_called_once_with(self.cell)

    def test_cell_mark_conflicted_ignores_other_values(self):
        self.cell.set(8)
        self.parent.cell_changed.reset_mock()
        self.cell.mark_conflicted(5)
        self.assertNotIn(CellAttrs.CONFLICTED, self.cell.attr())
        self.parent.cell_changed.assert_not_called()

    def test_cell_mark_conflicted_does_not_mark_a_conflicting_cell_again(self):
        self.__related_cell(value=8)
        self.cell.set(8)
        self.cell.mark_conflicted(8)
        self.assertEqual(self.cell.attr(), (CellAttrs.CONFLICTING,))

    def test_cell_clear_resolved_conflict_clears_marks_when_no_related_cell_holds_value(self):
        related = self.__related_cell(value=8)
        self.cell.set(8, (CellAttrs.GUESS,))
        self.cell.mark_conflicted(8)
        related.value.return_value = None
        self.parent.cell_changed.reset_mock()
        self.cell.clear_resolved_conflict(8)
        self.assertEqual(self.cell.attr(), (CellAttrs.GUESS,))
        self.parent.cell_changed.assert_called_once_with(self.cell)

    def test_cell_clear_resolved_conflict_keeps_mark_while_a_related_cell_holds_value(self):
        self.cell.set(8)
        self.cell.mark_conflicted(8)
        self.__related_cell(value=8)
        self.cell.clear_resolved_conflict(8)
        self.assertIn(CellAttrs.CONFLICTED, self.cell.attr())

    def test_cell_is_marked_in_conflict_when_conflicting(self):
        self.__related_cell(value=8)
        self.cell.set(8)
        self.assertTrue(self.cell.is_marked_in_conflict())

    def test_cell_is_not_marked_in_conflict_by_default(self):
        self.cell.set(8)
        self.assertFalse(self.cell.is_marked_in_conflict())

    # Questions from the solver

    def test_cell_single_possible_value_comes_from_solver(self):
        for value in range(1, self.MAX_VALUE - 1):
            self.cell.remove_possible(value)
        self.assertEqual(self.cell.single_possible_value(), self.MAX_VALUE - 1)

    def test_cell_is_dead_end_when_empty_with_no_possible_values(self):
        for value in range(1, self.MAX_VALUE):
            self.cell.remove_possible(value)
        self.assertTrue(self.cell.is_dead_end())

    def test_cell_with_a_value_is_not_a_dead_end(self):
        self.cell.set(8)
        self.assertFalse(self.cell.is_dead_end())

    def test_cell_hidden_single_is_a_value_that_can_go_nowhere_else_in_its_box(self):
        box = self.__house(House.BOX, all_but={4})
        self.assertEqual(self.cell.hidden_single(), (4, box))

    def test_cell_hidden_single_can_be_in_its_row_or_column(self):
        self.__house(House.BOX, all_but=set())
        self.__house(House.ROW, all_but=set())
        column = self.__house(House.COLUMN, all_but={5})
        self.assertEqual(self.cell.hidden_single(), (5, column))

    def test_cell_hidden_single_looks_in_its_box_before_its_row_and_column(self):
        box = self.__house(House.BOX, all_but={7})
        self.__house(House.ROW, all_but={2})
        self.assertEqual(self.cell.hidden_single(), (7, box))

    def test_cell_hidden_single_is_the_lowest_such_value_in_a_house(self):
        box = self.__house(House.BOX, all_but={6, 4})
        self.assertEqual(self.cell.hidden_single(), (4, box))

    def test_cell_has_no_hidden_single_while_every_value_has_another_place(self):
        self.__house(House.BOX, all_but=set())
        self.__house(House.ROW, all_but=set())
        self.assertIsNone(self.cell.hidden_single())

    def test_cell_with_a_value_has_no_hidden_single(self):
        self.cell.set(8)
        self.__house(House.BOX, all_but={4})
        self.assertIsNone(self.cell.hidden_single())

    def test_cell_unplaceable_value_is_one_its_house_lacks_with_no_place_left(self):
        self.cell.remove_possible(4)
        self.__house(House.BOX, all_but=set())
        row = self.__house(House.ROW, all_but={4})
        self.assertEqual(self.cell.unplaceable_value(), (4, row))

    def test_cell_unplaceable_value_looks_in_its_box_before_its_row_and_column(self):
        self.cell.remove_possible(4)
        self.cell.remove_possible(6)
        box = self.__house(House.BOX, all_but={6})
        self.__house(House.ROW, all_but={4})
        self.assertEqual(self.cell.unplaceable_value(), (6, box))

    def test_cell_has_no_unplaceable_value_while_every_value_has_a_place(self):
        self.cell.remove_possible(4)
        self.__house(House.BOX, all_but=set())
        self.assertIsNone(self.cell.unplaceable_value())

    def test_cell_with_a_value_has_no_unplaceable_value(self):
        self.cell.set(8)
        self.__house(House.BOX, all_but={4})
        self.assertIsNone(self.cell.unplaceable_value())

    # Tags

    def test_cell_is_not_tagged_at_first(self):
        self.assertFalse(self.cell.is_tagged())

    def test_cell_tag_can_be_set_and_cleared(self):
        self.cell.set_tagged(True)
        self.assertTrue(self.cell.is_tagged())
        self.cell.set_tagged(False)
        self.assertFalse(self.cell.is_tagged())

    def test_cell_keeps_its_tag_through_a_value_and_back(self):
        self.cell.set_tagged(True)
        self.cell.set(8)
        self.cell.set(None)
        self.assertTrue(self.cell.is_tagged())

    def test_cell_reports_a_change_only_when_its_tag_changes(self):
        self.cell.set_tagged(True)
        self.cell.set_tagged(True)
        self.parent.cell_changed.assert_called_once_with(self.cell)

    # Must-be marks

    def test_cell_has_no_marks_without_a_setting(self):
        self.__counted_house(House.BOX, {4: 1})
        self.cell.refresh_marks(None)
        self.assertEqual(self.cell.marks(), ())

    def test_an_untagged_cell_shows_snyder_marks_only_for_the_whole_puzzle(self):
        self.__counted_house(House.BOX, {4: 2})
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY))
        self.assertEqual(self.cell.marks(), ())
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True))
        self.assertEqual(self.cell.marks(), (4,))

    def test_a_tagged_cell_shows_its_single_possible_value(self):
        self.__leave_possible({6})
        self.assertEqual(self.__tagged_marks(), (6,))

    def test_a_tagged_cell_shows_its_hidden_single(self):
        self.__counted_house(House.BOX, {4: 1})
        self.assertEqual(self.__tagged_marks(), (4,))

    def test_a_tagged_cell_shows_its_possible_values_but_those_forced_into_related_cells(self):
        self.__leave_possible({3, 5, 7})
        self.__related_forced(3, None)
        self.assertEqual(self.__tagged_marks(), (5, 7))

    def test_a_tagged_cell_shows_what_it_must_be_even_for_the_whole_puzzle(self):
        self.__leave_possible({3, 5})
        self.__counted_house(House.BOX, {3: 2, 5: 2})
        self.__related_forced(3)
        self.assertEqual(self.__tagged_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True)), (5,))

    def test_a_tagged_cell_with_a_value_shows_nothing(self):
        self.cell.set(8)
        self.assertEqual(self.__tagged_marks(), ())

    def test_forced_value_is_the_single_possible_value_or_else_the_hidden_single(self):
        self.__counted_house(House.BOX, {4: 1})
        self.assertEqual(self.cell.forced_value(), 4)
        self.__leave_possible({6})
        self.assertEqual(self.cell.forced_value(), 6)

    def test_forced_value_is_none_when_nothing_forces_one(self):
        self.__counted_house(House.BOX, {4: 2})
        self.assertIsNone(self.cell.forced_value())

    def test_forced_value_is_none_for_a_cell_with_a_value(self):
        self.cell.set(8)
        self.assertIsNone(self.cell.forced_value())

    def test_cell_marks_values_with_few_enough_places_in_its_box(self):
        self.__counted_house(House.BOX, {4: 2, 6: 1, 7: 3})
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True))
        self.assertEqual(self.cell.marks(), (4, 6))

    def test_cell_marks_from_rows_and_columns_only_when_asked_to(self):
        self.__counted_house(House.BOX, {})
        self.__counted_house(House.ROW, {5: 2})
        self.__counted_house(House.COLUMN, {3: 2, 5: 2})
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True))
        self.assertEqual(self.cell.marks(), ())
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.EVERY_HOUSE, True))
        self.assertEqual(self.cell.marks(), (3, 5))

    def test_cell_marks_only_its_possible_values(self):
        self.cell.remove_possible(4)
        self.__counted_house(House.BOX, {4: 1})
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True))
        self.assertEqual(self.cell.marks(), ())

    def test_cell_with_a_value_has_no_marks(self):
        self.cell.set(8)
        self.__counted_house(House.BOX, {8: 1})
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True))
        self.assertEqual(self.cell.marks(), ())

    def test_cell_reports_a_change_only_when_its_marks_change(self):
        self.__counted_house(House.BOX, {4: 2})
        self.cell.refresh_marks(MarksSetting(2, MarksSetting.BOX_ONLY, True))
        self.cell.refresh_marks(MarksSetting(3, MarksSetting.BOX_ONLY, True))
        self.parent.cell_changed.assert_called_once_with(self.cell)

    # Private functions

    def __setup_parent(self):
        """
        Mock 'parent' needs to provide:
        1. values() - range of legal values
        2. related_cells() - the cells in the same block, row or column (none until a test adds some)
        3. houses_of() - the cell's box, row and column (none until a test adds some)
        4. cell_changed(cell) - hears of every change to the cell
        """
        self.parent = MagicMock()
        self.parent.values.return_value = range(1, self.MAX_VALUE)
        self.parent.related_cells.return_value = []
        self.parent.houses_of.return_value = []

    def __related_cell(self, value=None):
        """Add a mock related cell holding the value"""
        cell = MagicMock()
        cell.value.return_value = value
        self.parent.related_cells.return_value.append(cell)
        return cell

    def __leave_possible(self, values):
        for value in set(self.parent.values()) - values:
            self.cell.remove_possible(value)

    def __related_forced(self, *values):
        """Make the cell's related cells, one for each value forced into it (None for none)"""
        related = []
        for value in values:
            cell = MagicMock()
            cell.forced_value.return_value = value
            related.append(cell)
        self.parent.related_cells.return_value = related

    def __tagged_marks(self, setting=MarksSetting()) -> tuple:
        """Tag the cell and return the marks it shows with the setting"""
        self.cell.set_tagged(True)
        self.cell.refresh_marks(setting)
        return self.cell.marks()

    def __counted_house(self, kind, counts):
        """Add a house of this cell where each value in counts has that many places, and any other value 9"""
        house = MagicMock(kind=kind)
        house.places.side_effect = lambda value: [self.cell] * counts.get(value, 9)
        self.parent.houses_of.return_value.append(house)

    def __house(self, kind, all_but):
        """Add a house of this cell and one other, where every value but those in all_but can also go"""
        other = MagicMock()
        other.value.return_value = None
        other.possible_values.return_value = set(self.parent.values()) - all_but
        house = House(kind, [self.cell, other])
        self.parent.houses_of.return_value.append(house)
        return house


if __name__ == "__main__":
    main()
