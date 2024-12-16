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

# NOTE: supports different kinds of puzzles - change the following line
from puzzle_3x3 import Puzzle3x3 as Puzzle


class Main:
    """
    This runs the generic 3x3 Sudoku puzzle
    """

    def run(self):
        self.__splash()
        self._puzzle = Puzzle()
        self._puzzle.render()
        self.__play()
        Display.move_to_status_line()
        print("\n")

    def __splash(self):
        Copyright.splash()
        try:
            Display.term.inkey(timeout=5.0)
        except:
            exit(1)

    def __play(self):
        while self._puzzle.is_playing:
            if not Display.validate_screen_size():
                self._puzzle.render()
            Display.move_to_cell(*self._puzzle.selected_cell)
            self.__process_user_input()

    def __process_user_input(self):
        cmd = Input.get_cmd()
        self.__handle_puzzle_value(cmd) if Commands.is_value(cmd) else self.__handle_puzzle_func(cmd)

    def __handle_puzzle_value(self, cmd):
        self._puzzle.value(*Commands.val_with_guess(cmd))
        self._puzzle.display_status()

    def __handle_puzzle_func(self, cmd):
        self.__report_unsupported_func(cmd) if not hasattr(self._puzzle, cmd) else self.__execute_puzzle_func(cmd)

    def __report_unsupported_func(self, cmd):
        Display.warn(f'This puzzle does not support the "{cmd}" command')
        self.__handle_possible_forced_quit(cmd)

    def __handle_possible_forced_quit(self, cmd):
        if not cmd == "quit":
            return
        Display.move_to_status_line()
        print("\n" + Display.term.clear_eol + "FORCING quit")
        self._puzzle.is_playing = False

    def __execute_puzzle_func(self, cmd):
        try:
            getattr(self._puzzle, cmd)()
        except Exception as e:
            Display.warn(f'This puzzle\'s "{cmd}" command is broken!')
            self.__handle_possible_forced_quit(cmd)
            return
        self._puzzle.display_status()


if __name__ == "__main__":
    Main().run()
