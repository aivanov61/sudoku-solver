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

from game.puzzle import Puzzle
from game.puzzle_catalog import PuzzleCatalog
from ui.terminal.copyright import Copyright
from ui.terminal.display import Display
from ui.terminal.layout_menu import LayoutMenu
from ui.terminal.terminal_ui import TerminalUI


class Main:
    """
    This runs a Sudoku puzzle whose layout comes from the puzzle catalog: it picks the layout and the
    user interface, then lets the user interface play the puzzle
    """

    def run(self):
        self.__display = Display()
        layouts = PuzzleCatalog.available()
        self.__splash(self.__startup_note(layouts))
        layout = self.__chosen_layout(layouts)
        if layout:
            self.__play(layout.board_class())

    # Private functions

    def __splash(self, note):
        Copyright.splash()
        if note:
            print(self.__display.term.yellow(note))
        try:
            self.__display.term.inkey(timeout=5.0)
        except KeyboardInterrupt:
            exit(1)

    def __startup_note(self, layouts) -> str:
        """Return a note to show under the splash screen: no layouts, or the only layout is not fully usable"""
        if not layouts:
            return "No puzzle layouts were found in the puzzles folder."
        return layouts[0].label() if len(layouts) == 1 and layouts[0].has_notes() else ""

    def __chosen_layout(self, layouts):
        """Return the layout to play (from the menu when there are several), or None to exit"""
        if len(layouts) > 1:
            return LayoutMenu(layouts, self.__display).choose()
        return layouts[0] if layouts and not layouts[0].is_broken() else None

    def __play(self, board):
        ui = TerminalUI(self.__display, board.v_cells, board.h_cells)
        ui.play(Puzzle(board, ui))


if __name__ == "__main__":
    Main().run()
