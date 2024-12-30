# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import functools

from blessed import Terminal
from display_attrs import DisplayAttrs as Attrs

echo = functools.partial(print, end="", flush=True)


class Border:
    TOP = "top"
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"

    def __init__(self, borders=set()):
        self.__borders = borders

    def is_top(self):
        return self.TOP in self.__borders

    def is_left(self):
        return self.LEFT in self.__borders

    def is_right(self):
        return self.RIGHT in self.__borders

    def is_bottom(self):
        return self.BOTTOM in self.__borders


class Display:
    """
    Provides the interface to display to the terminal.

    It establishes the screen size and is able to draw the basic elements
    of the Sudoku puzzle, including managing the keyboard input.

    - geometry(geom) - set horizontal and vertical cell count
    - geom['h_cells'] = return number of horizontal cells
    - geom['v_cells'] = return number of vertical cells

    - clear_screen() - clears the screen and resets cursor to top-left
    - validate_screen_size() - ensure screen is large enough to manage the puzzle

    - draw_cell(row, col, border) - draw the cell outline, including thick border when needed
    - draw_cell_value(row, col, value) - draw the value of the cell in the middle of the cell
    - draw_cell_possible_values(row, col, values) - draw all the possible cell values at the bottom of the cell

    - move_to_status_line() - move the cursor to the status line: one line below the puzzle
    """

    # Initialize terminal and set basic configuration
    term = Terminal()
    geom = {"h_cells": None, "v_cells": None}

    def geometry(geometry):
        Display.geom["h_cells"] = geometry["h_cells"]
        Display.geom["v_cells"] = geometry["v_cells"]

    # Cell dimensions (internally fixed sizes to work on terminals)
    CELL_HORIZONTAL_SIZE = 5
    CELL_WIDTH = CELL_HORIZONTAL_SIZE + 1
    CELL_HEIGHT = 3
    CELL_VALUE_ROW = 1
    CELL_VALUES_ROW = 2

    # Cell location helpers
    def y(cell_row):
        """Return the screen row of the upper-left corner of the cell given its row relative to other cells"""
        return Display.CELL_HEIGHT * cell_row

    def x(cell_col):
        """Return the screen column of the upper-left corner of the cell given its column relative to other cells"""
        return Display.CELL_WIDTH * cell_col

    def clear_screen():
        echo(Display.term.home())
        echo(Display.term.clear())

    def validate_screen_size():
        is_size_ok = True
        min_width = Display.geom["h_cells"] * Display.CELL_WIDTH
        min_height = Display.geom["v_cells"] * Display.CELL_HEIGHT + 2
        while Display.term.width < min_width or Display.term.height < min_height:
            is_size_ok = False
            Display.clear_screen()
            print(f"The terminal must have at least {min_height} lines and {min_width} columns")
            print(f"It currently has {Display.term.height} lines and {Display.term.width} columns")
            echo("Please resize it and hit <ENTER> when ready or <CTRL-C> to quit: ")
            try:
                Display.term.inkey()
                Display.clear_screen()
            except:
                return is_size_ok
        return is_size_ok

    def draw_cell(row=0, col=0, border=Border(), attrs=dict()):
        x, y = Display.x(col), Display.y(row)
        echo(Display.term.move_xy(x, y))
        Display.__draw_top_line(border, attrs)
        for line_no in range(1, Display.CELL_HEIGHT):
            echo(Display.term.move_xy(x, y + line_no))
            Display.__draw_inner_line(border, attrs)
        echo(Display.term.move_xy(x, y + Display.CELL_HEIGHT))
        Display.__draw_bottom_line(border, attrs)

    def draw_cell_value(row=0, col=0, value=" ", attrs=dict()):
        """Draw the value in the middle of the cell using the rendered attributes"""
        Display.move_to_cell(row, col)
        rendered_attrs = Display.__rendered_attrs(attrs)
        echo(rendered_attrs + str(value) + Display.term.normal)

    def move_to_cell(row=0, col=0):
        """Move to the middle of the cell"""
        x = Display.x(col) + Display.CELL_WIDTH // 2
        y = Display.y(row) + Display.CELL_VALUE_ROW
        echo(Display.term.move_xy(x, y))

    def draw_cell_possible_values(row=0, col=0, values=[], attrs=dict()):
        """Draw the possible values at the bottom of the cell"""
        values = values if len(values) <= Display.CELL_HORIZONTAL_SIZE else "....."
        x = Display.x(col) + 1
        y = Display.y(row) + Display.CELL_VALUES_ROW
        echo(Display.term.move_xy(x, y))
        rendered_attrs = Display.__rendered_bg_attrs(attrs)
        echo(rendered_attrs + " " * (Display.CELL_HORIZONTAL_SIZE - len(values)) + Display.term.normal)
        echo(rendered_attrs + "".join(str(v).translate(Display.small_nums) for v in values) + Display.term.normal)

    def move_to_status_line():
        echo(Display.term.move_xy(*Display.status_line_location()))

    def status_line_location():
        return 0, (Display.geom["v_cells"] or 0) * Display.CELL_HEIGHT + 1

    def warn(msg, wait=False):
        with Display.term.location(*Display.status_line_location()):
            echo(Display.term.clear_eol + Display.term.yellow(msg))
            wait and Display.hit_any_key_to_continue()

    def hit_any_key_to_continue():
        echo("Hit any key to continue: ")
        try:
            with Display.term.cbreak():
                Display.term.inkey()
        except:
            pass

    def __draw_top_line(border, attrs):
        ulcorner = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_top() or border.is_left()
            else Attrs.inner_border(Display.bigplus, attrs)
        )
        hline = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_top()
            else Attrs.inner_border(Display.hline, attrs)
        )
        urcorner = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_top() or border.is_right()
            else Attrs.inner_border(Display.bigplus, attrs)
        )
        echo(ulcorner + hline * Display.CELL_HORIZONTAL_SIZE + urcorner)

    def __draw_inner_line(border, attrs):
        lvline = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_left()
            else Attrs.inner_border(Display.vline, attrs)
        )
        rvline = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_right()
            else Attrs.inner_border(Display.vline, attrs)
        )
        rendered_str = Display.__rendered_bg_attrs(attrs) + " " * Display.CELL_HORIZONTAL_SIZE + Display.term.normal
        echo(lvline + rendered_str + rvline)

    def __draw_bottom_line(border, attrs):
        llcorner = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_bottom() or border.is_left()
            else Attrs.inner_border(Display.bigplus, attrs)
        )
        hline = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_bottom()
            else Attrs.inner_border(Display.hline, attrs)
        )
        lrcorner = (
            Attrs.outer_border(Display.fullblock, attrs)
            if border.is_bottom() or border.is_right()
            else Attrs.inner_border(Display.bigplus, attrs)
        )
        echo(llcorner + hline * Display.CELL_HORIZONTAL_SIZE + lrcorner)

    def __rendered_attrs(attrs) -> str:
        return getattr(Display.term, Attrs.render(attrs))

    def __rendered_bg_attrs(attrs) -> str:
        return getattr(Display.term, Attrs.render_bg(attrs))

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
