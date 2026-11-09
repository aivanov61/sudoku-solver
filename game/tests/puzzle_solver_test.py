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
from unittest.mock import MagicMock

from game.eliminations_setting import EliminationsSetting
from game.puzzle_solver import PuzzleSolver
from game.rules.rule import Elimination, Move, Outcome, Rule
from game.user_interface import MessageKind


class TestPuzzleSolver(TestCase):
    def setUp(self):
        self.consulted = []
        self.puzzle = MagicMock()
        self.puzzle.is_complete.return_value = False
        return super().setUp()

    def test_move_of_the_first_rule_that_has_one_is_found(self):
        move = Move(Outcome.MOVED, "hint", MagicMock(), 3)
        solver = PuzzleSolver(self.puzzle, [self.__rule("a", None), self.__rule("b", move)])
        self.assertIs(solver.find_move(), move)

    def test_rules_after_the_first_with_a_move_are_not_consulted(self):
        stop = Move(Outcome.STOPPED, "warning")
        PuzzleSolver(self.puzzle, [self.__rule("a", stop), self.__rule("b", stop)]).find_move()
        self.assertEqual(self.consulted, ["a"])

    def test_no_move_when_no_rule_has_one(self):
        solver = PuzzleSolver(self.puzzle, [self.__rule("a", None), self.__rule("b", None)])
        self.assertIsNone(solver.find_move())
        self.assertEqual(self.consulted, ["a", "b"])

    def test_ruled_out_gathers_every_rules_eliminations(self):
        first, second = MagicMock(), MagicMock()

        def ruling_out(eliminations):
            class EliminatingRule(Rule):
                def find(self, puzzle):
                    return None

                def eliminations(self, puzzle):
                    return eliminations

            return EliminatingRule

        rules = [ruling_out({(first, 4): "why"}), ruling_out({(second, 5): "why not"})]
        self.assertEqual(PuzzleSolver(self.puzzle, rules).ruled_out(), {(first, 4): "why", (second, 5): "why not"})

    def test_nothing_is_removed_at_no_level(self):
        rule = self.__eliminating("intersections", lambda ruled_out: {(MagicMock(), 4): "why"})
        self.assertEqual(PuzzleSolver(self.puzzle, [rule]).removed(EliminationsSetting()), {})

    def test_removed_cascades_in_the_order_found_until_nothing_more_is_ruled_out(self):
        first, second = MagicMock(), MagicMock()
        after_first = self.__eliminating("intersections", lambda ruled_out: {(second, 5): "b"} if (first, 4) in ruled_out else {})
        always = self.__eliminating("intersections", lambda ruled_out: {(first, 4): "a"})
        removed = PuzzleSolver(self.puzzle, [after_first, always]).removed(EliminationsSetting("intersections"))
        self.assertEqual(list(removed.items()), [((first, 4), "a"), ((second, 5), "b")])

    def test_removed_keeps_the_first_reason_for_a_value(self):
        cell = MagicMock()
        rules = [
            self.__eliminating("intersections", lambda ruled_out: {(cell, 4): "first"}),
            self.__eliminating("intersections", lambda ruled_out: {(cell, 4): "second"}),
        ]
        self.assertEqual(PuzzleSolver(self.puzzle, rules).removed(EliminationsSetting("intersections")), {(cell, 4): "first"})

    def test_removed_leaves_out_rules_the_level_does_not_include(self):
        rule = self.__eliminating(None, lambda ruled_out: {(MagicMock(), 4): "why"})
        self.assertEqual(PuzzleSolver(self.puzzle, [rule]).removed(EliminationsSetting("intersections")), {})

    def test_everything_ruled_out_cascades_through_the_rules_of_every_level(self):
        first, second = MagicMock(), MagicMock()
        after_first = self.__eliminating(None, lambda ruled_out: {(second, 5): "b"} if (first, 4) in ruled_out else {})
        always = self.__eliminating("pairs", lambda ruled_out: {(first, 4): "a"})
        solver = PuzzleSolver(self.puzzle, [after_first, always])
        self.assertEqual(list(solver.everything_ruled_out().items()), [((first, 4), "a"), ((second, 5), "b")])

    def test_removal_steps_are_the_cells_removals_and_what_they_rely_on_oldest_first(self):
        first, other, second = MagicMock(), MagicMock(), MagicMock()
        steps = self.__steps_for(second, {(first, 4): "a", (other, 6): "c"}, {(second, 5): ("b", ((first, 4),))})
        self.assertEqual([step.cell for step in steps], [first, second])
        self.assertEqual(
            [step.message.text for step in steps],
            ["(1/2) 4 is ruled out here: a [rule] ", "(2/2) 5 is ruled out here: b (see step 1) [rule] "],
        )

    def test_removal_steps_follow_a_chain_back_through_every_step(self):
        first, second, third = MagicMock(), MagicMock(), MagicMock()
        steps = self.__steps_for(third, {(first, 4): "a"}, {(second, 4): ("b", ((first, 4),))}, {(third, 4): ("c", ((second, 4),))})
        self.assertEqual([step.cell for step in steps], [first, second, third])

    def test_a_removal_step_names_every_step_it_relies_on(self):
        first, second, third = MagicMock(), MagicMock(), MagicMock()
        steps = self.__steps_for(third, {(first, 4): "a", (second, 4): "b"}, {(third, 4): ("c", ((first, 4), (second, 4)))})
        self.assertEqual(steps[-1].message.text, "(3/3) 4 is ruled out here: c (see steps 1, 2) [rule] ")

    def test_a_removal_step_carries_what_its_elimination_points_at(self):
        cell, highlight = MagicMock(), MagicMock()
        rule = self.__eliminating("intersections", lambda ruled_out: {(cell, 4): Elimination("a", "rule", highlight=highlight)})
        steps = PuzzleSolver(self.puzzle, [rule]).removal_steps(cell, EliminationsSetting("intersections"))
        self.assertIs(steps[0].message.highlight, highlight)

    def test_the_pending_hint_is_a_hint_carrying_what_the_move_points_at(self):
        highlight = MagicMock()
        solver = self.__solver_with([Move(Outcome.MOVED, "why", MagicMock(), 3, highlight=highlight)])
        solver.next()
        self.assertIs(solver.pending_hint().kind, MessageKind.HINT)
        self.assertIs(solver.pending_hint().highlight, highlight)

    def test_a_removal_step_is_information_with_a_short_text(self):
        cell = MagicMock()
        message = self.__steps_for(cell, {(cell, 4): "a"})[0].message
        self.assertIs(message.kind, MessageKind.INFO)
        self.assertEqual(message.short, "(1/1) 4 ruled out: a")

    def test_removal_steps_are_the_removals_the_pointed_out_move_needs_whatever_the_level(self):
        cell, other = MagicMock(), MagicMock()
        reasons = {(other, 4): Elimination("a", "rule"), (cell, 5): Elimination("b", "rule", ((other, 4),))}
        solver = self.__solver_with([Move(Outcome.MOVED, "why", cell, 3, reasons=reasons)])
        solver.next()
        steps = solver.removal_steps(cell, EliminationsSetting())
        self.assertEqual([step.cell for step in steps], [other, cell])
        self.assertEqual(steps[1].message.text, "(2/2) 5 is ruled out here: b (see step 1) [rule] ")

    def test_a_pointed_out_move_with_no_removals_of_its_own_leaves_the_removal_steps_to_the_level(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.MOVED, "why", cell, 3)])
        solver.next()
        self.assertEqual(solver.removal_steps(cell, EliminationsSetting()), [])

    def test_a_cell_with_nothing_removed_has_no_removal_steps(self):
        self.assertEqual(self.__steps_for(MagicMock(), {(MagicMock(), 4): "a"}), [])

    def test_making_a_move_enters_its_value(self):
        cell = MagicMock()
        PuzzleSolver(self.puzzle, []).make_move(Move(Outcome.MOVED, "hint", cell, 3))
        self.puzzle.enter_solved_value.assert_called_once_with(cell, 3)

    def test_first_next_points_out_the_move_without_making_it(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.MOVED, "why", cell, 3)])
        self.assertIsNone(solver.next())
        self.puzzle.select.assert_called_once_with(cell)
        self.puzzle.enter_solved_value.assert_not_called()
        self.assertEqual(solver.pending_hint().text, "why")

    def test_second_next_makes_the_move_pointed_out(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.MOVED, "why", cell, 3)])
        solver.next()
        solver.next()
        self.puzzle.enter_solved_value.assert_called_once_with(cell, 3)
        self.assertIsNone(solver.pending_hint())

    def test_cancelled_move_is_pointed_out_again_by_the_next_next(self):
        move = Move(Outcome.MOVED, "why", MagicMock(), 3)
        solver = self.__solver_with([move, move])
        solver.next()
        solver.cancel_pending_move()
        self.assertIsNone(solver.pending_hint())
        solver.next()
        self.puzzle.enter_solved_value.assert_not_called()
        self.assertEqual(solver.pending_hint().text, "why")

    def test_next_warns_about_a_move_that_stops_solving_and_selects_its_cell(self):
        cell = MagicMock()
        solver = self.__solver_with([Move(Outcome.STOPPED, "dead end", cell)])
        warning = solver.next()
        self.assertEqual(warning.text, "dead end")
        self.assertEqual(warning.kind, MessageKind.WARNING)
        self.puzzle.select.assert_called_once_with(cell)
        self.assertIsNone(solver.pending_hint())

    def test_next_warning_points_out_a_value_with_no_place_left(self):
        cell = MagicMock()
        warning = self.__solver_with([Move(Outcome.STOPPED, "dead end", cell, 4)]).next()
        self.assertEqual(warning.missing, (cell, 4))

    def test_next_with_no_move_says_to_guess(self):
        self.assertIn("make a guess", self.__solver_with([]).next().text)

    def test_auto_makes_every_move_then_warns_why_it_stopped(self):
        first, second = MagicMock(), MagicMock()
        moves = [Move(Outcome.MOVED, "why", first, 1), Move(Outcome.MOVED, "why", second, 2)]
        warning = self.__solver_with(moves).auto()
        self.assertEqual(self.puzzle.enter_solved_value.call_count, 2)
        self.puzzle.select.assert_called_with(second)
        self.assertIn("make a guess", warning.text)

    def test_auto_that_completes_the_puzzle_ends_without_a_warning(self):
        def complete(cell, value):
            self.puzzle.is_complete.return_value = True

        self.puzzle.enter_solved_value.side_effect = complete
        self.assertIsNone(self.__solver_with([Move(Outcome.MOVED, "why", MagicMock(), 1)]).auto())

    # Private functions

    def __rule(self, name, move):
        """A rule class that records being consulted and returns the move"""
        consulted = self.consulted

        class FakeRule(Rule):
            def find(self, puzzle):
                consulted.append(name)
                return move

        return FakeRule

    def __eliminating(self, level, ruling):
        """A rule class at the level, ruling out what ruling(ruled_out) returns"""

        class EliminatingRule(Rule):
            LEVEL = level

            def find(self, puzzle):
                return None

            def eliminations(self, puzzle, ruled_out=frozenset()):
                return ruling(ruled_out)

        return EliminatingRule

    def __steps_for(self, cell, *found_by_each_pass):
        """
        The removal steps of the cell, with a rule for each pass that adds what it found once the pass before has been
        found: each found is {(cell, value): why} or {(cell, value): (why, relied_on)}
        """
        return PuzzleSolver(self.puzzle, [self.__passing(found_by_each_pass)]).removal_steps(cell, EliminationsSetting("intersections"))

    def __passing(self, found_by_each_pass):
        """An eliminating rule that finds more on each pass: what each pass found, and the passes before it"""
        eliminations = [{found: self.__elimination(why) for found, why in found.items()} for found in found_by_each_pass]

        def ruling(ruled_out):
            found = {}
            for pass_found in eliminations:
                found.update(pass_found)
                if not all(key in ruled_out for key in pass_found):
                    break
            return found

        return self.__eliminating("intersections", ruling)

    def __elimination(self, why) -> Elimination:
        """The elimination for a why, or for a (why, relied_on)"""
        why, *relied_on = why if type(why) is tuple else (why,)
        return Elimination(why, "rule", *relied_on)

    def __solver_with(self, moves):
        """A solver whose only rule returns the given moves one at a time, then None"""
        moves = list(moves)

        class ScriptedRule(Rule):
            def find(self, puzzle):
                return moves.pop(0) if moves else None

        return PuzzleSolver(self.puzzle, [ScriptedRule])


if __name__ == "__main__":
    main()
