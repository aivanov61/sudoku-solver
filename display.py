# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import functools

from blessed import Terminal

echo = functools.partial(print, end='', flush=True)

class Border:
    def __init__(self, borders=set()):
        self.__borders = borders

    def is_top(self):
        return 'top' in self.__borders

    def is_left(self):
        return 'left' in self.__borders

    def is_right(self):
        return 'right' in self.__borders

    def is_bottom(self):
        return 'bottom' in self.__borders

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
    geom = {'h_cells': None, 'v_cells': None}

    def geometry(geometry):
        Display.geom['h_cells'] = geometry['h_cells']
        Display.geom['v_cells'] = geometry['v_cells']

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
        min_width = Display.geom['h_cells'] * Display.CELL_WIDTH
        min_height = Display.geom['v_cells'] * Display.CELL_HEIGHT + 2
        while Display.term.width < min_width or Display.term.height < min_height:
            is_size_ok = False
            Display.clear_screen()
            print(f'The terminal must have at least {min_height} lines and {min_width} columns')
            print(f'It currently has {Display.term.height} lines and {Display.term.width} columns')
            echo('Please resize it and hit <ENTER> when ready or <CTRL-C> to quit: ')
            try:
                Display.term.inkey()
                Display.clear_screen()
            except:
                return is_size_ok
        return is_size_ok

    def draw_cell(row=0, col=0, border=Border()):
        x, y = Display.x(col), Display.y(row)
        echo(Display.term.move_xy(x, y))
        Display.__draw_top_line(border)
        for line_no in range(1, Display.CELL_HEIGHT):
            echo(Display.term.move_xy(x, y+line_no))
            Display.__draw_inner_line(border)
        echo(Display.term.move_xy(x, y+Display.CELL_HEIGHT))
        Display.__draw_bottom_line(border)

    def __draw_top_line(border):
        ulcorner = Display.fullblock if border.is_top() or border.is_left() else Display.bigplus
        hline = Display.fullblock if border.is_top() else Display.hline
        urcorner = Display.fullblock if border.is_top() or border.is_right() else Display.bigplus
        echo(ulcorner + hline * Display.CELL_HORIZONTAL_SIZE + urcorner)

    def __draw_inner_line(border):
        lvline = Display.fullblock if border.is_left() else Display.vline
        rvline = Display.fullblock if border.is_right() else Display.vline
        echo(lvline + ' ' * Display.CELL_HORIZONTAL_SIZE + rvline)

    def __draw_bottom_line(border):
        llcorner = Display.fullblock if border.is_bottom() or border.is_left() else Display.bigplus
        hline = Display.fullblock if border.is_bottom() else Display.hline
        lrcorner = Display.fullblock if border.is_bottom() or border.is_right() else Display.bigplus
        echo(llcorner + hline * Display.CELL_HORIZONTAL_SIZE + lrcorner)

    def draw_cell_value(row=0, col=0, value=' '):
        """Draw the value in the middle of the cell"""
        Display.move_to_cell(row, col)
        echo(str(value))

    def draw_cell_possible_values(row=0, col=0, values=[]):
        """Draw the possible values at the bottom of the cell"""
        values = values if len(values) <= Display.CELL_HORIZONTAL_SIZE else '.....'
        x = Display.x(col) + 1
        y = Display.y(row) + Display.CELL_VALUES_ROW
        echo(Display.term.move_xy(x, y))
        echo(' ' * (Display.CELL_HORIZONTAL_SIZE - len(values)))
        echo(''.join(str(v).translate(Display.small_nums) for v in values))

    def status_line_location():
        return 0, (Display.geom['v_cells'] or 0) * Display.CELL_HEIGHT + 1

    def move_to_status_line():
        echo(Display.term.move_xy(*Display.status_line_location()))

    def move_to_cell(row=0, col=0):
        """Move to the middle of the cell"""
        x = Display.x(col) + Display.CELL_WIDTH // 2
        y = Display.y(row) + Display.CELL_VALUE_ROW
        echo(Display.term.move_xy(x, y))

    def warn(msg):
        with Display.term.location(*Display.status_line_location()):
            echo(Display.term.clear_eol + Display.term.yellow(msg))

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

    small_nums = str.maketrans('1234567890', '₁₂₃₄₅₆₇₈₉₀')
    encircle = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ ', 'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ◯')
