# sudoku-solver

Play sudoku puzzles in the terminal - written in python.  The program shows each
cell's possible values and highlights conflicts as you play; auto-solving with
hints is planned.

## Requirements

Once this git package is downloaded into a directory, the only two requirements are:
1. Python 3 is installed
1. Blessed (at least ver 1.20.0) - `pip install -r requirements.txt`

The terminal must use UTF-8 and be at least 54 columns by 29 lines.

## Playing

To play the game, simply `cd` to the top-level directory and run `python sudoku.py`

First you will get a GNU GPL splash page which will disappear in 5 seconds (or
with the first/any key press).  Then the screen size will be checked and ensured
to be large enough to support the puzzle.  Finally, you will enter the initialization
screen (**INIT** mode):
```text
███████████████████████████████████████████████████████
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
█─────┼─────┼─────█─────┼─────┼─────█─────┼─────┼─────█
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
█─────┼─────┼─────█─────┼─────┼─────█─────┼─────┼─────█
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
███████████████████████████████████████████████████████
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
█─────┼─────┼─────█─────┼─────┼─────█─────┼─────┼─────█
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
█─────┼─────┼─────█─────┼─────┼─────█─────┼─────┼─────█
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
███████████████████████████████████████████████████████
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
█─────┼─────┼─────█─────┼─────┼─────█─────┼─────┼─────█
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
█─────┼─────┼─────█─────┼─────┼─────█─────┼─────┼─────█
█     │     │     █     │     │     █     │     │     █
█     │     │     █     │     │     █     │     │     █
███████████████████████████████████████████████████████
HELP=?, #=1-9/shift=guess, UP=k/^, DOWN=j/v, LEFT=h/<, RIGHT=l/>, QUIT=q/CTRL-C, DEL=Delete, PLAY=ESC [initializing]
```
Notice at the bottom of the play field is a status line which will display
information during game setup and playing and also provides command hints.

### Initializing the Puzzle (**INIT** mode)

Use the arrow keys and/or the hjkl keys (left, down, up, right) to move around.
Use the '?' to get help on possible commands.  Enter numbers in the squares
(I call them cells in the code) for the given numbers in your puzzle.  You
will notice that these numbers show up in purple on a lavender background.
Use the Delete key to clear a cell.

When you are done, hit the ESC key to enter the **PLAY** mode.  If you
accidentally hit the ESC key before completing the puzzle, or you notice a
mistake or just want to change the initialization values, undo all your moves
and hit the ESC key again to re-enter **INIT** mode.

### Solving the Puzzle (**PLAY** mode)

While you are solving the puzzle, the movement keys are the same as in initialization
mode.  You will notice that the status line has changed, showing you different
command options.  There are some **hidden** commands that do not show up in the
status line for two reasons: 1) It would make the status line very long, 2) they
are not common commands.  To see these, use the **HELP** key (?).

Follow the Sudoku rules to solve the puzzle:
- The bottom line of each cell shows the values still possible for it (or `.....`
when more than 5 are possible).  Entering a value removes it from the possible
values of every cell in its row, column and box.
- If you enter a number that is already in the same row, column or box, the cell
turns bold red on yellow.
- Enter a SHIFTED digit to make a guess.  Guesses, and every value entered after
them, get a gray background so you can see what depends on the guess.  Use "u"
to undo back to it.

*[Not completed]*
Rewind (r), auto-play (a) and next (n) are listed in the help but not implemented
yet.  Possible values are not given back when a value is deleted, undone or
changed, and the cell that a conflicting number clashes with is not highlighted
yet.

See [UserGuide.md](UserGuide.md) for the full list of keys and colors.

## Testing

Run all the unit tests with `py -m pytest` (or `python -m pytest`), or run a single
test file directly, e.g. `python tests/cell_test.py`.  Two tests are meant to be
watched: `tests/display_test.py::TestDisplay` draws on the terminal and
`tests/input_test.py` waits for a key press.

## Purpose and Design

The purpose of writing this program is three-fold:
1. I've been playing Sudoku on paper books with a pen - I want a "soft" puzzle
2. I enjoy coding, especially Clean Code (SOLID principles)
3. Provide an example of Python, OO, Clean Code (for others and for criticism)

### The code

First, a few observations I have generally about Clean Code.  I have noticed over
the years, that clean code will have certain look and feel.  Generally:
- Small(er) classes
- Many files (since I try to do one file per class)
- Lots of "includes" (or "import"s in Python)
- Sometimes difficult to identify the flow through the code
- Unit testing is helpful to:
  - Provide simple way to test embedded operations/functions
  - Guide new coders on how stuff is supposed to work and how to use it
- Test Driven Development (TDD) is super-useful for coding the building blocks!
- Using an IDE is **extremely** helpful since it helps drill into and back out
of functions which are often in different files (I've been using VSCode lately)

#### File layout

When looking at the code for this Sudoku puzzle solver, this list will give you
some guidance:
- sudoku.py - plays the game, handles the flow; `Main` class, has entry point run()
- puzzle_3x3.py - creates/manages a 3x3 rectangular block Sudoku puzzle
of 3x3 cells per block; `Puzzle3x3` class
- rectangular_block.py - creates/manages a rectangular block of 3x3 cells; `RectangularBlock` class.
- cell.py - creates/manages an individual cell; `Cell` class
- cell_solver.py - keeps the possible values of a cell; `CellSolver` class
- commands.py - establish the commands for the puzzle; `Commands` class
- display.py - manages the terminal display; `Display` class
- display_attrs.py - turns cell attributes into terminal colors; `DisplayAttrs` class
- history.py - keeps the history of entries for undo; `History` and `Entry` classes
- input.py - manages keyboard input and decodes into a valid command; `Input` class
- copyright.py - the GNU GPL splash text; `Copyright` class

#### Class Organization

Rather than drawing a UML (I'll leave that to the reader and IDE), here is an
explanation of a few of the classes.  [DesignDoc.md](DesignDoc.md) describes
all of them and how they work together.

#### Main

This class is instantiated in sudoku.py and drives the Sudoku program.  Driving
the Sudoku program entails:
1. Handling the GNU GPL notice
1. Instantiating the Puzzle object
1. Rendering the puzzle
1. Entering the *play* loop
1. Cleaning up and exiting when the *play* is over

#### Display

Initializes the `blessed` terminal and provides class functions for manipulating
the display.  Key functions/attributes in this class are:

- term - an instance of the `blessed` Terminal()
- geometry() - establish the horizontal and vertical sizes of the puzzle
- geom - access the geometry `h_cells` and `v_cells` (horizontal and vertical respectively)
- CONSTANTS for the puzzle cell sizes
- y() - return the terminal y offset for a given row
- x() - return the terminal x offset for a given column
- clear_screen() - as the name suggests
- validate_screen_size() - makes sure terminal is big enough; forces resizing until it is
- draw_cell() - Draws the cell outline/background, sans the values
- draw_cell_value() - Draws the current cell value with color/attributes
- draw_cell_possible_values() - Draws the sorted values possible for the cell (or `.....` if there are too many to fit in the cell)
- move_to_status_line() - Move the cursor to the first character of the status line (one line below the puzzle cells)
- move_to_cell() - Move to the 'center' of the cell (where the value will be printed)
- warn() - Display a warning in yellow on the status line

#### Input

Get terminal input and decode it using the commands given. It relies on commands
given in a specific format (see Commands below).  It provides a single function:

- get_cmd() - Wait for, and get, keyboard input.  It handles exceptions and CTRL-C
(keyboard interrupt) and returns a valid command.  Keyboard input that is not
recognized is ignored.
