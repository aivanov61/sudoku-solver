# Sudoku: Design Document

This document explains how the terminal Sudoku program is built: its layers, how a keystroke becomes a change on screen, and the conventions the code follows. It is written for developers working on the code. For how to play, see the User Guide.

## 1. Purpose and scope

The program lets a player type in a published 9x9 Sudoku puzzle and then solve it in the terminal. It helps by showing each cell's remaining possible values and by marking conflicting entries. Guesses are shaded so the player can see what depends on them and undo back to them.

The code is also meant as an example of clean, object-oriented Python built with test-driven development. The structure is designed to grow to other Sudoku layouts: each layout is a small subclass of `Board` in the `game/puzzles/` folder, found automatically by `PuzzleCatalog`, and played by the one generic `Puzzle`. Today only the standard layout of 3x3 boxes exists, in `game/puzzles/board_3x3.py`.

## 2. Current status

| Area | Status |
|---|---|
| Entering initial values, moving around, help, quit | Working |
| Guesses with gray shading | Working |
| Undo | Working |
| Possible values | Removed from the row, column and box when a value is entered, and given back when it is deleted, undone or changed, unless another related cell still holds it. An emptied cell works out its whole set again. |
| Conflict marking | The cell just entered is marked `CONFLICTING` (bold red on bright yellow), and every related cell already holding the value is marked `CONFLICTED` (its usual color on yellow). Marks clear when the value is deleted, changed or undone, once no related cell still holds it. |
| Rewind (`r`) | Working |
| Next (`n`) | Working for single values and hidden singles (see 5.6) |
| Auto (`a`) | Working: makes every move `n` would, one after another (see 5.6) |
| Save and restore (`s`, `o`) | Working (see 5.8) |
| "Must be" marks | Working: shown in empty cells, configured with `c` (see 5.9) |
| Tags (`m`) | Working: a tagged empty cell shows its small digits in steel blue (see 5.10) |
| Redo | Not implemented. |

## 3. Running and testing

