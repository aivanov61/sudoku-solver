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

import argparse
import sys

sys.path.insert(0, ".")

from game.puzzle import Puzzle
from game.puzzle_catalog import PuzzleCatalog
from ui.terminal.copyright import Copyright
from ui.terminal.display import Display
from ui.terminal.menu import Menu
from ui.terminal.menu_entry import MenuEntry
from ui.terminal.terminal_ui import TerminalUI


class Main:
    """
    This runs a Sudoku puzzle whose layout comes from the puzzle catalog: it picks the layout and the
    user interface, then lets the user interface play the puzzle
    """

    LAYOUT_KEYS_HELP = "Up/down to choose, ENTER to play, ESC or q to quit"
    QUIT_QUESTION = "Really quit? (y/n)"

    def run(self, args=None):
        """Play, as the command line arguments ask (sys.argv's when args is None)"""
        options = self.__options(args)
        self.__display = Display(panel=not options.no_panel)
        layouts = PuzzleCatalog.available()
        self.__splash(self.__startup_note(layouts))
        layout = self.__chosen_layout(layouts)
        if layout:
            self.__play(layout.board_class())

    # Private functions

    def __options(self, args) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Play sudoku puzzles in the terminal.")
        parser.add_argument(
            "--no-panel", action="store_true",
            help="leave out the command panel beside the puzzle, so it fits a narrower terminal (55 columns for 9x9)",
        )
        return parser.parse_args(args)

    def __splash(self, note):
        Copyright.splash()
        if note:
            print(self.__display.term.yellow(note))
        try:
            self.__wait_for_a_key(timeout=5.0)
        except KeyboardInterrupt:
            exit(1)

    def __wait_for_a_key(self, timeout) -> None:
        """Wait for a key or the timeout, then drop any other keys pressed meanwhile, so the menu never reads them"""
        term = self.__display.term
        with term.cbreak():
            term.inkey(timeout=timeout)
            while term.inkey(timeout=0):
                pass

    def __startup_note(self, layouts) -> str:
        """Return a note to show under the splash screen: no layouts, or the only layout is not fully usable"""
        if not layouts:
            return "No puzzle layouts were found in the puzzles folder."
        return layouts[0].label() if len(layouts) == 1 and layouts[0].has_notes() else ""

    def __chosen_layout(self, layouts):
        """Return the layout to play (from the menu when there are several), or None to exit"""
        if len(layouts) > 1:
            return self.__layout_menu(layouts).choose()
        return layouts[0] if layouts and not layouts[0].is_broken() else None

    def __layout_menu(self, layouts) -> Menu:
        """A menu of the layouts, with any notes after their names; broken ones can't be picked"""
        entries = [MenuEntry(layout.label(), layout, can_pick=not layout.is_broken()) for layout in layouts]
        return Menu("Choose a puzzle layout:", entries, self.LAYOUT_KEYS_HELP, self.__display, self.QUIT_QUESTION)

    def __play(self, board):
        ui = TerminalUI(self.__display, board.v_cells, board.h_cells)
        ui.play(Puzzle(board, ui))


if __name__ == "__main__":
    Main().run()
