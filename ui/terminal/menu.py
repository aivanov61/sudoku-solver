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

from ui.terminal.display import Display, echo


class Menu:
    """
    A menu on a cleared screen: a title, the items, as many as fit, then a message line and a line of key help.

    The selected item is shown in reverse video; up and down move to the next item that can be selected,
    scrolling a line at a time, and scroll a line instead when there is none, even past the selected item.
    While it is out of view, up and down only scroll, a hint says so, and ENTER brings it back into view;
    otherwise ENTER picks it.  While items are hidden above or below, a "---more---" line takes the top or
    bottom item line.  ESC or q asks "Really quit? (y/n)", and CTRL-C quits at once.
    """

    RESERVED_LINES = 5  # title, blank line, blank line, message, key help
    MORE = "---more---"
    HINT = "ENTER brings the highlighted line back into view"
    QUIT_KEYS = ("KEY_ESCAPE", "q", "Q")

    def __init__(self, title, items: list, keys_help, display: Display):
        self.__title = title
        self.__items = items
        self.__keys_help = keys_help
        self.__display = display
        self.__selected = self.__next_selectable(-1, 1)  # index of the selected item, None when none can be
        self.__top = 0  # index of the first item shown
        self.__message = ""
        if self.__selected is not None:
            self.__bring_into_view(self.__selected)

    def choose(self):
        """Return the value of the entry picked, or None if the player quits or there is nothing to pick"""
        try:
            while True:
                self.__draw()
                key = self.__read_key()
                if key == "KEY_ENTER" and self.__is_selection_hidden():
                    self.__bring_into_view(self.__selected)
                elif key == "KEY_ENTER":
                    return None if self.__selected is None else self.__items[self.__selected].value
                elif key in self.QUIT_KEYS and self.__quit_confirmed():
                    return None
                elif key in ("KEY_UP", "KEY_DOWN"):
                    self.__move(1 if key == "KEY_DOWN" else -1)
        except KeyboardInterrupt:
            return None

    # Private functions

    def __next_selectable(self, start, step) -> int:
        """Return the index of the first item past start, going by step, that can be selected, or None"""
        indexes = range(start + step, len(self.__items)) if step > 0 else range(start + step, -1, -1)
        return next((index for index in indexes if self.__items[index].is_selectable()), None)

    def __bring_into_view(self, index) -> None:
        """Scroll as little as needed for the item to be shown"""
        self.__top = min(self.__top, index)
        while index not in self.__shown(self.__top):
            self.__top += 1

    def __shown(self, top) -> range:
        """Return the indexes of the items shown from top, leaving room for a "more" line above or below"""
        count = self.__display.term.height - self.RESERVED_LINES - (top > 0)
        if top + count < len(self.__items):
            count -= 1
        return range(top, min(top + max(1, count), len(self.__items)))

    def __draw(self) -> None:
        shown = self.__shown(self.__top)
        message = self.__message or (self.HINT if self.__is_selection_hidden() else "")
        lines = [
            self.__title,
            "",
            *self.__more_line(shown.start > 0),
            *(self.__item_line(index) for index in shown),
            *self.__more_line(shown.stop < len(self.__items)),
            "",
            self.__display.term.yellow(message) if message else "",
            self.__keys_help,
        ]
        self.__display.clear_screen()
        echo("\n".join(lines))

    def __is_selection_hidden(self) -> bool:
        return self.__selected is not None and self.__selected not in self.__shown(self.__top)

    def __more_line(self, is_more) -> list:
        return [self.MORE] if is_more else []

    def __item_line(self, index) -> str:
        """Return the item's label: reversed when selected, grayed out when it can't be selected"""
        term, item = self.__display.term, self.__items[index]
        if index == self.__selected:
            return "  " + term.reverse(item.label)
        return "  " + (item.label if item.is_selectable() else term.gray50(item.label))

    def __read_key(self) -> str:
        """Return the key pressed: its name (e.g. KEY_ENTER) for special keys, else the character"""
        with self.__display.term.cbreak():
            key = self.__display.term.inkey()
        return key.name if key.is_sequence else str(key)

    def __quit_confirmed(self) -> bool:
        """Ask on the menu's message line; only "y" or "Y" confirms"""
        self.__message = "Really quit? (y/n)"
        self.__draw()
        self.__message = ""
        return self.__read_key() in ("y", "Y")

    def __move(self, step) -> None:
        """
        Select the next item that way that can be selected and bring it into view; scroll a line that way
        instead when there is none, or when the selected item is out of view
        """
        is_moving = self.__selected is not None and not self.__is_selection_hidden()
        found = self.__next_selectable(self.__selected, step) if is_moving else None
        if found is None:
            self.__scroll(step)
        else:
            self.__selected = found
            self.__bring_into_view(found)

    def __scroll(self, step) -> None:
        """Scroll a line that way, unless the first or last item is already shown"""
        self.__top = max(0, min(self.__top + step, self.__last_top()))

    def __last_top(self) -> int:
        """Return the first item shown when scrolled all the way down"""
        count = len(self.__items)
        return next((top for top in range(count) if self.__shown(top).stop == count), 0)