- **Requirements:** Python 3 (currently developed on 3.15) and `blessed` 1.20 or later (`pip install -r requirements.txt`).
- **Run:** `python sudoku.py` from the project folder.
- **Terminal size:** at least 80 columns × 29 lines (9 cells × 6 columns plus the command panel; 9 cells × 3 lines, plus 2 for the status line). `Display.min_width()` asks for the grid plus the panel, but never less than 80. A message too long for the status line is split at words onto the lines below it, never into the last column or past the last line, so the screen never scrolls (`term.wrap()`, which keeps the colours); with no lines left, the last one is cut short with "…". With the panel there is no line to spare at the minimum height, so a long message there is cut, unless its short text fits. With `--no-panel` (`Display(panel=False)`, from `Main`'s command line, read with `argparse`), the minimum width is the grid's own (55 columns) and the minimum height has two more lines (`STATUS_LINES_WITHOUT_PANEL`, 31 for a 9x9), so long messages, such as `n`'s hints, have room to wrap: `TerminalUI` draws no panel, shows every message whole (never its short text), and shows the mode in gray on a blank status line (`MODE_HINT`, "PLAY - ? for commands"). Every message, `TerminalUI.status()` included, goes through `Display.show_on_status_line()`, which clears to the end of the screen first (`clear_eos`), so a message that wrapped leaves nothing behind; with `wait`, the "Hit any key to continue" prompt is part of the text that wraps.
- **Tests:** `py -m pytest` from the project folder, or run one file directly, for example `py game/tests/cell_test.py`. The tests use `unittest` and pytest runs them unchanged. Each folder of code has its tests in a `tests/` folder beside it (`game/tests/`, `game/rules/tests/`, `ui/terminal/tests/`); the top-level `tests/` holds the tests that cover both packages. The test folders are packages, so shared helpers are imported as, for example, `game.tests.recording_ui`. Note:
  - `ui/terminal/tests/display_test.py::TestDisplay` draws on the real terminal and pauses for a second after each test. `ui/terminal/tests/input_test.py` waits up to two seconds for a key press. Both are meant for watching by hand. Select the other files or classes to skip them.

## 4. Architecture

### 4.1 Layers

```
Main (sudoku.py)  ── gets the layout from PuzzleCatalog, then has the user interface (TerminalUI) play the puzzle:
                     TerminalUI reads commands via Input and hands each action to puzzle.handle()
  └── Puzzle                  the game: commands, modes, cursor, screen; helpers do moves, solving, completion, files
        └── Board3x3 (a Board)    Board: finding and asking about cells; Board3x3: only the 3x3 block layout
              └── RectangularBlock ×9   knows its cells and which lie in a given row or column
                    └── Cell ×9          holds a value, attributes (CellAttrs) and a CellSolver; reports its changes
                          └── CellSolver  holds the set of possible values
```

Supporting modules:

| Module | Class | Role |
|---|---|---|
| `game/actions.py` | `Action`, `Mode`, `OFFERED_ACTIONS` | What the player can ask the game to do, the modes, and which actions each mode offers |
| `ui/terminal/commands.py` | `Commands` | The terminal's key bindings: keys, command panel lines and help text for each action, plus the help screen |
| `ui/terminal/input.py` | `Input` | Reads keystrokes and turns the next bound one into a command |
| `game/user_interface.py` | `UserInterface`, `Message`, `MessageKind` | The port through which the game talks to the player (section 4.4) |
| `ui/terminal/terminal_ui.py` | `TerminalUI` | The terminal's implementation of the port: runs the play loop, draws the board, the command panel and the help screen, and shows messages and questions on the status line |
| `game/border.py` | `Border` | Which sides of a cell lie on its block's edge (layout data) |
| `game/marks_setting.py` | `MarksSetting` | Which "must be" marks (Snyder notation) cells show, and the options the player configures them with |
| `game/config_option.py` | `ConfigOption` | A setting the player can configure: its group, name, choices and the value chosen |
| `game/settings.py` | `Settings` | Every setting the player can configure, offered, chosen and saved by name; a new setting is listed in `KINDS` |
| `game/house.py` | `House` | A box, row or column: a group of cells that must hold every value once, where a value can still go in it, and whether a missing value has no place left |
| `ui/terminal/display.py` | `Display` | All terminal drawing, through `blessed` |
| `game/cell_attrs.py` | `CellAttrs` | What a cell's attributes mean: how its value got there, conflict marks, guess depth |
| `ui/terminal/display_attrs.py` | `DisplayAttrs` | The terminal's style table: turns a cell's attributes into `blessed` style names |
| `game/history.py` | `History`, `Entry` | The undo stack |
| `game/moves.py` | `Moves` | Enters values, records them in its own `History` for undo and rewind, and keeps the guess shading |
| `game/save_file.py` | `SaveFile`, `SavedPuzzle`, `SaveFileError` | Writes and reads the versioned save file |
| `ui/terminal/copyright.py` | `Copyright` | The GPL splash text |
| `ui/error_log.py` | `ErrorLog` | Appends the traceback of each error the program survives to `sudoku.log`, for any user interface |
| `game/puzzle.py` | `Puzzle` | The game, played on a board: commands, modes, cursor and screen. Hands work to the helpers below |
| `game/board.py` | `Board` | The grid of cells: finds cells through the blocks and answers questions about them; an abstract base class for layouts |
| `game/completion_report.py` | `CompletionReport` | Tells the player when the puzzle becomes complete, solved or with errors |
| `game/game_file.py` | `GameFile` | The save and restore commands: file name prompt, confirmations and messages |
| `game/puzzles/` | one module per layout | e.g. `board_3x3.py` with `Board3x3` |
| `game/puzzle_catalog.py` | `PuzzleCatalog`, `PuzzleLayout` | Finds the layouts and reports any that are broken |
| `ui/terminal/menu.py` | `Menu` | A full-screen menu: up/down select, "---more---" scrolling; used to choose a layout and to configure |
| `ui/terminal/menu_item.py` | `MenuItem` | The base class of menu lines: text, selectable, grayed out, picked by ENTER, keys it takes |
| `ui/terminal/menu_entry.py` | `MenuEntry` | A menu line that ENTER picks, standing for a value |
| `ui/terminal/menu_heading.py` | `MenuHeading` | A menu line naming the group below it; never selected |
| `ui/terminal/menu_note.py` | `MenuNote` | A grayed-out menu line explaining the choice above it; never selected |
| `ui/terminal/menu_choice.py` | `MenuChoice` | A menu line offering choices, changed with TAB, Shift-TAB, right and left |
| `game/puzzle_solver.py` | `PuzzleSolver` | Applies the solving rules in order to find the next move; carries out next (`n`) and auto (`a`) |
| `game/rules/` | one module per rule, plus `rule.py` and `order.py` | `Rule`, `Outcome` and the rules; `order.py` sets the order |

`ui/terminal/keyboard_query.py` is a standalone `blessed` experiment that shows what each key sends; it is not part of the program.

The code is in two packages: `game/` is the game, which knows nothing about how it is shown, and `ui/terminal/` is the terminal user interface. `sudoku.py` (`Main`) stays at the top and puts them together. `tests/package_boundary_test.py` checks that nothing in `game/` imports from `ui` or `blessed`.

### 4.2 Responsibilities between layers

Blocks decide which cells are related; cells act on them:

- **A block** gives a cell its *houses* (the groups of cells that must each hold every value once) through the generator `houses_of(row, col)`: a `House` for its own box first, then one for the row and one for the column, with the cells it gets from the board. Each house has a `kind` (`box`, `row` or `column`, for hints) and `places(value)`, the cells that can still hold the value. From the houses the block gives a cell its *related cells* (every other cell in the same box, row or column, once each) through the generator `related_cells(row, col)`. Besides that, it gives cells the legal `values()`.
- **A cell** acts on its related cells directly: it gives them back an old value (`add_possible`), removes a new one (`remove_possible`), and marks or clears conflicts (`mark_conflicted`, `clear_resolved_conflict`). It checks whether a related cell holds a value with `any()`, which stops at the first match. New cross-cell behavior is added to `Cell` alone, so blocks, the board and the puzzle stay unchanged.
- **The board** knows only its block layout. Its methods for blocks, `cells_in_row(row)` and `cells_in_col(col)`, yield from every block's method of the same name. Each block decides which of its own cells are in the row or column. The board passes those cells along but never reads or changes them, because in other Sudoku layouts the blocks may not form a regular grid, and only a block knows which of its cells lie in a given row or column.
- **The puzzle** reaches cells only through its board: `first_cell_where`, `is_full`, `has_conflicts`, `has_values`, `givens`, `clear` and `cells`.
- **Changes travel up:** a cell never draws itself. Whenever its value, attributes, possible values, marks or tag change, it calls its parent's `cell_changed(cell)`; the block passes that on to the board, and the board to the listener the puzzle gave it with `report_changes_to()`: the user interface's `cell_changed()`. A full draw is the puzzle's `render()`, which hands the board's `cells()` to the user interface's `show_board()`.
- **The one exception** is a cell by position. The cursor moves by row and column, and a Sudoku's outer edge is always rectangular, so the board offers `cell(row, col)` (through the layout's `_block_at`) for the selected cell and for replaying a saved game. Revisit this if a puzzle with a non-rectangular outer edge is ever designed.

Each class groups its methods under comments naming who calls them, for example `# Interface required for cells` in `RectangularBlock` and `# Interface required for related cells` in `Cell`, with private methods last under `# Private functions`.

### 4.3 Coordinates

Every cell stores its **puzzle-wide** `row` and `col` (0–8), set by `RectangularBlock.__phys_pos` when the block creates it. All requests between layers use these puzzle-wide positions. That's why a block can pick out "its cells in row 6 or column 8" without knowing where it sits relative to the cell that asked. `RectangularBlock.cell(row, col)` accepts puzzle-wide positions and reduces them with `%`.

### 4.4 Where the architecture is headed: the game apart from the display

**Goal:** the gameplay is generic and independent of how it is shown. The terminal is one user interface; a true GUI should be addable later without changing any gameplay code. The structure for this is *ports and adapters*: the game (the core) talks to the player only through one interface it defines, `UserInterface` (the port), and each way of showing the game is an adapter that implements it (`TerminalUI` today, a GUI later). The work is done step by step; section 8 tracks progress, and until it is finished the rest of this document describes the code as it is.

**The port.** Dialogs stay synchronous: the game asks a question and gets the answer back, which a GUI can do with modal dialogs. A first sketch, to be refined as the steps are done:

```python
class UserInterface(Protocol):
    def show_board(self, cells) -> None: ...               # full draw: every cell, with its block edges
    def cell_changed(self, cell) -> None: ...              # the moment a cell changes; redraw what differs
    def select(self, row, col) -> None: ...
    def mode_changed(self, mode, actions) -> None: ...     # e.g. the terminal's command panel
    def status(self, message) -> None: ...                 # shown until the next command; None blanks it
    def inform(self, message) -> None: ...                 # must be acknowledged before going on
    def confirm(self, question) -> bool: ...
    def ask_file_name(self, prompt, default) -> str | None: ...
    def configure(self, options) -> list: ...              # the options (ConfigOption) as the player chose them
    def guess_depth_changed(self, depth) -> None: ...      # every change; the interface decides what to show
```

