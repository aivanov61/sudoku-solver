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

sys.path.insert(0, ".")

from game.actions import Action
from game.cell_attrs import CellAttrs
from game.puzzle import Puzzle
from game.user_interface import Message, MessageKind
from ui.error_log import ErrorLog
from ui.terminal.commands import Commands
from ui.terminal.display import Display, echo
from ui.terminal.display_attrs import DisplayAttrs
from ui.terminal.input import Input
from ui.terminal.menu import Menu
from ui.terminal.menu_choice import MenuChoice
from ui.terminal.menu_heading import MenuHeading


class TerminalUI:
    """
    The user interface on a terminal: it runs the game from the keyboard, draws the board and the command
    panel, and shows the game's messages and asks its questions on the status line.
    """

    CONFIGURE_KEYS_HELP = "Up/down to choose, TAB/Shift-TAB or right/left to change, ESC for the puzzle"

    def __init__(self, display: Display, v_cells: int, h_cells: int):
        display.geometry(v_cells, h_cells)
        display.validate_screen_size()
        self.__display = display
        self.__input = Input(display)
        self.__guess_depth = 0
        self.__mode = None
        self.__offered = ()  # the actions the mode offers
        self.__drawn = {}  # (row, col): (attributes, value, possible values, marks) of each cell as last drawn
        self.__showing_missing = None  # the cell showing a message's missing value, until the message goes

    # Interface required for Main

    def play(self, game: Puzzle) -> None:
        """Show the game, then hand it the action for each key, until the game is over"""
        game.render()
        while game.is_playing:
            if not self.__display.validate_screen_size():
                game.render()
            self.__display.move_to_cell(*game.selected_cell)
            self.__carry_out(game, *self.__input.get_cmd(self.__offered))
        self.__display.move_to_status_line()
        print("\n")

    # Interface required for the game

    def status(self, message) -> None:
        """Show the message, and its missing value in its cell, until the next status"""
        self.__take_back_missing()
        self.__display.move_to_status_line()
        echo((self.__styled(message, self.__display.term.width) if message else "") + self.__display.term.clear_eol)
        self.__show_missing(message)

    def inform(self, message) -> None:
        """Show the message, and its missing value in its cell, until a key is hit"""
        self.__show_missing(message)
        room = self.__display.term.width - len(Display.HIT_ANY_KEY)
        self.__display.show_on_status_line(self.__styled(message, room), wait=True)
        self.__take_back_missing()

    def confirm(self, question) -> bool:
        return self.__display.confirm(question)

    def ask_file_name(self, prompt, default, extension) -> str:
        """Ask for the file name with the extension shown after it; return it with the extension, or None if cancelled or empty"""
        name = self.__display.ask(prompt, default, extension)
        return name + extension if name else None

    def configure(self, options) -> list:
        """Show the options in a menu, each group under a heading, until ESC; return them as chosen"""
        choices = [MenuChoice(option.name, option.labels(), option.chosen_index()) for option in options]
        Menu("Configure", self.__menu_items(options, choices), self.CONFIGURE_KEYS_HELP, self.__display).choose()
        return [option.with_choice(choice.chosen) for option, choice in zip(options, choices)]

    def guess_depth_changed(self, depth) -> None:
        """Warn when guesses go from within the shades of gray to deeper than the last one"""
        runs_out = DisplayAttrs.is_beyond_last_shade(depth) and not DisplayAttrs.is_beyond_last_shade(self.__guess_depth)
        self.__guess_depth = depth
        if runs_out:
            self.inform(Message("No more shades of gray left - repeating last shade. ", MessageKind.WARNING))

    def show_board(self, cells) -> None:
        """Clear the screen and draw every cell whole, and the command panel"""
        self.__display.clear_screen()
        for cell in cells:
            self.__draw_whole_cell(cell)
        self.__draw_panel()

    def cell_changed(self, cell) -> None:
        """
        Redraw only what differs from what was last drawn: the whole cell when its attributes changed, and the
        small digits (marks and possible values) when its tag changed
        """
        attrs, value, possible_values, marks, tagged = self.__drawn.get((cell.row, cell.col), (None,) * 5)
        if attrs != cell.attr():
            self.__draw_whole_cell(cell)
            return
        is_retagged = tagged != cell.is_tagged()
        if is_retagged or value != cell.value() or marks != cell.marks():
            self.__draw_middle(cell)
        if is_retagged or possible_values != cell.possible_values():
            self.__draw_possible_values(cell)
        self.__remember(cell)

    def mode_changed(self, mode, actions) -> None:
        self.__mode = mode
        self.__offered = actions
        self.__draw_panel()

    # Private functions

    def __take_back_missing(self) -> None:
        """Draw the cell showing a missing value as it is again, if there is one"""
        if self.__showing_missing:
            self.__draw_middle(self.__showing_missing)
            self.__showing_missing = None

    def __show_missing(self, message) -> None:
        """Draw the message's missing value in its cell, if it has one"""
        if message and message.missing:
            cell, value = message.missing
            self.__display.draw_cell_missing_value(cell.row, cell.col, value)
            self.__showing_missing = cell

    def __menu_items(self, options, choices) -> list:
        """Return the choices, with a heading before the first of each group"""
        items, group = [], None
        for option, choice in zip(options, choices):
            if option.group != group:
                group = option.group
                items.append(MenuHeading(group))
            items.append(choice)
        return items

    def __carry_out(self, game: Puzzle, command, digit) -> None:
        """Show the help screen, or hand the action to the game, surviving an action that breaks"""
        if command == Commands.HELP:
            self.__show_help()
            game.render()
            return
        try:
            game.handle(command, digit)
        except Exception as error:
            self.__report_broken(game, command, error)

    def __show_help(self) -> None:
        """Show the commands the mode offers, with their keys, until a key is hit"""
        self.__display.clear_screen()
        print(Commands.long_help(self.__offered))
        self.__display.hit_any_key_to_continue()

    def __report_broken(self, game: Puzzle, command, error) -> None:
        """
        Log the error, say what broke, why and where until a key is hit, then show the whole game again,
        as the message may have scrolled the screen; a broken quit stops the game instead
        """
        log = ErrorLog.record(error)
        details = f"details in {log}" if log else "the details could not be logged"
        what = f'This puzzle\'s "{command.value}" command is broken: {type(error).__name__}: {error}'
        self.__display.warn(f"{what} - at {ErrorLog.where(error)} ({details})", wait=True)
        if command in (Action.QUIT, Action.FORCE_QUIT):
            self.__force_quit(game)
        else:
            game.render()

    def __force_quit(self, game: Puzzle) -> None:
        self.__display.move_to_status_line()
        print("\n" + self.__display.term.clear_eol + "FORCING quit")
        game.force_quit_()

    def __styled(self, message, room) -> str:
        """Successes and hints in the solved style (steel blue), everything else in yellow"""
        text = self.__fitting_text(message, room)
        if message.kind in (MessageKind.SUCCESS, MessageKind.HINT):
            return self.__display.styled(text, (CellAttrs.SOLVED,))
        return self.__display.term.yellow(text)

    def __fitting_text(self, message, room) -> str:
        """The message's text, or its short text when the whole text is longer than the room on the line"""
        return message.short if message.short and len(message.text) > room else message.text

    def __draw_panel(self) -> None:
        """Draw the mode's title and its commands beside the puzzle, once a mode has been announced"""
        if self.__mode:
            self.__display.draw_command_panel(self.__mode.value, Commands.panel(self.__offered))

    def __draw_whole_cell(self, cell) -> None:
        self.__display.draw_cell(cell.row, cell.col, cell.borders, cell.attr())
        self.__draw_middle(cell)
        self.__draw_possible_values(cell)
        self.__remember(cell)

    def __draw_middle(self, cell) -> None:
        """Draw the middle line: the marks (none on a filled cell), then the value on top of them, if any"""
        self.__display.draw_cell_marks(cell.row, cell.col, cell.marks(), cell.attr(), cell.is_tagged())
        if cell.value():
            self.__display.draw_cell_value(cell.row, cell.col, cell.value(), cell.attr())

    def __draw_possible_values(self, cell) -> None:
        display = self.__display
        display.draw_cell_possible_values(cell.row, cell.col, cell.possible_values(), cell.attr(), cell.is_tagged())

    def __remember(self, cell) -> None:
        """Keep what the cell looks like now, copying its possible values, which change in place"""
        drawn = (cell.attr(), cell.value(), set(cell.possible_values()), cell.marks(), cell.is_tagged())
        self.__drawn[(cell.row, cell.col)] = drawn
