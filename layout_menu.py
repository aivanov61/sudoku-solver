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

from display import Display, echo
from puzzle_catalog import PuzzleLayout


class LayoutMenu:
    """
    Let the player choose a puzzle layout, a page at a time.

    A layout is chosen by typing its number and pressing ENTER; (p)revious, (n)ext and (q)uit act on a
    single key, and CTRL-C quits.  Broken layouts are listed with their notes but cannot be chosen.
    """

    RESERVED_LINES = 5  # title, blank line, blank line, message, prompt
    MAX_DIGITS = 9  # always fits in a 32-bit integer; more digits make the number "too big"
    TOO_BIG_MARK = "..."

    def __init__(self, layouts):
        self.__layouts = layouts
        self.__page = 0
        self.__typed = ""
        self.__too_big = False
        self.__message = ""

    def choose(self) -> PuzzleLayout:
        """Return the chosen layout, or None if the player quits"""
        try:
            while True:
                self.__draw()
                key = self.__read_key()
                if key in ("q", "Q") and self.__quit_confirmed():
                    return None
                layout = self.__handle(key)
                if layout:
                    return layout
        except KeyboardInterrupt:
            return None

    # Private functions

    def __draw(self) -> None:
        size = self.__page_size()
        pages = self.__page_count()
        self.__page = min(self.__page, pages - 1)
        first = self.__page * size
        page_note = f" (page {self.__page + 1} of {pages})" if pages > 1 else ""
        shown = self.__layouts[first : first + size]
        items = [f"  {number}. {layout.label()}" for number, layout in enumerate(shown, first + 1)]
        message = Display.term.yellow(self.__message) if self.__message else ""
        entry = self.__typed + (self.TOO_BIG_MARK if self.__too_big else "")
        lines = [f"Choose a puzzle layout{page_note}:", "", *items, "", message, self.__prompt(pages) + entry]
        Display.clear_screen()
        echo("\n".join(lines))

    def __page_size(self) -> int:
        return max(1, Display.term.height - self.RESERVED_LINES)

    def __page_count(self) -> int:
        return -(-len(self.__layouts) // self.__page_size())

    def __prompt(self, pages) -> str:
        paging = ", (p)revious, (n)ext" if pages > 1 else ""
        return f"Layout number (1-{len(self.__layouts)}) + ENTER{paging}, or (q)uit: "

    def __read_key(self) -> str:
        """Return the key pressed: its name (e.g. KEY_ENTER) for special keys, else the character"""
        with Display.term.cbreak():
            key = Display.term.inkey()
        return key.name if key.is_sequence else str(key)

    def __quit_confirmed(self) -> bool:
        """Ask on the menu's message line; only "y" or "Y" confirms"""
        self.__message = "Really quit? (y/n)"
        self.__draw()
        return self.__read_key() in ("y", "Y")

    def __handle(self, key) -> PuzzleLayout:
        """Act on one key; return the chosen layout once a playable one is entered"""
        self.__message = ""
        if key == "KEY_ENTER":
            return self.__chosen_layout()
        if key in ("n", "N", "p", "P"):
            self.__turn_page(1 if key in ("n", "N") else -1)
        elif key in ("KEY_BACKSPACE", "KEY_DELETE"):
            self.__backspace()
        elif key.isdigit():
            self.__type_digit(key)
        return None

    def __chosen_layout(self) -> PuzzleLayout:
        typed, too_big = self.__typed, self.__too_big
        self.__typed, self.__too_big = "", False
        number = int(typed) if typed else 0
        if too_big:
            self.__message = "Number too big"
            return None
        if not 1 <= number <= len(self.__layouts):
            self.__message = f"There is no layout {number}" if typed else "Type a layout number, then press ENTER"
            return None
        layout = self.__layouts[number - 1]
        if layout.is_broken():
            self.__message = f"{layout.label()} can't be started - choose another"
            return None
        return layout

    def __turn_page(self, step) -> None:
        self.__page = min(max(self.__page + step, 0), self.__page_count() - 1)

    def __backspace(self) -> None:
        """Remove the too-big mark if it is shown, otherwise the last digit"""
        if self.__too_big:
            self.__too_big = False
        else:
            self.__typed = self.__typed[:-1]

    def __type_digit(self, digit) -> None:
        if len(self.__typed) < self.MAX_DIGITS and not self.__too_big:
            self.__typed += digit
        else:
            self.__too_big = True