A message is a `Message(text, kind)`; `MessageKind` is `INFO`, `WARNING`, `SUCCESS` or `HINT`. The port, `Message` and `MessageKind` are in `user_interface.py`. `status`, `inform`, `confirm` and `ask_file_name` exist since step 1, `guess_depth_changed` since step 2, `show_board` and `cell_changed` since step 3, `mode_changed` since step 4, and `configure` with the configure menu. A user interface reads the puzzle's `selected_cell` after each action; a `select()` method that tells it of every change can be added if a user interface needs one.

**What belongs where:**

| The game (core) | A user interface (adapter) |
|---|---|
| Actions: enter a value or a guess, move, undo, rewind, next, auto, save, open, quit, switch mode | Which keys, clicks or menus trigger each action, and the help text describing them |
| Receiving one action at a time: `game.handle(action)` | The main loop: reading input and calling the game (a GUI toolkit owns its own event loop) |
| A cell's state: value, kind (given, typed, guess, solved), conflict marks, guess depth, possible values | Colors and shading for each kind and depth, and what to do when it runs out of shades |
| Which sides of a cell are block edges | How edges are drawn |
| Which cells changed, as they change | Redrawing what differs from what it last showed |
| Messages as plain text with a kind (warning, success, hint) and whether they must be acknowledged, plus any value with no place left and the cell to show it in | Styling messages, how they are acknowledged, and how a missing value is shown in its cell (the terminal: white on red, until the message goes) |
| The list of layouts | The layout menu, startup notes and screen-size checks |
| The save file format | File-name prompts or file dialogs |

**Tests** use a `RecordingUI` that implements the port and records what the game asked it to do, instead of patching `Display` by name. It also serves as the contract any new interface must meet. `tests/package_boundary_test.py` checks that no game module imports a user-interface module.

**Out of scope here:** an event-driven model, in which ports and adapters connect every object rather than just the game and its interface. That would be a separate experiment.

## 5. Key flows

### 5.1 Startup and the main loop (`sudoku.py`)

1. Create the `Display`, the one object that draws on the terminal, and ask `PuzzleCatalog` for the available layouts.
2. Show the GPL splash; continue after 5 seconds or any key. The key is read in cbreak mode, like every other key, and any further keys pressed during the splash are dropped, so none of them reaches the layout menu (outside cbreak, a Windows console leaves part of ENTER behind, which the menu would take as ENTER). With a single layout that is broken, or with no layouts at all, a yellow note under the splash says so.
3. Pick the layout: with several, a `Menu` of them lets the player choose (see 5.7); with one, it is used directly. If the player quits the menu, or the only layout is broken or missing, exit here.
4. Create the board, the user interface and the puzzle: `TerminalUI(display, board.v_cells, board.h_cells)` sets the display's geometry from the board's size, checks the screen size and creates the `Input` that reads keys from the display's terminal; `Puzzle(board, ui)` announces setup mode and creates its helpers (`Moves` creates its own, empty `History`). The board's `__init__` builds its blocks (9 blocks of 9 cells for `Board3x3`).
5. `ui.play(puzzle)` runs the game. It first calls the puzzle's `render()`, which shows the whole board (through the user interface's `show_board()`, which also draws the command panel) and the status line.
6. Then it loops while `puzzle.is_playing`: re-check the screen size (render again if it was resized), move the cursor to the puzzle's `selected_cell`, read a command and carry it out (see 5.2).

### 5.2 Command dispatch

- **Actions** (`actions.py`) are what the player can ask the game to do. Each `Action`'s value names the puzzle method that does it, plus `_` (for example `Action.UP` is `up_()`), so it can't clash with Python reserved words; a test checks that `Puzzle` has a method for every action. `OFFERED_ACTIONS` lists the actions each `Mode` offers. The puzzle announces its mode and those actions to the user interface with `mode_changed()`.
- **Commands** (`commands.py`) belong to the terminal: `Commands.BINDINGS` lists, in command panel order, each command's keys, its panel label and name, and its help text. A command is an action, or `Commands.HELP`, the terminal's own help screen. `Commands.command_for(key, offered)` returns `(command, digit)`: a key always maps to its command, even where the mode doesn't offer it, so the puzzle can refuse it with its warning; a key bound to a command in each mode (`ESC`: `PLAY` in setup, `INIT` while playing) maps to the one the mode offers. Digits give `VALUE` and shifted digits `GUESS`, with the digit.
- `Input.get_cmd(offered)` reads keys until one is bound and returns its command. Unknown keys are ignored. CTRL-C or any input error gives `FORCE_QUIT`, which stops at once without asking; `q` gives `QUIT`, which asks for confirmation.
- `TerminalUI` shows the help screen itself, then has the puzzle render again. It hands every action to `puzzle.handle(action, digit)`, the game's one entry point for the player's actions.
- `handle()` first lets the puzzle react to actions in general (any action ends a notice and the completion report, and any action but `n` cancels a pending `n` move), then calls the puzzle's method for the action with `getattr`, passing the digit for `VALUE` and `GUESS`, and then shows the status.
- If `handle()` raises an exception, `TerminalUI` appends its traceback to `sudoku.log` (`ErrorLog.record()`; `*.log` is ignored by git) and warns, waiting for a key, what broke, why and where: e.g. "This puzzle's "up" command is broken: KeyError: 5 - at game/puzzle.py:123 in up_ (details in sudoku.log)", where the place is the innermost one on the error's stack (`ErrorLog.where()`). The warning may wrap and scroll the screen, so the whole game is then shown again and play goes on. If the failing action was `QUIT` or `FORCE_QUIT`, it forces the game to stop instead (`force_quit_()`).
- `except` clauses name what they catch: `KeyboardInterrupt` where CTRL-C cancels a prompt or the splash, and `(KeyboardInterrupt, Exception)` in `Input`, where anything wrong with the terminal quits; nothing catches `SystemExit`.

### 5.3 Entering a value

