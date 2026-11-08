# sudoku-solver

Play sudoku puzzles in the terminal - written in python.  The program shows each
cell's possible values and highlights conflicts as you play, and can point out
obvious moves (n) or make them all at once (a), and save and restore puzzles (s, o).

## Requirements

Once this git package is downloaded into a directory, the only two requirements are:
1. Python 3 is installed
1. Blessed (at least ver 1.20.0) - `pip install -r requirements.txt`

The terminal must use UTF-8 and be at least 80 columns by 29 lines, or 55 columns by 31 lines with `--no-panel` (see below).

## Playing

To play the game, simply `cd` to the top-level directory and run `python sudoku.py`.
On a narrow screen, such as a phone (Termux on Android), run `python sudoku.py --no-panel`
to leave out the command panel; `?` still lists the commands.

First you will get a GNU GPL splash page which will disappear in 5 seconds (or
with the first/any key press).  Then the screen size will be checked and ensured
to be large enough to support the puzzle.  Finally, you will enter the setup
screen (**SETUP** mode):
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
```
To the right of the grid, a command panel shows the current mode and its keys.
Below the grid, a status line shows hints, warnings and questions as you play.

### Setting up the Puzzle (**SETUP** mode)

Use the arrow keys and/or the hjkl keys (left, down, up, right) to move around.
Use the '?' to get help on possible commands.  Enter numbers in the squares
(I call them cells in the code) for the given numbers in your puzzle.  You
will notice that these numbers show up in purple on a lavender background.
Use the Delete or Backspace key to clear a cell.

When you are done, hit the ESC key to enter the **PLAY** mode.  If you
accidentally hit the ESC key before completing the puzzle, or you notice a
mistake or just want to change the given numbers, undo all your moves
and hit the ESC key again to re-enter **SETUP** mode.

### Solving the Puzzle (**PLAY** mode)

While you are solving the puzzle, the movement keys are the same as in setup
mode.  You will notice that the command panel has changed, showing you the
commands for playing.  For a longer description of every command, use the
**HELP** key (?).

Follow the Sudoku rules to solve the puzzle:
- The bottom line of each cell shows the values still possible for it (or `.....`
when more than 5 are possible).  Entering a value removes it from the possible
values of every cell in its row, column and box, and deleting, changing or
undoing it gives the value back.
- If you enter a number that is already in the same row, column or box, the cell
turns bold red on bright yellow, and the cells it clashes with get a yellow background.
- Enter a SHIFTED digit to make a guess.  Guesses, and every value entered after
them, get a gray background so you can see what depends on the guess.  Use "r"
to rewind back to the most recent guess and try a different one.

*[Not completed]*
Next (n) and auto (a) know only a few solving techniques so far.

See [UserGuide.md](UserGuide.md) for the full list of keys and colors.

## Testing

Run all the unit tests with `py -m pytest` (or `python -m pytest`), or run a single
test file directly, e.g. `python game/tests/cell_test.py`.  Each folder of code has
its tests in a `tests/` folder beside it.  Two tests are meant to be
watched: `ui/terminal/tests/display_test.py::TestDisplay` draws on the terminal and
`ui/terminal/tests/input_test.py` waits for a key press.

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
some guidance.  Each folder of code also has a `tests/` folder beside it (see Testing).

- sudoku.py - starts the program: picks the layout and the user interface; `Main` class, has entry point run()
- game/ - the game itself, which knows nothing about how it is shown
  - puzzle.py - the generic puzzle: the commands, modes and cursor; `Puzzle` class
  - moves.py - enters values and keeps them for undo/rewind and guess shading; `Moves` class
  - history.py - keeps the history of entries for undo; `History` and `Entry` classes
  - completion_report.py - tells the player when the puzzle is complete; `CompletionReport` class
  - game_file.py - the save and restore commands; `GameFile` class
  - save_file.py - writes and reads the versioned save file; `SaveFile` and `SavedPuzzle` classes
  - actions.py - what the player can ask the game to do, and which actions each mode offers; `Action` and `Mode`
  - user_interface.py - the port through which the game talks to the player; `UserInterface`, `Message` and `MessageKind`
  - board.py - the grid of cells, found through the blocks; `Board` class, the base class for layouts
  - puzzle_catalog.py - finds the available layouts; `PuzzleCatalog` class
  - puzzles/ - the puzzle layouts, one per file (new layouts go here)
    - board_3x3.py - the standard layout of nine 3x3 blocks; `Board3x3` class
  - rectangular_block.py - creates/manages a rectangular block of 3x3 cells; `RectangularBlock` class
  - house.py - a box, row or column, where a value can still go in it, and whether a missing value has no place left; `House` class
  - cell.py - creates/manages an individual cell; `Cell` class
  - cell_solver.py - keeps the possible values of a cell; `CellSolver` class
  - cell_attrs.py - what a cell's attributes mean (given, guess, solved, conflicts, guess depth); `CellAttrs` class
  - border.py - which sides of a cell lie on its block's edge; `Border` class
  - settings.py - every setting the player can configure, saved by name; `Settings` class
  - config_option.py - a setting the player can configure; `ConfigOption` class
  - marks_setting.py - which "must be" marks (Snyder notation) cells show; `MarksSetting` class
  - puzzle_solver.py - finds and makes the next obvious move (n) or all of them (a) by applying the solving rules; `PuzzleSolver` class
  - rules/ - the solving rules, one per file
    - order.py - sets the order the rules are applied in
    - rule.py - the base class of the rules, and the moves they find; `Rule` and `Move` classes
    - conflicts_rule.py - stops solving while values conflict; `ConflictsRule` class
    - dead_end_rule.py - stops solving at a dead end; `DeadEndRule` class
    - single_value_rule.py - only one value fits a cell; `SingleValueRule` class
    - hidden_single_rule.py - a value can go nowhere else in a house; `HiddenSingleRule` class
    - intersection_rule.py - the base of the next two rules; `IntersectionRule` class
    - pointing_pair_rule.py - finds pointing pairs; `PointingPairRule` class
    - box_line_rule.py - finds box/line reductions; `BoxLineRule` class
- ui/ - the ways of showing the game
  - error_log.py - keeps the details of errors the program survives, in sudoku.log; `ErrorLog` class
  - terminal/ - shows the game in a terminal, using Blessed
    - terminal_ui.py - the terminal's user interface: runs the play loop, draws the board and panel, shows messages and asks questions; `TerminalUI` class
    - display.py - manages the terminal display; `Display` class
    - display_attrs.py - turns cell attributes into terminal colors; `DisplayAttrs` class
    - input.py - manages keyboard input and decodes into a valid command; `Input` class
    - commands.py - the terminal's key bindings, command panel and help text; `Commands` class
    - copyright.py - the GNU GPL splash text; `Copyright` class
    - menu.py - a full-screen menu, used to choose a layout and to configure; `Menu` class
    - menu_item.py - the base class of menu lines; `MenuItem` class
    - menu_entry.py - a menu line that ENTER picks; `MenuEntry` class
    - menu_heading.py - a menu line naming a group; `MenuHeading` class
    - menu_note.py - a grayed-out menu line explaining the choice above it; `MenuNote` class
    - menu_choice.py - a menu line offering choices; `MenuChoice` class
    - keyboard_query.py - a small stand-alone tool that shows what each key sends
- tests/ - the tests that cover both game/ and ui/

#### Class Organization

Rather than drawing a UML (I'll leave that to the reader and IDE), see
[DesignDoc.md](DesignDoc.md), which describes all the classes and how they work together.
