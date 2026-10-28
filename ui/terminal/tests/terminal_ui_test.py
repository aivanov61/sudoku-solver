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
from unittest.mock import call, MagicMock, patch

sys.path.insert(0, ".")

from game.actions import Action, Mode, OFFERED_ACTIONS
from game.cell_attrs import CellAttrs
from game.config_option import ConfigOption
from game.user_interface import Message, MessageKind
from ui.terminal.commands import Commands
from ui.terminal.display import Display
from ui.terminal.terminal_ui import TerminalUI


class TestTerminalUI(TestCase):
    LONG = Message("much too long", MessageKind.WARNING, short="short")

    def setUp(self):
        self.display = MagicMock()
        self.display.term.yellow = lambda text: f"<yellow>{text}</yellow>"
        self.display.term.clear_eos = "<clear>"
        self.display.term.gray50 = lambda text: f"<gray>{text}</gray>"
        self.display.panel = True
        self.display.term.width = Display.MIN_WIDTH
        self.ui = TerminalUI(self.display, 9, 9)
        self.display.reset_mock()
        return super().setUp()

    # Starting

    def test_a_new_terminal_ui_sets_the_board_size_and_checks_the_screen(self):
        display = MagicMock()
        TerminalUI(display, 9, 6)
        display.geometry.assert_called_once_with(9, 6)
        display.validate_screen_size.assert_called_once()

    # Playing

    def test_play_shows_the_game_then_hands_it_each_action_until_it_stops_playing(self):
        game = self.__game()
        self.__play(game, [(Action.UP, None), (Action.VALUE, 5)])
        self.assertEqual(game.handle.call_args_list, [call(Action.UP, None), call(Action.VALUE, 5), call(Action.QUIT, None)])
        game.render.assert_called_once()

    def test_play_puts_the_cursor_on_the_selected_cell_before_each_key(self):
        game = self.__game()
        self.__play(game, [])
        self.display.move_to_cell.assert_called_with(2, 3)

    def test_play_shows_the_whole_game_again_after_the_screen_is_resized(self):
        game = self.__game()
        self.__play(game, [], screen_ok=[False, True])
        self.assertEqual(game.render.call_count, 2)

    def test_help_is_shown_without_the_game_and_the_game_is_shown_again_after_it(self):
        game = self.__game()
        printed, record = self.__play(game, [(Commands.HELP, None)])
        printed.assert_any_call(Commands.long_help(()))
        self.display.hit_any_key_to_continue.assert_called_once()
        self.assertEqual(game.handle.call_args_list, [call(Action.QUIT, None)])
        self.assertEqual(game.render.call_count, 2)

    def test_help_shows_the_commands_of_the_mode(self):
        game = self.__game()
        self.ui.mode_changed(Mode.SETUP, OFFERED_ACTIONS[Mode.SETUP])
        printed, record = self.__play(game, [(Commands.HELP, None)])
        printed.assert_any_call(Commands.long_help(OFFERED_ACTIONS[Mode.SETUP]))

    def test_a_broken_action_is_logged_and_play_goes_on(self):
        game = self.__game(broken=Action.UP)
        printed, record = self.__play(game, [(Action.UP, None)])
        record.assert_called_once()
        self.assertIsInstance(record.call_args.args[0], RuntimeError)
        self.assertEqual(game.handle.call_args_list[-1], call(Action.QUIT, None))

    def test_a_broken_action_says_what_broke_where_and_where_the_details_are_then_waits(self):
        game = self.__game(broken=Action.UP)
        self.__play(game, [(Action.UP, None)])
        warning = self.display.warn.call_args
        self.assertIn('"up" command is broken: RuntimeError: broken', warning.args[0])
        self.assertRegex(warning.args[0], r" - at \S*terminal_ui_test\.py:\d+ in handle ")
        self.assertTrue(warning.args[0].endswith("(details in sudoku.log)"))
        self.assertEqual(warning.kwargs, {"wait": True})

    def test_a_broken_action_shows_the_whole_game_again(self):
        game = self.__game(broken=Action.UP)
        self.__play(game, [(Action.UP, None)])
        self.assertEqual(game.render.call_count, 2)

    def test_a_broken_action_says_so_when_the_details_could_not_be_logged(self):
        game = self.__game(broken=Action.UP)
        self.__play(game, [(Action.UP, None)], logged_to=None)
        self.assertTrue(self.display.warn.call_args.args[0].endswith("(the details could not be logged)"))

    def test_a_broken_quit_forces_the_game_to_stop(self):
        game = self.__game(broken=Action.QUIT)
        self.__play(game, [])
        game.force_quit_.assert_called_once()

    # Showing the game

    def test_status_shows_a_warning_in_yellow_and_clears_the_rest_of_the_line(self):
        self.assertEqual(self.__status(Message("careful", MessageKind.WARNING)), "<yellow>careful</yellow>")

    def test_status_shows_information_in_yellow(self):
        self.assertEqual(self.__status(Message("saved", MessageKind.INFO)), "<yellow>saved</yellow>")

    def test_status_shows_success_and_hints_in_the_solved_style(self):
        self.display.styled.side_effect = lambda text, attrs: f"<{attrs[0]}>{text}"
        for kind in (MessageKind.SUCCESS, MessageKind.HINT):
            self.assertEqual(self.__status(Message("why", kind)), "<solved>why")
            self.display.styled.assert_called_with("why", (CellAttrs.SOLVED,))

    def test_status_without_a_message_blanks_the_line(self):
        self.assertEqual(self.__status(None), "")

    def test_without_the_panel_a_blank_status_shows_the_mode_in_gray(self):
        self.display.panel = False
        self.ui.mode_changed(Mode.PLAY, OFFERED_ACTIONS[Mode.PLAY])
        self.assertEqual(self.__status(None), "<gray>PLAY - ? for commands</gray>")

    def test_without_the_panel_a_new_mode_draws_no_panel(self):
        self.display.panel = False
        self.ui.mode_changed(Mode.PLAY, OFFERED_ACTIONS[Mode.PLAY])
        self.ui.show_board([])
        self.display.draw_command_panel.assert_not_called()

    def test_without_the_panel_the_whole_text_is_shown_to_wrap(self):
        self.display.panel = False
        self.display.term.width = len("much too long") - 1
        self.assertEqual(self.__status(self.LONG), "<yellow>much too long</yellow>")

    def test_inform_shows_the_message_and_waits_for_a_key(self):
        self.ui.inform(Message("careful", MessageKind.WARNING))
        self.display.show_on_status_line.assert_called_once_with("<yellow>careful</yellow>", wait=True)

    def test_status_shows_the_short_text_when_the_whole_text_does_not_fit(self):
        self.display.term.width = len("much too long") - 1
        self.assertEqual(self.__status(self.LONG), "<yellow>short</yellow>")

    def test_status_shows_the_whole_text_when_it_fits(self):
        self.display.term.width = len("much too long")
        self.assertEqual(self.__status(self.LONG), "<yellow>much too long</yellow>")

    def test_inform_leaves_room_for_the_prompt_to_hit_a_key(self):
        self.display.term.width = len("much too long" + Display.HIT_ANY_KEY) - 1
        self.ui.inform(self.LONG)
        self.display.show_on_status_line.assert_called_once_with("<yellow>short</yellow>", wait=True)

    def test_status_shows_a_missing_value_in_its_cell(self):
        self.__status(Message("stuck", MessageKind.WARNING, (self.__cell(2, 5), 4)))
        self.display.draw_cell_missing_value.assert_called_once_with(2, 5, 4)

    def test_the_next_status_draws_the_cell_as_it_is_again(self):
        self.__status(Message("stuck", MessageKind.WARNING, (self.__cell(2, 5, attrs=("a",), marks=(4,)), 4)))
        self.__status(None)
        self.display.draw_cell_marks.assert_called_once_with(2, 5, (4,), ("a",), False)
        self.display.draw_cell_value.assert_not_called()

    def test_a_status_without_a_missing_value_draws_no_cell(self):
        self.__status(Message("careful", MessageKind.WARNING))
        self.__status(None)
        self.display.draw_cell_missing_value.assert_not_called()
        self.display.draw_cell_marks.assert_not_called()
        self.display.draw_cell_value.assert_not_called()

    def test_inform_shows_a_missing_value_until_the_player_has_seen_the_message(self):
        self.ui.inform(Message("stuck", MessageKind.WARNING, (self.__cell(2, 5, value=None), 4)))
        drawn = [name for name, _args, _kwargs in self.display.mock_calls]
        self.assertEqual(drawn, ["draw_cell_missing_value", "show_on_status_line", "draw_cell_marks"])

    def test_confirm_asks_on_the_status_line(self):
        self.display.confirm.return_value = True
        self.assertTrue(self.ui.confirm("Really?"))
        self.display.confirm.assert_called_once_with("Really?")

    def test_file_name_is_asked_for_on_the_status_line_with_its_extension_shown(self):
        self.display.ask.return_value = "game"
        self.assertEqual(self.ui.ask_file_name("Save to file:", "sudoku", ".json"), "game.json")
        self.display.ask.assert_called_once_with("Save to file:", "sudoku", ".json")

    def test_a_cancelled_file_name_is_none(self):
        self.display.ask.return_value = None
        self.assertIsNone(self.ui.ask_file_name("Save to file:", "sudoku", ".json"))

    def test_an_empty_file_name_counts_as_cancelled(self):
        self.display.ask.return_value = ""
        self.assertIsNone(self.ui.ask_file_name("Save to file:", "sudoku", ".json"))

    def test_show_board_clears_the_screen_and_draws_every_cell_whole(self):
        cells = [self.__cell(0, 0, value=5), self.__cell(0, 1, possible={1, 2})]
        self.ui.show_board(cells)
        self.display.clear_screen.assert_called_once()
        self.assertEqual(self.display.draw_cell.call_count, 2)
        self.display.draw_cell_value.assert_any_call(0, 0, 5, ())
        self.display.draw_cell_possible_values.assert_any_call(0, 1, {1, 2}, (), False)

    def test_a_new_mode_draws_its_panel(self):
        self.ui.mode_changed(Mode.PLAY, OFFERED_ACTIONS[Mode.PLAY])
        self.display.draw_command_panel.assert_called_once_with("PLAY", Commands.panel(OFFERED_ACTIONS[Mode.PLAY]))

    def test_show_board_redraws_the_panel_of_the_mode(self):
        self.ui.mode_changed(Mode.SETUP, OFFERED_ACTIONS[Mode.SETUP])
        self.display.reset_mock()
        self.ui.show_board([])
        self.display.draw_command_panel.assert_called_once_with("SETUP", Commands.panel(OFFERED_ACTIONS[Mode.SETUP]))

    def test_a_cell_not_yet_drawn_is_drawn_whole(self):
        display = self.__drawn_after_change(None, self.__cell(2, 3, value=4))
        display.draw_cell.assert_called_once()
        display.draw_cell_value.assert_called_once_with(2, 3, 4, ())

    def test_changed_attributes_redraw_the_whole_cell(self):
        cell = self.__cell(value=4)
        display = self.__drawn_after_change(cell, self.__cell(value=4, attrs=(CellAttrs.GUESS,)))
        display.draw_cell.assert_called_once()
        display.draw_cell_marks.assert_called_once()
        display.draw_cell_value.assert_called_once()
        display.draw_cell_possible_values.assert_called_once()

    def test_a_whole_empty_cell_is_drawn_with_its_marks(self):
        display = self.__drawn_after_change(None, self.__cell(2, 3, marks=(5, 8)))
        display.draw_cell_marks.assert_called_once_with(2, 3, (5, 8), (), False)
        display.draw_cell_value.assert_not_called()

    def test_a_tagged_cell_draws_its_marks_and_possible_values_as_tagged(self):
        display = self.__drawn_after_change(None, self.__cell(2, 3, possible={1, 5}, marks=(5,), tagged=True))
        display.draw_cell_marks.assert_called_once_with(2, 3, (5,), (), True)
        display.draw_cell_possible_values.assert_called_once_with(2, 3, {1, 5}, (), True)

    def test_a_changed_tag_redraws_the_marks_and_possible_values(self):
        display = self.__drawn_after_change(self.__cell(possible={1}), self.__cell(possible={1}, tagged=True))
        display.draw_cell.assert_not_called()
        display.draw_cell_marks.assert_called_once_with(0, 0, (), (), True)
        display.draw_cell_possible_values.assert_called_once_with(0, 0, {1}, (), True)

    def test_a_changed_value_redraws_only_the_middle_line_blank_with_the_value_on_it(self):
        display = self.__drawn_after_change(self.__cell(value=4), self.__cell(value=6))
        display.draw_cell.assert_not_called()
        self.assertEqual(
            display.method_calls, [call.draw_cell_marks(0, 0, (), (), False), call.draw_cell_value(0, 0, 6, ())]
        )
        display.draw_cell_possible_values.assert_not_called()

    def test_an_emptied_cell_shows_its_marks_and_no_value(self):
        display = self.__drawn_after_change(self.__cell(value=4), self.__cell(value=None, marks=(4,)))
        display.draw_cell_marks.assert_called_once_with(0, 0, (4,), (), False)
        display.draw_cell_value.assert_not_called()

    def test_changed_marks_redraw_only_the_middle_line(self):
        display = self.__drawn_after_change(self.__cell(marks=(4,)), self.__cell(marks=(4, 7)))
        display.draw_cell.assert_not_called()
        display.draw_cell_marks.assert_called_once_with(0, 0, (4, 7), (), False)
        display.draw_cell_possible_values.assert_not_called()

    def test_changed_possible_values_redraw_only_the_possible_values(self):
        display = self.__drawn_after_change(self.__cell(possible={1, 2}), self.__cell(possible={2}))
        display.draw_cell.assert_not_called()
        display.draw_cell_marks.assert_not_called()
        display.draw_cell_possible_values.assert_called_once_with(0, 0, {2}, (), False)

    def test_an_unchanged_cell_is_not_redrawn(self):
        display = self.__drawn_after_change(self.__cell(value=4), self.__cell(value=4))
        self.assertEqual(display.method_calls, [])

    def test_guesses_going_deeper_than_the_last_shade_warn(self):
        self.assertEqual(self.__warnings_for_depths([10, 11]), ["No more shades of gray left - repeating last shade. "])

    def test_guesses_staying_beyond_the_last_shade_do_not_warn_again(self):
        self.assertEqual(len(self.__warnings_for_depths([11, 12, 11])), 1)

    def test_coming_back_within_the_shades_and_going_beyond_again_warns_again(self):
        self.assertEqual(len(self.__warnings_for_depths([11, 10, 11])), 2)

    def test_guesses_within_the_shades_do_not_warn(self):
        self.assertEqual(self.__warnings_for_depths([1, 2, 10, 9, 0]), [])

    # Configuring

    def test_configure_shows_each_group_under_a_heading_and_returns_the_options_as_chosen(self):
        options = [
            ConfigOption("Marks", "Kind", (("a", 1), ("b", 2)), 1),
            ConfigOption("Marks", "Level", (("x", 1), ("y", 2), ("z", 3)), 3),
            ConfigOption("Other", "Speed", (("slow", 1), ("fast", 2)), 1),
        ]
        with patch("ui.terminal.terminal_ui.Menu", side_effect=self.__menu_pressing_tab_on_line(2)) as menu:
            chosen = self.ui.configure(options)
        self.assertEqual(
            self.shown_items,
            [("MenuHeading", "Marks"), ("MenuChoice", "Kind"), ("MenuChoice", "Level"), ("MenuHeading", "Other"),
             ("MenuChoice", "Speed")],
        )
        self.assertEqual(menu.call_args.args[0], "Configure")
        self.assertEqual([option.value for option in chosen], [1, 1, 1])

    def test_configure_shows_an_options_notes_under_it_with_the_key_of_their_action(self):
        notes = ("Tag with {key} first", "")
        options = [ConfigOption("Marks", "Whole", (("off", False), ("on", True)), False, notes, Action.TAG)]
        with patch("ui.terminal.terminal_ui.Menu", side_effect=self.__menu_pressing_tab_on_line(1)):
            self.ui.configure(options)
        self.assertEqual(self.shown_items, [("MenuHeading", "Marks"), ("MenuChoice", "Whole"), ("MenuNote", "Tag")])
        self.assertEqual(self.shown_texts[2], "Tag with m first")

    def test_configure_cancelled_returns_the_options_as_they_were(self):
        options = [ConfigOption("Marks", "Kind", (("a", 1), ("b", 2)), 1)]
        with patch("ui.terminal.terminal_ui.Menu", side_effect=self.__menu_pressing_tab_on_line(1, picked=None)):
            self.assertEqual(self.ui.configure(options), options)

    # Private functions

    def __menu_pressing_tab_on_line(self, line, picked=0):
        """A stand-in for Menu that keeps the items it is shown, presses TAB on one of them, then returns picked"""

        def menu(title, items, keys_help, display):
            self.shown_texts = [item.text() for item in items]
            self.shown_items = [(type(item).__name__, text.split(" ")[0]) for item, text in zip(items, self.shown_texts)]
            items[line].handle("KEY_TAB")
            return MagicMock(**{"choose.return_value": picked})

        return menu

    def __game(self, broken=None):
        """A stand-in game at (2, 3) that stops playing on QUIT, and whose handling of the broken action fails"""
        game = MagicMock(is_playing=True, selected_cell=(2, 3))

        def handle(action, digit):
            if action is broken:
                raise RuntimeError("broken")
            game.is_playing = action is not Action.QUIT

        def force_quit():
            game.is_playing = False

        game.handle.side_effect = handle
        game.force_quit_.side_effect = force_quit
        return game

    def __play(self, game, commands, screen_ok=None, logged_to="sudoku.log"):
        """Play the game with the commands, then QUIT, logging errors to the file given; return the patched print and error log"""
        self.display.validate_screen_size.side_effect = (screen_ok or []) + [True] * 10
        with patch("builtins.print") as printed, patch("ui.terminal.terminal_ui.ErrorLog.record", return_value=logged_to) as record:
            with patch("ui.terminal.terminal_ui.Input.get_cmd", side_effect=commands + [(Action.QUIT, None)]):
                self.ui.play(game)
        return printed, record

    def __cell(self, row=0, col=0, value=None, attrs=(), possible=frozenset(), marks=(), tagged=False):
        """A stand-in for a cell as it is at one moment"""
        cell = MagicMock(row=row, col=col)
        cell.value.return_value = value
        cell.attr.return_value = attrs
        cell.possible_values.return_value = set(possible)
        cell.marks.return_value = tuple(marks)
        cell.is_tagged.return_value = tagged
        return cell

    def __drawn_after_change(self, before, after):
        """Report the cell as before (if any), then as after; return the display, holding only the second report's drawing"""
        if before:
            self.ui.cell_changed(before)
        self.display.reset_mock()
        self.ui.cell_changed(after)
        return self.display

    def __warnings_for_depths(self, depths) -> list:
        """Report each guess depth in turn; return the text of every warning shown"""
        with patch.object(TerminalUI, "inform") as inform:
            for depth in depths:
                self.ui.guess_depth_changed(depth)
        return [call.args[0].text for call in inform.call_args_list]

    def __status(self, message) -> str:
        """Show the message on the status line and return the text shown there"""
        self.ui.status(message)
        return self.display.show_on_status_line.call_args.args[0]


if __name__ == "__main__":
    main()