```
Puzzle.value_(val) / guess_(val)   (guess_ is refused in setup mode, like the other play-only actions)
  ├─ refuse to change an INITIAL cell in play mode (warning)
  ├─ Moves.enter(cell, val, GUESS or None)
       ├─ guess (in play mode) → one guess deeper
       ├─ attributes           → INITIAL (init mode) or the primary attribute, plus the guess depth if any
       ├─ play mode            → History.add(Entry(cell, new value, previous value))
       └─ Cell.set(val, attrs)
                 ├─ a related cell holds the value? → add CONFLICTING (even if the value is unchanged)
                 └─ value changed → __smart_update(value)
                      ├─ assign the new value (before notifying, so related cells see the board as it now is)
                      ├─ for each cell in parent.related_cells(row, col), in one pass:
                      │    ├─ old value → cell.add_possible(...)              takes it back if it is empty and
                      │    │                                                  none of its own related cells holds it
                      │    ├─ old value → cell.clear_resolved_conflict(...)   drops its mark if it holds the value and
                      │    │                                                  none of its own related cells holds it
                      │    ├─ new value → cell.remove_possible(...)           removes it
                      │    └─ new value → cell.mark_conflicted(...)           is marked CONFLICTED if it holds it
                      ├─ new value → the cell clears its own possible values
                      └─ no value  → the cell adds back every value no related cell holds
                 └─ value or attributes changed → report the change (parent.cell_changed(cell))
  └─ __found_dead_end()   DeadEndRule's move, if any: select its cell and set the notice
                          (the rule's warning in play mode, the setup warning in init mode)
```

- A cell reports a change only when something actually changed: its value or attributes (in `set()`), or its possible values (each related cell, as it gains or loses one).
- `TerminalUI` remembers what it last drew for each cell. On `cell_changed()` it redraws the whole cell if the attributes changed, otherwise only the value or the possible values that differ, and both lines of small digits (marks and possible values) if the tag changed.

**Conflicts** are worked out from the values on the board, never from a cell's possible values. A cell checks its related cells (its box first, then the row and column). Its own position is never among them, so its current value never counts against it. The same check decides whether a value can be given back: a cell regains a value only if no related cell holds it, so a duplicate left on the board keeps the value blocked.

### 5.4 Modes

- **Initialization mode** (the start mode): values get `INITIAL` and are not recorded in `History`. `Delete` clears a cell. Setup offers no guesses and no `u`, `r`, `a` or `n`: they are left out of the panel and the help, and their keys only warn "This works only while playing - ESC starts playing." `ESC` calls `play_()`, which is refused while any cell is marked in conflict ("Resolve the conflicts before playing.") or while an empty cell has no possible values (it selects that cell and shows "This square has no possible values left - change the setup before playing." as a notice, the same check and warning that follow every value entered in setup and restoring a game saved in setup), so play never starts from a broken setup.
- **Play mode:** values are recorded in `History`. `ESC` calls `init_()`, which is refused while there is anything to undo ("Cannot initialize puzzle while playing - undo everything first."). `Delete` is mapped to `del_()` only to show a warning.

### 5.5 Undo and guess shading

- `History` is a list of `Entry(cell, valueinfo, previous_valueinfo)`; each `Moves` creates and owns one, so there is no shared, global history. `ValueInfo` stores the value and its primary attribute (`INITIAL`, `GUESS` or `None`).
- `Moves` (`moves.py`) is the only code that uses its `History`; the puzzle's `undo_()` and `rewind_()` call its `undo()` and `rewind()`, which return the cell for the cursor.
- `undo_()` pops the last entry, moves the cursor to that cell and restores the previous value with `cell.set()`. With nothing to undo, it warns "Cannot undo initialized puzzle. ESC will re-enter initialization mode."
- `rewind_()` undoes at least one entry, then keeps undoing until the most recent remaining entry is a guess (primary attribute `GUESS`), or until the history is empty. The guess stays on the board and the cursor moves to it, ready for a different value to be typed over it. Pressing `r` again undoes that guess and rewinds to the one before. It uses `History.last()` to look at the most recent entry without removing it. With nothing to undo, it gives the same warning as `undo_()`. Otherwise it asks for confirmation first, since a rewind can't be undone.
- **Guess shading:** each guess makes the guess depth kept by `Moves` one deeper. Every value entered afterwards, guess or not, carries that depth, which shows what depends on the guess; undoing a guess makes it one shallower. The terminal shows depth as gray: `DisplayAttrs.GRAY_STEP` (10) lighter per guess, up to `MAX_GRAY_LEVEL` (100). Deeper than that it reuses the last shade. `Moves` reports every change of depth through the user interface's `guess_depth_changed()`, and `TerminalUI` warns "No more shades of gray left - repeating last shade." whenever the depth goes from within the shades to beyond the last one; deeper guesses stay quiet, and coming back within the shades lets it warn again. The game itself never knows about shades.

### 5.6 Next: the obvious next move

`n` teaches as it goes, in two steps. The first press asks the puzzle's `PuzzleSolver` for the next move, moves the cursor to its cell and shows *why* on the status line, in steel blue like the solved values. The second press fills it in. The next press starts over with the following move.

The solver consults the rules listed in `game/rules/order.py`, in that order, and takes the move of the first one that has one:

1. **`ConflictsRule`** (`[conflicts]`): if any cell carries a conflict mark, the move is the warning "Resolve the conflicts first."
2. **`DeadEndRule`** (`[dead end]`): if an empty cell has no possible values, or else a value missing from a box, row or column has no place left there (`Cell.unplaceable_value()`, through `House.has_no_place_for()`), the cursor moves to that cell (for a missing value, the first empty cell of such a house) and the warning is "Dead end; try either undoing or rewinding-back-to-a-previous-guess." For a missing value, the move also carries the value and the house: `Move.missing()` gives `(cell, value)`, which goes into the warning's `Message.missing`, so the user interface shows the value in the cell for as long as the warning (`status()` until the next command, `inform()` until a key). In setup mode the puzzle words its own warning from the move, e.g. "4 has no place left in this row - change the setup before playing."
3. **`SingleValueRule`** (`[single value]`): a cell whose only possible value is left; the hint is "Only 9 fits here: every other value is already in its row, column or box."
4. **`HiddenSingleRule`** (`[hidden single]`): a value that can go in only one cell of a box, row or column (a *hidden single*); the hint is "4 fits nowhere else in its box." (or row, or column). `Cell.hidden_single()` looks through the cell's houses, box first, for the lowest value whose only place (`House.places()`) is the cell. It comes after `SingleValueRule`, because a cell with one possible value is the simpler explanation when both apply.

5. **`PointingPairRule`** (`[pointing pair]`) and 6. **`BoxLineRule`** (`[box/line reduction]`): a value that, within one house (the *source*), can only go where it crosses a house of another kind can go nowhere else in that other house, so it is ruled out of the rest of it. A pointing pair's source is a box (the value is confined to one row or column of it); a box/line reduction's source is a row or column (the value is confined to one box). Both are `IntersectionRule` subclasses (`intersection_rule.py`), which do the work: `eliminations(puzzle)` goes through `puzzle.houses()`, and for each value with two or more places left in a source, finds the house of another kind holding them all (`Cell.houses()` of the first place) and rules the value out of that house's other places; the subclass says which houses are sources (`_is_source()`) and why (`_reason()`, e.g. "in one box, 4 can only go in one row"). `find()` then looks for a cell that only the eliminations force: one candidate left (hint "Only 9 fits here: in one box, 4 can only go in one row, which rules 4 out here.") or a hidden single among the candidates ("4 fits nowhere else in its column: in one box, 4 can only go in one row."). A cell forced without them is left to the singles, which come first. Each rule finds a move only from its own eliminations.

