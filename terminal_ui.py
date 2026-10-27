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

from cell_attrs import CellAttrs
from commands import Commands
from display import Display, echo
from display_attrs import DisplayAttrs
from user_interface import Message, MessageKind


class TerminalUI:
    """
    The user interface on a terminal: it shows the game's messages and asks its questions on the status line.
    """

    def __init__(self):
        self.__guess_depth = 0
        self.__mode = None
        self.__offered = ()  # the actions the mode offers
        self.__drawn = {}  # (row, col): (attributes, value, possible values) of each cell as last drawn

    # Interface required for the game

    def status(self, message) -> None:
        Display.move_to_status_line()
        echo((self.__styled(message) if message else "") + Display.term.clear_eol)

    def inform(self, message) -> None:
        Display.show_on_status_line(self.__styled(message), wait=True)

    def confirm(self, question) -> bool:
        return Display.confirm(question)

    def ask_file_name(self, prompt, default) -> str:
        return Display.ask(prompt, default)

    def guess_depth_changed(self, depth) -> None:
        """Warn when guesses go from within the shades of gray to deeper than the last one"""
        runs_out = DisplayAttrs.is_beyond_last_shade(depth) and not DisplayAttrs.is_beyond_last_shade(self.__guess_depth)
        self.__guess_depth = depth
        runs_out and self.inform(Message("No more shades of gray left - repeating last shade. ", MessageKind.WARNING))

    def show_board(self, cells) -> None:
        """Clear the screen and draw every cell whole, and the command panel"""
        Display.clear_screen()
        for cell in cells:
            self.__draw_whole_cell(cell)
        self.__draw_panel()

    def cell_changed(self, cell) -> None:
        """Redraw only what differs from what was last drawn: the whole cell when its attributes changed"""
        attrs, value, possible_values = self.__drawn.get((cell.row, cell.col), (None, None, None))
        if attrs != cell.attr():
            self.__draw_whole_cell(cell)
            return
        value != cell.value() and self.__draw_value(cell)
        possible_values != cell.possible_values() and self.__draw_possible_values(cell)
        self.__remember(cell)

    def mode_changed(self, mode, actions) -> None:
        self.__mode = mode
        self.__offered = actions
        self.__draw_panel()

    # Interface required for Main

    def offered_actions(self) -> tuple:
        return self.__offered

    def show_help(self) -> None:
        """Show the commands the mode offers, with their keys, until a key is hit"""
        Display.clear_screen()
        print(Commands.long_help(self.__offered))
        Display.hit_any_key_to_continue()

    # Private functions

    def __styled(self, message) -> str:
        """Successes and hints in the solved style (steel blue), everything else in yellow"""
        if message.kind in (MessageKind.SUCCESS, MessageKind.HINT):
            return Display.styled(message.text, (CellAttrs.SOLVED,))
        return Display.term.yellow(message.text)

    def __draw_panel(self) -> None:
        """Draw the mode's title and its commands beside the puzzle, once a mode has been announced"""
        self.__mode and Display.draw_command_panel(self.__mode.value, Commands.panel(self.__offered))

    def __draw_whole_cell(self, cell) -> None:
        Display.draw_cell(cell.row, cell.col, cell.borders, cell.attr())
        self.__draw_value(cell)
        self.__draw_possible_values(cell)
        self.__remember(cell)

    def __draw_value(self, cell) -> None:
        Display.draw_cell_value(cell.row, cell.col, cell.value() or " ", cell.attr())

    def __draw_possible_values(self, cell) -> None:
        Display.draw_cell_possible_values(cell.row, cell.col, cell.possible_values(), cell.attr())

    def __remember(self, cell) -> None:
        """Keep what the cell looks like now, copying its possible values, which change in place"""
        self.__drawn[(cell.row, cell.col)] = (cell.attr(), cell.value(), set(cell.possible_values()))
