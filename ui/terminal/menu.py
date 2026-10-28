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
    A menu on a cleared screen: a title, the items (MenuItem), as many as fit, then a message line and a line
    of key help.

    The selected item is shown in reverse video; up and down move to the next item that can be selected,
    scrolling a line at a time, and scroll a line instead when there is none, even past the selected item.
    While it is out of view, up and down only scroll, a hint says so, and ENTER brings it back into view;
    otherwise ENTER picks it if it is an item ENTER picks.  The selected item gets the keys the menu doesn't
    use (e.g. TAB for a choice).  While items are hidden above or below, a "---more---" line takes the top or
    bottom item line.  ESC or q leaves, first asking the quit question if there is one, and CTRL-C leaves at
    once.
    """

    RESERVED_LINES = 5  # title, blank line, blank line, message, key help
    MORE = "---more---"
    HINT = "ENTER brings the highlighted line back into view"
    LEAVE_KEYS = ("KEY_ESCAPE", "q", "Q")

    def __init__(self, title, items: list, keys_help, display: Display, quit_question=None):
        self.__title = title
        self.__items = items
        self.__keys_help = keys_help
        self.__display = display
        self.__quit_question = quit_question  # asked before leaving, when there is one; only "y" or "Y" confirms
        self.__selected = self.__next_selectable(-1, 1)  # index of the selected item, None when none can be
        self.__top = 0  # index of the first item shown
        self.__message = ""
        if self.__selected is not None:
            self.__bring_into_view(self.__selected)

    def choose(self):
        """Return the value of the item picked, or None if the player leaves or there is nothing to pick"""
        try:
            while True:
                self.__draw()
                key = self.__read_key()
                if key == "KEY_ENTER" and self.__is_selection_hidden():
                    self.__bring_into_view(self.__selected)
                elif key == "KEY_ENTER" and self.__selected is None:
                    return None
                elif key == "KEY_ENTER" and self.__items[self.__selected].is_picked_by_enter():
                    return self.__items[self.__selected].value
                elif key in self.LEAVE_KEYS and self.__leave_confirmed():
                    return None
                elif key in ("KEY_UP", "KEY_DOWN"):
                    self.__move(1 if key == "KEY_DOWN" else -1)
                elif self.__selected in self.__shown(self.__top):
                    self.__items[self.__selected].handle(key)
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
        """Return the item's text, indented: reversed when selected, else grayed out if the item says so"""
        term, item = self.__display.term, self.__items[index]
        text = item.text()
        if index == self.__selected:
            text = term.reverse(text)
        elif item.is_grayed_out():
            text = term.gray50(text)
        return item.INDENT + text

    def __read_key(self) -> str:
        """Return the key pressed: its name (e.g. KEY_ENTER) for special keys, else the character"""
        term = self.__display.term
        with term.cbreak():
            key = term.inkey()
            if key.name == "CSI" and term.inkey(timeout=0) == "Z":  # blessed reads Shift-TAB as "\x1b[" then "Z"
                return "KEY_BTAB"
        return key.name if key.is_sequence else str(key)

    def __leave_confirmed(self) -> bool:
        """Ask the quit question, if there is one, on the menu's message line; only "y" or "Y" confirms"""
        if self.__quit_question is None:
            return True
        self.__message = self.__quit_question
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
