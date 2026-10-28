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

import functools

from contextlib import contextmanager

from blessed import Terminal
from game.border import Border
from ui.terminal.display_attrs import DisplayAttrs as Attrs

echo = functools.partial(print, end="", flush=True)


class Display:
    """
    Provides the interface to display to the terminal: one object per terminal, created with its
    blessed Terminal (a new one if none is given).

    It establishes the screen size and is able to draw the basic elements
    of the Sudoku puzzle, including managing the keyboard input.

    - geometry(v_cells, h_cells) - set vertical and horizontal cell count
    - geom['h_cells'] = return number of horizontal cells
    - geom['v_cells'] = return number of vertical cells

    - clear_screen() - clears the screen and resets cursor to top-left
    - validate_screen_size() - ensure screen is large enough to manage the puzzle

    - draw_cell(row, col, border) - draw the cell outline, including thick border when needed
    - draw_cell_value(row, col, value) - draw the value of the cell in the middle of the cell
    - draw_cell_possible_values(row, col, values) - draw all the possible cell values at the bottom of the cell
    - draw_command_panel(title, entries) - draw the mode's title and its commands to the right of the puzzle

    - move_to_status_line() - move the cursor to the status line: one line below the puzzle
    """

    # Cell dimensions (internally fixed sizes to work on terminals)
    CELL_HORIZONTAL_SIZE = 5
    CELL_WIDTH = CELL_HORIZONTAL_SIZE + 1
    CELL_HEIGHT = 3
    CELL_VALUE_ROW = 1
    CELL_VALUES_ROW = 2

    # Command panel, to the right of the puzzle
    PANEL_GAP = 2
    PANEL_KEYS_WIDTH = 11
    PANEL_NAME_WIDTH = 8
    MIN_WIDTH = 80

    def __init__(self, term: Terminal = None):
        self.term = term or Terminal()  # the blessed terminal to draw on
        self.geom = {"h_cells": None, "v_cells": None}

    def geometry(self, v_cells, h_cells):
        """Set the size of the board, in cells"""
        self.geom["h_cells"] = h_cells
        self.geom["v_cells"] = v_cells

    def validate_screen_size(self):
        is_size_ok = True
        min_width = self.min_width()
        min_height = self.geom["v_cells"] * self.CELL_HEIGHT + 2
        while self.term.is_a_tty and (self.term.width < min_width or self.term.height < min_height):
            is_size_ok = False
            self.clear_screen()
            print(f"The terminal must have at least {min_height} lines and {min_width} columns")
            print(f"It currently has {self.term.height} lines and {self.term.width} columns")
            echo("Please resize it and hit <ENTER> when ready or <CTRL-C> to quit: ")
            try:
                self.term.inkey()
                self.clear_screen()
            except KeyboardInterrupt:
                return is_size_ok
        return is_size_ok

    def min_width(self) -> int:
        """The puzzle plus the command panel, and never less than 80 columns"""
        return max(self.MIN_WIDTH, self.__panel_x() + self.PANEL_KEYS_WIDTH + self.PANEL_NAME_WIDTH)

    def clear_screen(self):
        echo(self.term.home())
        echo(self.term.clear())

    def draw_cell(self, row=0, col=0, border=Border(), attrs=tuple()):
        x, y = self.x(col), self.y(row)
        echo(self.term.move_xy(x, y))
        self.__draw_edge_line(border.is_top(), border, attrs)
        for line_no in range(1, self.CELL_HEIGHT):
            echo(self.term.move_xy(x, y + line_no))
            self.__draw_inner_line(border, attrs)
        echo(self.term.move_xy(x, y + self.CELL_HEIGHT))
        self.__draw_edge_line(border.is_bottom(), border, attrs)

    # Cell location helpers
    def x(self, cell_col):
        """Return the screen column of the upper-left corner of the cell given its column relative to other cells"""
        return self.CELL_WIDTH * cell_col

    def y(self, cell_row):
        """Return the screen row of the upper-left corner of the cell given its row relative to other cells"""
        return self.CELL_HEIGHT * cell_row

    def draw_cell_value(self, row=0, col=0, value=" ", attrs=dict()):
        """Draw the value in the middle of the cell using the rendered attributes"""
        self.move_to_cell(row, col)
        echo(self.styled(str(value), attrs))

    def draw_cell_missing_value(self, row=0, col=0, value=" "):
        """Draw a value with no place left in the middle of the cell, in the missing value's colors"""
        self.move_to_cell(row, col)
        echo(getattr(self.term, Attrs.MISSING_VALUE)(str(value)))

    def move_to_cell(self, row=0, col=0):
        """Move to the middle of the cell"""
        x = self.x(col) + self.CELL_WIDTH // 2
        y = self.y(row) + self.CELL_VALUE_ROW
        echo(self.term.move_xy(x, y))

    def styled(self, text, attrs) -> str:
        """Return the text styled with the attributes' colors, e.g. (CellAttrs.SOLVED,) for steel blue"""
        return getattr(self.term, Attrs.render(attrs)) + text + self.term.normal

    def draw_cell_possible_values(self, row=0, col=0, values=[], attrs=dict()):
        """Draw the possible values at the bottom of the cell"""
        values = sorted(values) if len(values) <= self.CELL_HORIZONTAL_SIZE else "....."
        x = self.x(col) + 1
        y = self.y(row) + self.CELL_VALUES_ROW
        echo(self.term.move_xy(x, y))
        rendered_attrs = self.__rendered_bg_attrs(attrs)
        echo(rendered_attrs + " " * (self.CELL_HORIZONTAL_SIZE - len(values)) + self.term.normal)
        echo(rendered_attrs + "".join(str(v).translate(self.small_nums) for v in values) + self.term.normal)

    def draw_command_panel(self, title, entries):
        """Draw the title, then one command per line (its keys in red, then its name), clearing the rest beside the puzzle"""
        lines = [self.term.bold(title), ""]
        lines += [self.term.red(keys.ljust(self.PANEL_KEYS_WIDTH)) + name for keys, name in entries]
        for y in range(self.y(self.geom["v_cells"]) + 1):
            line = lines[y] if y < len(lines) else ""
            echo(self.term.move_xy(self.__panel_x(), y) + line + self.term.clear_eol)

    def move_to_status_line(self):
        echo(self.term.move_xy(*self.status_line_location()))

    def status_line_location(self):
        return 0, (self.geom["v_cells"] or 0) * self.CELL_HEIGHT + 1

    def warn(self, msg, wait=False):
        self.show_on_status_line(self.term.yellow(msg), wait=wait)

    def show_on_status_line(self, text, wait=False):
        """Show already styled text on the status line, waiting for a key if asked"""
        with self.__status_line_message(text):
            if wait:
                self.hit_any_key_to_continue()

    def hit_any_key_to_continue(self):
        echo("Hit any key to continue: ")
        try:
            with self.term.cbreak():
                self.term.inkey()
        except KeyboardInterrupt:
            pass

    def confirm(self, msg) -> bool:
        """Ask a yes/no question on the status line; only "y" or "Y" confirms"""
        with self.__status_line_message(self.term.yellow(msg + " (y/n) ")):
            try:
                with self.term.cbreak():
                    return self.term.inkey() in ("y", "Y")
            except KeyboardInterrupt:
                return False

    def ask(self, msg, default="", suffix="") -> str:
        """
        Ask for a line of text on the status line, starting from the default, with the suffix shown after it.
        The arrows move the cursor within the text, never into the suffix; ENTER accepts the text (without the
        suffix), ESC cancels (None).
        """
        text, cursor = default, len(default)
        try:
            with self.term.cbreak():
                while True:
                    with self.__status_line_message(self.term.yellow(f"{msg} {text}{suffix}")):
                        self.__move_cursor_left(len(text) - cursor + len(suffix))
                        key = self.term.inkey()
                    if key.name in ("KEY_ENTER", "KEY_ESCAPE"):
                        return text if key.name == "KEY_ENTER" else None
                    text, cursor = self.__edited(text, cursor, key)
        except KeyboardInterrupt:
            return None

    # Private functions

    def __panel_x(self) -> int:
        """The screen column where the command panel starts: past the puzzle's right edge and a gap"""
        return self.x(self.geom["h_cells"]) + 1 + self.PANEL_GAP

    def __draw_edge_line(self, is_edge, border, attrs):
        """Draw the top or bottom line of a cell; is_edge tells whether it lies on the block's outer edge"""
        left = self.__border_char(is_edge or border.is_left(), self.bigplus, attrs)
        line = self.__border_char(is_edge, self.hline, attrs)
        right = self.__border_char(is_edge or border.is_right(), self.bigplus, attrs)
        echo(left + line * self.CELL_HORIZONTAL_SIZE + right)

    def __border_char(self, is_outer, inner_char, attrs) -> str:
        return Attrs.outer_border(self.fullblock, attrs) if is_outer else Attrs.inner_border(inner_char, attrs)

    def __draw_inner_line(self, border, attrs):
        left = self.__border_char(border.is_left(), self.vline, attrs)
        right = self.__border_char(border.is_right(), self.vline, attrs)
        rendered_str = self.__rendered_bg_attrs(attrs) + " " * self.CELL_HORIZONTAL_SIZE + self.term.normal
        echo(left + rendered_str + right)

    def __rendered_bg_attrs(self, attrs) -> str:
        return getattr(self.term, Attrs.render_bg(attrs))

    @contextmanager
    def __status_line_message(self, text):
        """Show the styled text on the status line, keeping the cursor there until the block ends"""
        with self.term.location(*self.status_line_location()):
            echo(self.term.clear_eol + text)
            yield

    def __move_cursor_left(self, count):
        if count:
            echo(self.term.move_left(count))

    def __edited(self, text, cursor, key) -> tuple:
        """
        Return the text and the cursor after a key: the arrows move the cursor, backspace removes the character
        before it and delete the one at it, other special keys are ignored, and any other key is inserted at it
        """
        if key.name == "KEY_LEFT":
            return text, max(cursor - 1, 0)
        if key.name == "KEY_RIGHT":
            return text, min(cursor + 1, len(text))
        if key.name == "KEY_BACKSPACE":
            return text[: max(cursor - 1, 0)] + text[cursor:], max(cursor - 1, 0)
        if key.name == "KEY_DELETE":
            return text[:cursor] + text[cursor + 1 :], cursor
        if key.is_sequence:
            return text, cursor
        return text[:cursor] + key + text[cursor:], cursor + 1

    # These character symbols are re-used from https://github.com/thisisparker/cursewords/blob/master/cursewords/characters.py
    vline = "│"
    hline = "─"

    llcorner = "└"
    ulcorner = "┌"
    lrcorner = "┘"
    urcorner = "┐"

    ttee = "┬"

    btee = "┴"
    ltee = "├"
    rtee = "┤"

    bigplus = "┼"

    lhblock = "▌"
    rhblock = "▐"
    fullblock = "█"
    squareblock = rhblock + fullblock + lhblock

    small_nums = str.maketrans("1234567890", "₁₂₃₄₅₆₇₈₉₀")
    encircle = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ ", "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ◯")