Every hint ends with the name of the rule that found it, in brackets: "4 fits nowhere else in its box. [hidden single]". Each rule has a `NAME`, and builds its move with `Rule._move()`, which adds the name; so the warning the puzzle shows itself after an entry (from `DeadEndRule`) carries it too.

The first two *stop* solving: every `n` repeats their warning, and there is nothing to fill in. If no rule has a move, `next_()` warns "No obvious next move. You'll have to make a guess."

- **Rules** live in `game/rules/`, one file each. Each is a `Rule` subclass with `find(puzzle)`, which returns a `Move` or `None` without changing anything, and `eliminations(puzzle)`, which returns `{(cell, value): why}` for each value it rules out of a cell now (none, `{}`, for most rules). Eliminations are never stored: nothing is taken out of a cell's possible values, so undo, rewind and saving need nothing new. `PuzzleSolver.ruled_out()` gathers every rule's eliminations; `Cell.candidates(ruled_out)` is a cell's possible values less those ruled out of it, and `forced_value()`, `hidden_single()` and `House.places()` take the same `ruled_out`. A `Move` holds its `outcome` (`MOVED` for a value to fill in, `STOPPED` for a warning), its `hint` (the explanation or the warning), its `cell` and its `value`. Rules that stop solving come before rules that make moves. A test checks that every rule in `rules/` is listed in `game/rules/order.py`.
- **The solver** has `find_move()` (the first rule's move) and `make_move(move)` (fill in its value through the puzzle). It also carries out the commands: `next()` points out a move, keeping it as its *pending move*, and the following `next()` makes it; `auto()` makes moves until none is obvious. The puzzle's `next_()` and `auto_()` first refuse in setup mode or on a complete puzzle, then call these.
- **Cancelling:** `handle()` lets the puzzle react to every action before carrying it out. Any action other than `n` drops the pending move (`PuzzleSolver.cancel_pending_move()`), so the following `n` points out a move again instead of filling one in. Keys the program does not recognize are ignored as before and cancel nothing.
- **The puzzle's interface for the solver:** `first_cell_where(condition)` returns the first cell, left to right and top to bottom, for which the condition holds (it asks every block's `cells_where()`, so only blocks look inside cells, as section 4.2 requires); `houses()` returns every house of the board (each block's `box()`, then every row and column from `cells_in_row()` and `cells_in_col()`); `select(cell)` moves the cursor; `enter_solved_value(cell, value)` enters a value; `is_complete()` tells `auto()` not to warn once it has filled in the last cell. The other helpers use the same section of the puzzle (`Interface required for the solver and the other helpers`): `is_initializing()`, `has_conflicts()`, `has_values()`, `saved_state()` and `restore(saved)`.
- **Auto (`a`):** `PuzzleSolver.auto()` makes moves with `find_move()` and `make_move()` while they are `MOVED`, selecting each move's cell, without hints. It ends with the same warning `n` would give: the stopping rule's warning, or the one about making a guess. Each move is a separate `History` entry, so `u` takes them back one at a time.
- **Notices:** a dead-end warning does not wait for a key. The puzzle keeps it as a notice (a `WARNING` message), which `display_status()` passes to the user interface's `status()` ahead of the completion report and the `n` hint, until `command_received()` clears it at the next command. (A `Display.warn()` that does not wait would be overwritten at once, because `Main` redraws the status line after every command.)
- **A complete puzzle:** in play mode, once `first_cell_where` finds no empty cell, `CompletionReport` (`completion_report.py`) gives `display_status()` the message that the puzzle is solved (steel blue), or complete with errors (yellow) if any cell is marked in conflict. The report replaces the status line until the next command, and comes back only when the completion changes (including back to unfinished, after undo or rewind empties a cell). With errors, the advice is to undo or change values. `n` and `a` then only warn that the puzzle is already complete; values can still be typed over. When `a` fills in the last cell it ends without a warning.
- **Making the move:** a `SOLVED` value goes through the same path as a typed value, so it is recorded in `History` with `SOLVED` as its primary attribute. `u` and `r` treat it like any other non-guess entry, and undoing a change restores the steel blue. It also picks up the current guess shading.
- **Adding a rule** means a new file in `game/rules/` and one line in `game/rules/order.py`; nothing else changes. A rule about whole boxes, rows or columns asks each cell about its houses, as `HiddenSingleRule` does through `Cell.hidden_single()`, or goes through every house with `houses()`, as the intersection rules do. An abstract base class shared by rules (such as `IntersectionRule`) is not listed in `order.py`.
- **Rules and several layouts (planned, not built yet):** today every layout uses the shared list in `game/rules/order.py`. The intended direction:
  - **Shared rules stay shared** by working through units the layout supplies (the groups of cells that must each hold every value once: rows, columns and boxes, or a jigsaw's regions, an X-Sudoku's diagonals, and so on), the way `related_cells` already comes from the blocks.
  - **Layout-specific rules** (such as Killer Sudoku cage sums) live with their layout, for example in a `game/puzzles/<layout>/` package, rather than in the shared `rules/` folder.
  - **A layout chooses its rules** through a `RULES` class attribute that defaults to the shared order; a variant lists shared and its own rules together, in order, and `Puzzle` passes `self.RULES` to its `PuzzleSolver`.
  - Build this when the first layout that needs its own rules arrives.

### 5.7 Layouts and the catalog

- **`Board`** (`board.py`) is an abstract base class (`abc.ABC`) holding everything about cells that does not depend on the block layout. A layout subclass sets `NAME`, calls `super().__init__(v_cells, h_cells)`, builds its blocks with the board as their parent, and implements the two `@abstractmethod` hooks `_blocks()` and `_block_at(row, col)`. Python refuses to create a layout that is missing a hook. `Puzzle` is not a base class: one generic game plays every layout, so every layout has every command.
- **`PuzzleCatalog.available()`** imports every module in `game/puzzles/` and returns a `PuzzleLayout` for each `Board` subclass that has its own `NAME` (classes without one, such as shared base classes, are skipped), sorted by name. A new layout is just a new file there.
- **Notes for the player:** a layout is *broken* if its file cannot be loaded or a hook is missing (the class is still abstract). `PuzzleLayout.label()` shows this after the name, e.g. "Jigsaw (broken: missing _block_at)". Detecting it never creates the board, so it has no side effects. A test checks that `Puzzle` has a method for every `Action`.
- **With one layout**, its note, if any, is shown under the splash screen; a broken layout then exits instead of starting.
- **With several layouts**, `Main` lists them all with their notes after the splash, in a `Menu` (`menu.py`) of `MenuEntry` lines (`menu_entry.py`), each standing for its layout. A broken layout's entry can't be picked: it is grayed out and skipped.
- **`Menu`** clears the screen and shows a title, the items, a message line and a line of key help. Each item is a `MenuItem` (`menu_item.py`), which gives its text and indent and says whether it can be selected, is grayed out, or is picked by ENTER; each kind of line is a subclass, so a new kind (such as a typed-in number) is a new class: `MenuEntry` (picked by ENTER, grayed out and skipped when it can't be picked), `MenuHeading` (never selected), and `MenuChoice` and `MenuNote` (see 5.9). The selected item is in reverse video, starting at the first that can be selected. Up and down move to the next one that can be selected (doing nothing at either end); when there is none that way, they scroll a line instead, so grayed-out items at the ends come into view, even if the selection scrolls off the screen. While it is out of view, up and down only scroll (moving the selection would jump the view back to it), the message line says "ENTER brings the highlighted line back into view", and ENTER does just that, scrolling as little as needed, as when the menu opens; a second ENTER picks it. As many items are shown as fit the terminal's height; while some are hidden above or below, a "---more---" line takes the top or bottom item line, and it goes away at the first or last item. Otherwise ENTER picks the selected item if it is one ENTER picks (an entry or a choice), and does nothing on any other; with nothing selectable, nothing is selected and ENTER returns nothing, so the program exits. Any other key goes to the selected item, if it is in view. ESC or q leaves the menu, first asking the menu's quit question on the message line if it has one (the layout menu asks "Really quit? (y/n)"; only y confirms), and CTRL-C leaves at once. blessed reads Shift-TAB (`ESC [ Z`) as an unnamed `CSI` and a `Z`, so the menu puts them back together as `KEY_BTAB`.

### 5.8 Saving and restoring

- **`SavedPuzzle`** (`save_file.py`) holds everything needed to rebuild a puzzle: the layout's `NAME`, the mode, the `Settings`, the selected cell, the tagged cells as `(row, col)`, the givens as `(row, col, value)`, and the moves, one per `History` entry, as `(row, col, value, prim_attr)`, oldest first. Shading, conflict marks and possible values are not saved; replaying the moves rebuilds them. A file without `tags` is read with none, so adding them needed no new version.
- **`SaveFile`** writes it as JSON: `{"format": "sudoku-save", "version": 2, "state": {...}}`. The settings are saved by name, each as plain data from its `saved()`: `"settings": {"marks": {"threshold": 2, "kinds": ["box"], "whole_puzzle": false}}`. Reading checks the format marker and the structure, and raises `SaveFileError` with a message for the player if the file is missing, isn't a save file, or is damaged. A version newer than `SaveFile.VERSION` raises an error suggesting the player update the program.
- **Changing the format:** raise `VERSION` and add an entry to `SaveFile.UPGRADES` that converts the previous version's `state` dictionary to the new one. Reading applies the upgrades one version at a time, so files from any older version still load; an upgrade that fails on a damaged file makes it damaged. Version 2 turns marks off with `whole_puzzle` instead of the threshold: a version 1 file's marks that were off (`"threshold": null`) come back with threshold 2 in tagged cells only, and marks that were on come back in the whole puzzle, so they look as they did. Adding a setting is not a change of format: a setting missing from a file is read as its default (so files saved before the settings existed come back with marks in tagged cells only), and an older program reading a newer file skips the entries it doesn't know: `SaveFile` walks the whole file, settings included, against what this version writes (with every setting at its default) and lists each unknown entry by its dotted path (`state.settings.marks.style`) in `SavedPuzzle.ignored`, which is never written, and `GameFile` warns after restoring with a `Message` whose `short` text only counts them; `TerminalUI` shows the short text when the whole text doesn't fit the terminal's width, less the "Hit any key to continue: " prompt. `MarksSetting` refuses a threshold, kinds or whole puzzle switch its options don't offer, so a hand-edited setting makes the file damaged rather than breaking the configure menu.
- **Where files go:** `SaveFile.located(name)` puts a name without a folder in `SaveFile.FOLDER` (`saved_games`, relative to where the program runs); a name with any folder, even `.`, is used as given. `SaveFile.write()` creates `saved_games` when it is missing, but no other folder. `GameFile` remembers the name as typed and shows the located path in its messages. `saved_games/` is in `.gitignore`.
- **Save (`s`)** warns "Nothing to save - the board is empty." if no cell has a value; otherwise it asks for a file name with the user interface's `ask_file_name(prompt, default, extension)`, offering the last name saved or restored, without its extension (`GameFile.DEFAULT_FILE_NAME`, `sudoku`, at first), and passing `SaveFile.EXTENSION` (`.json`), which the player never types. On the terminal, `Display.ask(msg, default, suffix)` shows the extension after the name, with the cursor before it; the arrows move the cursor within the name, Backspace and Delete remove the character before or at it, and typed characters are inserted at it. `TerminalUI` adds the extension to the name it returns, and an empty name counts as cancelled. `GameFile` then confirms before replacing an existing file. The puzzle's `saved_state()` builds the `SavedPuzzle`; givens are the cells whose attributes include `INITIAL`.
- **Restore (`o`)** reads the file first, so a bad file or one from another layout only warns and changes nothing. If the board has any values, it then confirms. `GameFile.restore()` hands the `SavedPuzzle` to the puzzle's `restore(saved)`, which empties and untags every cell, clears the moves, enters the givens in setup mode, switches to the saved mode, replays the moves through `Moves.enter()`, the same path as typed and solved values, and tags the saved cells. Undo, rewind and guess shading then work as if the moves had just been made. After redrawing, it points out any dead end the same way as after a typed value (selecting the first one and showing a notice).

### 5.9 "Must be" marks (Snyder notation)

A "must be" mark shows, in an empty cell, a value that has only a few places left in one of the cell's houses, this cell among them: what solvers call Snyder notation. A value with one place is a hidden single (5.6).

- **`MarksSetting`** (`marks_setting.py`, frozen) says which marks to show: each value with at most `threshold` places (2 to 5, 2 by default) in one of the cell's houses of the given `kinds`: `BOX_ONLY` (the default), or `EVERY_HOUSE` (box, row and column); and where: in every empty cell that isn't tagged when `whole_puzzle` is on, otherwise (the default) in none. Kind and threshold apply only to these Snyder marks; tagged cells show what they must be instead. Per box is the default because two marks in a box always mean "one of these two"; marks from rows and columns can be misread as pairs when two of them line up from different houses. `options()` gives the player's two `ConfigOption`s (`config_option.py`), both in the group "Must-be marks (Snyder notation)", naming the technique so that players can look it up: "Kind of house" (box, or box, row or column), "Threshold" (2 to 5 or fewer places) and "Whole puzzle" (off or on), as set now; `from_options()` makes the setting back from them as chosen. It is saved as `{"threshold": ..., "kinds": [...], "whole_puzzle": ...}` by `saved()` and read back by `from_saved()`.
- **`Settings`** (`settings.py`, frozen) keeps every setting by its kind's `NAME` (the marks are `"marks"`), each starting as its default. `options()` gives every setting's options, one setting after another, and `from_options()` hands each setting back its own; `saved()` and `from_saved()` do the same for the save file. `Puzzle` holds one `Settings` and asks it for the marks with `of(MarksSetting)`. A new setting is a class with `NAME`, a default, `options()`, `from_options()`, `saved()` and `from_saved()`, listed in `Settings.KINDS`; `Puzzle`, `SavedPuzzle` and the save file format stay as they are.
- **Cells keep their marks.** `Cell.refresh_marks(setting)` works them out: none with no setting (`None`); what the cell must be once it is tagged; otherwise its Snyder marks from the cell's houses (`House.places()`) when the setting's `whole_puzzle` is on. It keeps them and reports a change, like any other change, only when they differ; `marks()` gives them to the user interface. A filled cell has no possible values, so it has no marks.
- **The puzzle refreshes them after every command:** `handle()` calls `Board.refresh_marks()` with the setting while playing, and with `None` in setup mode, so no cell shows marks there, tagged or not, so a mark that changes because of a change anywhere in its houses (an entry, undo, rewind, auto, a restore) is always current, and the marks come back when play resumes.
- **`c`** (`Action.CONFIGURE`, offered in both modes) calls `configure_()`, which hands the settings' options to the user interface's `configure()`, makes the settings from the options it returns, refreshes the marks and shows the board afresh (`render()`). Nothing is said on the status line, since changing the marks changes no value.
- **The configure menu:** `TerminalUI.configure()` shows a `Menu` titled "Configure" with a `MenuHeading` before the first option of each group and a `MenuChoice` (`menu_choice.py`) for each option, and, under an option with notes, a `MenuNote` (`menu_note.py`). A choice shows its name dotted out to a fixed width, the label chosen and where it is among them, e.g. "Threshold .......... 2 or fewer places (1 of 4)"; TAB or right moves to the next choice and Shift-TAB or left to the previous one, going round at either end. ENTER on any choice picks it, and `configure()` returns the options with the choices made; the menu has no quit question, so ESC (or q) cancels at once, and `configure()` returns the options as they were. Either way the puzzle shows the board afresh.
- **Notes:** a `ConfigOption` can carry a note for each choice (`notes`, `""` for none). Only the user interface knows the keys, so a note names the key for an action as `{key}`, with the action in `note_action`; `TerminalUI` fills it in with `Commands.label_for()`. The `MenuNote` under the choice shows the note for the choice made, following it as TAB changes it, and stays as a blank line for a choice without one, so the lines below never move. The marks' "Whole puzzle" option has a note for each choice, naming the tag key (`m`).
- **The terminal** draws the marks on an empty cell's middle line with `Display.draw_cell_marks()`, in the small digits of the possible values: spaced while they fit (up to 3), closed up for 4 or 5, and `.....` beyond that. `TerminalUI` treats the middle line as one: whenever the value or the marks change, it draws the marks (a blank line for a filled cell, which has none) and then the value on top, so neither overwrites the other however their changes are reported. It remembers the marks with the rest of what it last drew.

### 5.10 Tags

- **Cells keep their tag.** `Cell.set_tagged(tagged)` tags or untags the cell, reporting a change only when it differs, and `is_tagged()` tells the user interface. The tag has nothing to do with the cell's value or attributes, so entering, deleting, undoing or rewinding a value leaves it, and `Moves` never records it.
- **`m`** (`Action.TAG`, offered in both modes) calls `tag_()`, which toggles the tag of the selected cell. While playing, a tagged cell shows what it must be in place of marks, whatever the marks setting (5.9); `handle()` refreshes the marks after the tag changes, so they show at once.
- **What a tagged cell must be** looks one step ahead, at what is forced now, and leaves out the values the rules rule out (`PuzzleSolver.ruled_out()`, which `Puzzle` passes through `Board.refresh_marks()` to each cell while playing). `Cell.forced_value()` gives the value a cell is forced to hold: its single possible value, or else its hidden single (`hidden_single()`), or `None`. A tagged cell with a forced value shows just that value; otherwise it shows its candidates less those forced into its related cells, which each answer `forced_value()`. It never follows the chain of forced values (as `a` would), so it gives away no more than the next move. Each new rule's eliminations take more values out, so tagged cells sharpen without any change to how they are drawn.
- **The board** gives the tagged cells' positions with `tags()`, for the save file, and `clear()` untags every cell as well as emptying it, so a restore starts with no tags.
- **The terminal** draws a tagged cell's small digits, its marks and its possible values, in `DisplayAttrs.TAGGED_COLOR` (steel blue) on the cell's background, with `DisplayAttrs.render_small_digits(attrs, tagged)`. A filled cell has no small digits, so its tag doesn't show until the value goes. `TerminalUI` remembers the tag with the rest of what it last drew.

## 6. Display

- **Cell layout:** each cell is 6 columns by 3 lines. The top line is the border (shared with the cell above), the middle line shows the value (or an empty cell's "must be" marks, see 5.9), and the bottom line shows the possible values. Box edges use full blocks (`█`); inner lines use `│`, `─` and `┼`.
- **Possible values** are drawn in increasing order as subscript digits. When there are more than 5, `.....` is shown instead. A tagged cell's small digits are steel blue (see 5.10).
- **Attributes:** a cell's attributes are a tuple whose meanings are defined, for the game, by `CellAttrs`; `DisplayAttrs`, the terminal's style table, turns them into `blessed` style names such as `purple_on_lavender` or `bold_red_on_bright_yellow`. There are two kinds:
  - *Primary* attributes (at most one per cell): `INITIAL` gives purple on lavender, `GUESS` gives green on the current gray, and `SOLVED` (values filled in by `n`) gives steel blue on the current gray.
  - *Optional* attributes: `CONFLICTING` gives bold red on bright yellow. `CONFLICTED` gives the primary color on yellow, so the newest entry stands out from the cells it clashes with. A cell carries at most one of the two; `CONFLICTING` wins.
  - Values with no primary attribute are drawn in `darkorange3`.
  - The guess depth travels in the attribute tuple as `{"depth": n}`; the terminal shows it as `gray{10 × n}`, at most `gray100`.
- `Display` is an object: `Main` creates one, `Display(term)` with a `blessed` `Terminal` (a new one if none is given), and passes it to the layout `Menu` and `TerminalUI`, which passes it to `Input`. It keeps its terminal (`term`) and the board size (`geom`, set with `geometry(v_cells, h_cells)`). Tests hand `TerminalUI`, `Input` and `Menu` a stand-in display, and `Display` a stand-in terminal, instead of patching classes.
- **Command panel:** `Display.draw_command_panel(title, entries)` draws the mode's title (SETUP or PLAY) and one command per line to the right of the grid, keys in red, then clears the rest of every line beside the grid. `Commands.panel(offered)` lists, as `(keys, name)`, the commands the mode offers, in `BINDINGS` order: `ESC`, help, the values, the moves, the mode's other commands, then save, open and quit. `TerminalUI` draws the panel when the puzzle announces a mode (`mode_changed()`) and again in `show_board()`.
- **Help screen:** `?` shows `Commands.long_help(offered)`: the commands the mode offers, the same ones as the panel, each with its keys and a longer description.
- **Status line:** blank unless there is something to report: `n`'s hint, a change in completion, a warning or a question.
- **Messages:** the game sends a `Message` with a kind; `TerminalUI` styles it: successes and hints in steel blue (the `SOLVED` style), information and warnings in yellow. `status()` shows it until the next command; `inform()` shows it with `Display.show_on_status_line(text, wait=True)`, which waits for a key press. `Display.warn()` is the yellow shortcut still used by code not yet moved behind the port (`Moves`, `Main`).
- `Display.confirm(msg)` asks a yes/no question the same way and returns `True` only for `y` or `Y`. Any other key, or an interrupted prompt, declines. `TerminalUI.confirm()` uses it, for `quit_()`, `rewind_()` and the save and restore questions.
- **Tests** of the game use `game/tests/recording_ui.py`, a `RecordingUI` that records every message and question and answers as the test tells it, instead of patching `Display`.

## 7. Conventions

The full list is in `CLAUDE.md`. The main points:

- **TDD:** write a failing test, make it pass, then refactor. Before starting a new feature, look for refactoring that would make the feature easier to add.
- **Private methods** use the `__` prefix. Tests that need one call the mangled name through a single helper in the test class, rather than making the method public. The one exception is a method that crosses into a subclass: a hook a subclass must override, such as a layout's `_blocks()`, or a helper a subclass calls, such as `Rule._move()`. It uses a single `_`, because Python would mangle a `__` name per class.
- **Method order:** a called method is placed as soon after its caller as possible, within its own section (interface or private).
- **Constants first:** class constants go at the top of the class, except constants built from a nested class and long data tables (such as `Display`'s drawing characters), which go at the end.
- **Layer boundaries** are as described in section 4.2.
- **Typed collaborators:** every parameter that receives a collaborator is annotated with its class, so the IDE can find the calls made on it (injected objects are otherwise untyped). Imports that would be circular are made under `if TYPE_CHECKING:` with the name quoted, e.g. `puzzle: "Puzzle"`. A collaborator typed as the `UserInterface` port leads to the port's methods, not to `TerminalUI`'s, by design.
- **Testing by hand:** the program is run and watched before every commit, because the tests can't show what the terminal looks like.

## 8. Next steps

1. **Separate the game from the display** (section 4.4), one step at a time, each with its own commits, all tests passing and a check by hand:
   - Done first: each `Moves` owns its `History`, instead of one global history.
   - Done, **step 1, messages and dialogs:** `PuzzleSolver` and `CompletionReport` return messages instead of warning; the puzzle and `GameFile` send every message, with its kind, and every dialog through the user interface (`user_interface.py`), and `TerminalUI` wraps today's `Display`. Left for step 2: `Moves`' warning about running out of gray shades, which belongs to the terminal.
   - Done, **step 2, attributes with meaning only:** `CellAttrs` (`cell_attrs.py`) defines what the attributes mean, and the game uses only it. `Moves` keeps a guess depth instead of a gray level. `DisplayAttrs` is now just the terminal's style table, turning depth into gray. `Moves` reports every change of depth through the new `guess_depth_changed()` port method, and `TerminalUI` warns when the depth crosses beyond its last shade.
   - Done, **step 3, cells stop drawing:** a cell reports each change through its block and the board to the user interface's `cell_changed()`, and `render()` shows the whole board with `show_board()`; `TerminalUI` decides what to redraw. `Cell.update()` is gone (`set()` reports changes), and so are the `render()` methods of cells, blocks and the board. `Border` is layout data in `border.py`.
   - Done, **step 4, actions apart from keys:** `actions.py` defines the game's `Action`s, its `Mode`s and the actions each offers; the puzzle announces its mode with `mode_changed()`. `commands.py` is now the terminal's key-binding table, and `TerminalUI` draws the panel and the help screen. Hidden commands are gone: every key maps to its action and the puzzle refuses what its mode doesn't offer, now including guesses in setup. `Puzzle.help_()` is gone (help is the terminal's), and values and guesses are separate actions (`value_()`, `guess_()`).
   - Done, **step 5, the loop moves to the interface:** `TerminalUI.play(puzzle)` runs the loop: it reads keys, shows help itself and hands each action to `puzzle.handle(action, digit)`. `TerminalUI(v_cells, h_cells)` sets the geometry and checks the screen size, so `Puzzle` no longer uses `Display` at all. `Main` just picks the layout and the user interface.
   - Done, **step 6, packages and the instance:**
     - Done, **6a, packages:** the game is in `game/` (with `game/rules/` and `game/puzzles/`), the terminal user interface in `ui/terminal/`, and `tests/package_boundary_test.py` checks that nothing in `game/` imports from `ui` or `blessed`.
     - Done, **6b, `Display` becomes an object:** created by `Main` and passed to `LayoutMenu`, `TerminalUI` and `Input`, instead of class-level state.

   The separation is complete: the game talks to the player only through the `UserInterface` port, and the terminal is one adapter for it.
2. **More rules for next and auto:** for example, a value that fits only one cell in a row, column or box.
3. **Redo**, if wanted.
