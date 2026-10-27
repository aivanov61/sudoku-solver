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
        layout and self.__start(Puzzle(layout.board_class(), TerminalUI()))

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
        cmd = Input.get_cmd()
        self._puzzle.command_received(cmd)
        self.__handle_puzzle_value(cmd) if Commands.is_value(cmd) else self.__handle_puzzle_func(cmd)

    def __handle_puzzle_value(self, cmd):
        self._puzzle.value_(*Commands.val_with_guess(cmd))
        self._puzzle.display_status()

    def __handle_puzzle_func(self, cmd):
        self.__execute_puzzle_func(cmd)if hasattr(self._puzzle, cmd) else self.__report_unsupported_func(cmd)

    def __execute_puzzle_func(self, cmd):
        try:
            getattr(self._puzzle, cmd)()
        except Exception as e:
            Display.warn(f'This puzzle\'s "{cmd}" command is broken!')
            self.__handle_possible_forced_quit(cmd)
            return
        self._puzzle.display_status()

    def __report_unsupported_func(self, cmd):
        Display.warn(f'This puzzle does not support the "{cmd}" command')
        self.__handle_possible_forced_quit(cmd)

    def __handle_possible_forced_quit(self, cmd):
        if cmd not in ("quit_", "force_quit_"):
            return
        Display.move_to_status_line()
        print("\n" + Display.term.clear_eol + "FORCING quit")
        self._puzzle.is_playing = False


if __name__ == "__main__":
    Main().run()
