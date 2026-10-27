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

from actions import Action
from copyright import Copyright
from commands import Commands
from display import Display
from input import Input
from layout_menu import LayoutMenu
from puzzle import Puzzle
from puzzle_catalog import PuzzleCatalog
from terminal_ui import TerminalUI


class Main:
    """
    This runs a Sudoku puzzle whose layout comes from the puzzle catalog
    """

    def run(self):
        layouts = PuzzleCatalog.available()
        self.__splash(self.__startup_note(layouts))
        layout = self.__chosen_layout(layouts)
        self.__ui = TerminalUI()
        layout and self.__start(Puzzle(layout.board_class(), self.__ui))

    # Private functions

    def __splash(self, note):
        Copyright.splash()
        note and print(Display.term.yellow(note))
        try:
            Display.term.inkey(timeout=5.0)
        except:
            exit(1)

    def __startup_note(self, layouts) -> str:
        """Return a note to show under the splash screen: no layouts, or the only layout is not fully usable"""
        if not layouts:
            return "No puzzle layouts were found in the puzzles folder."
        return layouts[0].label() if len(layouts) == 1 and layouts[0].has_notes() else ""

    def __chosen_layout(self, layouts):
        """Return the layout to play (from the menu when there are several), or None to exit"""
        if len(layouts) > 1:
            return LayoutMenu(layouts).choose()
        return layouts[0] if layouts and not layouts[0].is_broken() else None

    def __start(self, puzzle):
        self._puzzle = puzzle
        self._puzzle.render()
        self.__play()
        Display.move_to_status_line()
        print("\n")

    def __play(self):
        while self._puzzle.is_playing:
            if not Display.validate_screen_size():
                self._puzzle.render()
            Display.move_to_cell(*self._puzzle.selected_cell)
            self.__process_user_input()

    def __process_user_input(self):
        command, digit = Input.get_cmd(self.__ui.offered_actions())
        self._puzzle.command_received(command)
        self.__show_help() if command == Commands.HELP else self.__carry_out(command, digit)

    def __show_help(self):
        self.__ui.show_help()
        self._puzzle.render()

    def __carry_out(self, action, digit):
        """Call the puzzle's method for the action, with the digit for values and guesses"""
        try:
            getattr(self._puzzle, f"{action.value}_")(*([] if digit is None else [digit]))
        except Exception as e:
            Display.warn(f'This puzzle\'s "{action.value}" command is broken!')
            self.__handle_possible_forced_quit(action)
            return
        self._puzzle.display_status()

    def __handle_possible_forced_quit(self, action):
        if action not in (Action.QUIT, Action.FORCE_QUIT):
            return
        Display.move_to_status_line()
        print("\n" + Display.term.clear_eol + "FORCING quit")
        self._puzzle.is_playing = False


if __name__ == "__main__":
    Main().run()
