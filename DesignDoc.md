# Sudoku: Design Document

This document explains how the terminal Sudoku program is built: its layers, how a keystroke becomes a change on screen, and the conventions the code follows. It is written for developers working on the code. For how to play, see the User Guide.

## 1. Purpose and scope

The program lets a player type in a published 9x9 Sudoku puzzle and then solve it in the terminal. It helps by showing each cell's remaining possible values and by marking conflicting entries. Guesses are shaded so the player can see what depends on them and undo back to them.

The code is also meant as an example of clean, object-oriented Python built with test-driven development. The structure is designed to grow to other Sudoku layouts: each layout is a small subclass of `Puzzle` in the `puzzles/` folder, found automatically by `PuzzleCatalog`. Today only the standard layout of 3x3 boxes exists, in `puzzles/puzzle_3x3.py`.

## 2. Current status

| Area | Status |
|---|---|
| Entering initial values, moving around, help, quit | Working |
| Guesses with gray shading | Working |
| Undo | Working |
| Possible values | Removed from the row, column and box when a value is entered, and given back when it is deleted, undone or changed, unless another related cell still holds it. An emptied cell works out its whole set again. |
| Conflict marking | The cell just entered is marked `CONFLICTING` (bold red on bright yellow), and every related cell already holding the value is marked `CONFLICTED` (its usual color on yellow). Marks clear when the value is deleted, changed or undone, once no related cell still holds it. |
| Rewind (`r`) | Working |
| Next (`n`) | Working for the first rule: a cell with a single possible value (see 5.6) |
| Auto (`a`) | **Not implemented.** The key is defined in `Commands`, but `Puzzle` has no `auto_` method, so `Main` shows "This puzzle does not support…". |
| Redo | Not implemented. |

## 3. Running and testing

- **Requirements:** Python 3 (currently developed on 3.15) and `blessed` 1.20 or later (`pip install -r requirements.txt`).
- **Run:** `python sudoku.py` from the project folder.
- **Terminal size:** at least 54 columns × 29 lines (9 cells × 6 columns; 9 cells × 3 lines, plus 2 for the status line).
- **Tests:** `py -m pytest` from the project folder, or run one file directly, for example `py tests/cell_test.py`. The tests use `unittest` and pytest runs them unchanged. Note:
  - `tests/display_test.py::TestDisplay` draws on the real terminal and pauses for a second after each test. `tests/input_test.py` waits up to two seconds for a key press. Both are meant for watching by hand. Select the other files or classes to skip them.
  - `tests/unit_test_utils.py` holds an older helper that no test uses.

## 4. Architecture

### 4.1 Layers

```
Main (sudoku.py)  ── gets the layout from PuzzleCatalog, reads keys via Input, dispatches to the puzzle
  └── Puzzle3x3 (a Puzzle)    Puzzle: everything generic; Puzzle3x3: only the 3x3 block layout
        └── RectangularBlock ×9   knows its cells and which lie in a given row or column
              └── Cell ×9          holds a value, display attributes and a CellSolver
                    └── CellSolver  holds the set of possible values
```

Supporting modules:

| Module | Class | Role |
|---|---|---|
| `commands.py` | `Commands` | Key bindings and help text for each mode |
| `input.py` | `Input` | Reads a keystroke and turns it into a command name |
| `display.py` | `Display`, `Border` | All terminal drawing, through `blessed` |
| `display_attrs.py` | `DisplayAttrs` | Turns attribute mnemonics into `blessed` style names |
| `history.py` | `History`, `Entry` | The undo stack |
| `copyright.py` | `Copyright` | The GPL splash text |
| `puzzle.py` | `Puzzle` | The generic puzzle; an abstract base class for layouts |
| `puzzles/` | one module per layout | e.g. `puzzle_3x3.py` with `Puzzle3x3` |
| `puzzle_catalog.py` | `PuzzleCatalog`, `PuzzleLayout` | Finds the layouts and reports any that are broken or not fully functional |
| `layout_menu.py` | `LayoutMenu` | Lets the player choose a layout when there are several |
| `puzzle_solver.py` | `PuzzleSolver` | Applies the solving rules in order to find the next move |
| `rules/` | one module per rule, plus `rule.py` and `order.py` | `Rule`, `Outcome` and the rules; `order.py` sets the order |

`doit.py` is a standalone `blessed` experiment and is not part of the program.

### 4.2 Responsibilities between layers

Blocks decide which cells are related; cells act on them:

- **A block** gives a cell its *related cells* (every other cell in the same box, row or column, once each) through the generator `related_cells(row, col)`. It yields its own box cells first, then the row and column cells it gets from the puzzle, skipping any in its own box. Besides that, it gives cells the legal `values()`.
- **A cell** acts on its related cells directly: it gives them back an old value (`add_possible`), removes a new one (`remove_possible`), and marks or clears conflicts (`mark_conflicted`, `clear_resolved_conflict`). It checks whether a related cell holds a value with `any()`, which stops at the first match. New cross-cell behavior is added to `Cell` alone, so blocks and the puzzle stay unchanged.
- **The puzzle** knows only its block layout. Its single method for blocks, `cells_in_row_or_col(row, col)`, yields from every block's `cells_in_row_or_col`. Each block decides which of its own cells are in the row or column. The puzzle passes those cells along but never reads or changes them, because in other Sudoku layouts the blocks may not form a regular grid, and only a block knows which of its cells lie in a given row or column.
- **The one exception** is the selected cell. The cursor moves by row and column, and a Sudoku's outer edge is always rectangular, so `Puzzle` finds the selected cell itself (`__selected_cell` → `__cell` → the layout's `_block_at`). Revisit this if a puzzle with a non-rectangular outer edge is ever designed.

Each class groups its methods under comments naming who calls them, for example `# Interface required for cells` in `RectangularBlock` and `# Interface required for related cells` in `Cell`, with private methods last under `# Private functions`.

### 4.3 Coordinates

Every cell stores its **puzzle-wide** `row` and `col` (0–8), set by `RectangularBlock.__phys_pos` when the block creates it. All requests between layers use these puzzle-wide positions. That's why a block can pick out "its cells in row 6 or column 8" without knowing where it sits relative to the cell that asked. `RectangularBlock.cell(row, col)` accepts puzzle-wide positions and reduces them with `%`.

## 5. Key flows

### 5.1 Startup and the main loop (`sudoku.py`)

1. Ask `PuzzleCatalog` for the available layouts.
2. Show the GPL splash; continue after 5 seconds or any key. With a single layout that is broken or not fully functional, or with no layouts at all, a yellow note under the splash says so.
3. Pick the layout: with several, `LayoutMenu` lets the player choose (see 5.7); with one, it is used directly. If the player quits the menu, or the only layout is broken or missing, exit here.
4. Create the puzzle. `Puzzle.__init__` sets the display geometry, checks the screen size and clears `History`; the layout's `__init__` then builds its blocks (9 blocks of 9 cells for `Puzzle3x3`).
5. `render()` draws the whole grid and the status line.
6. Loop while `puzzle.is_playing`: re-check the screen size (redraw if it was resized), move the cursor to the selected cell, read a command and handle it.

### 5.2 Command dispatch

- `Commands.CMDS` maps command names to their keys and help text. It is swapped between `COMMON_CMDS + INIT_COMMANDS` and `COMMON_CMDS + PLAY_COMMANDS` when the mode changes.
- `Input.get_cmd()` reads a key. Digits and shifted digits are returned as the character itself. Other keys become the command name plus `_` (for example `up_`), so they can't clash with Python reserved words. Unknown keys are ignored. `q` gives `quit_`, which asks for confirmation. CTRL-C or any input error gives `force_quit_`, which stops at once without asking.
- Before carrying out any command, `Main` calls `puzzle.command_received(cmd)`, so the puzzle can react to commands in general (today: any command but `n` cancels a pending `n` move).
- `Main` sends values to `puzzle.value_(value, guess)`. For anything else, it calls the puzzle method of that name with `getattr`. A missing method gives "This puzzle does not support the "…" command". A method that raises an exception gives "This puzzle's "…" command is broken!". If the failing command was `quit_` or `force_quit_`, `Main` forces the program to quit.

### 5.3 Entering a value

```
Puzzle.value_(val, guess)
  ├─ guess (in play mode)  → raise the gray level
  ├─ __attributes()        → INITIAL (init mode) or GUESS, plus the gray level if any
  ├─ refuse to change an INITIAL cell in play mode (warning)
  └─ __accept_user_value()
       ├─ play mode → History.add(Entry(cell, new value, previous value))
       └─ Cell.update(val, attrs)
            └─ Cell.set()
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
```

- A cell redraws its possible values only when they actually change.
- `update()` then redraws the cell: only its value and possible values if its attributes are unchanged, or the whole cell if they changed.

**Conflicts** are worked out from the values on the board, never from a cell's possible values. A cell checks its related cells (its box first, then the row and column). Its own position is never among them, so its current value never counts against it. The same check decides whether a value can be given back: a cell regains a value only if no related cell holds it, so a duplicate left on the board keeps the value blocked.

### 5.4 Modes

- **Initialization mode** (the start mode): values get `INITIAL` and are not recorded in `History`. `Delete` clears a cell. `ESC` calls `play_()`.
- **Play mode:** values are recorded in `History`. `ESC` calls `init_()`, which is refused while there is anything to undo ("Cannot initialize puzzle while playing - undo everything first."). `Delete` is mapped to `del_()` only to show a warning.

### 5.5 Undo and guess shading

- `History` is a class-level list of `Entry(cell, valueinfo, previous_valueinfo)`. `ValueInfo` stores the value and its primary attribute (`INITIAL`, `GUESS` or `None`).
- `undo_()` pops the last entry, moves the cursor to that cell and restores the previous value with `cell.update()`. With nothing to undo, it warns "Cannot undo initialized puzzle. ESC will re-enter initialization mode."
- `rewind_()` undoes at least one entry, then keeps undoing until the most recent remaining entry is a guess (primary attribute `GUESS`), or until the history is empty. The guess stays on the board and the cursor moves to it, ready for a different value to be typed over it. Pressing `r` again undoes that guess and rewinds to the one before. It uses `History.last()` to look at the most recent entry without removing it. With nothing to undo, it gives the same warning as `undo_()`. Otherwise it asks for confirmation first, since a rewind can't be undone.
- **Guess shading:** each guess raises `_bg_level` by 10. Every value entered afterwards, guess or not, gets that gray background, which shows what depends on the guess. Undoing a guess lowers the level by 10. Above `MAX_GRAY_LEVEL` (100), the program warns and keeps reusing the last shade.

### 5.6 Next: the obvious next move

`n` teaches as it goes, in two steps. The first press asks the puzzle's `PuzzleSolver` for the next move, moves the cursor to its cell and shows *why* in place of the command summary on the status line, in steel blue like the solved values. The second press fills it in. The next press starts over with the following move.

The solver consults the rules listed in `rules/order.py`, in that order, and takes the move of the first one that has one:

1. **`ConflictsRule`:** if any cell carries a conflict mark, the move is the warning "Resolve the conflicts first."
2. **`DeadEndRule`:** if an empty cell has no possible values, the cursor moves there and the warning is "Dead end - try undoing until this square shows at least one possible value." It suggests undoing rather than rewinding, because a rewind could go back further than needed.
3. **`SingleValueRule`:** a cell whose only possible value is left; the hint is "Only 9 fits here: every other value is already in its row, column or box."

The first two *stop* solving: every `n` repeats their warning, and there is nothing to fill in. If no rule has a move, `next_()` warns "No obvious next move. You'll have to make a guess."

- **Rules** live in `rules/`, one file each. Each is a `Rule` subclass with `find(puzzle)`, which returns a `Move` or `None` without changing anything. A `Move` holds its `outcome` (`MOVED` for a value to fill in, `STOPPED` for a warning), its `hint` (the explanation or the warning), its `cell` and its `value`. Rules that stop solving come before rules that make moves. A test checks that every rule in `rules/` is listed in `rules/order.py`.
- **The solver** has `find_move()` (the first rule's move) and `make_move(move)` (fill in its value through the puzzle). The puzzle keeps a found move as its *pending move* between the two presses of `n`.
- **Cancelling:** `Main` calls `puzzle.command_received(cmd)` before carrying out every command. Any command other than `n` drops the pending move, so the following `n` points out a move again instead of filling one in. Keys the program does not recognize are ignored as before and cancel nothing.
- **The puzzle's interface for the solver:** `first_cell_where(condition)` returns the first cell, left to right and top to bottom, for which the condition holds (it asks every block's `cells_where()`, so only blocks look inside cells, as section 4.2 requires); `select(cell)` moves the cursor; `enter_solved_value(cell, value)` enters a value.
- **Making the move:** a `SOLVED` value goes through the same path as a typed value, so it is recorded in `History` with `SOLVED` as its primary attribute. `u` and `r` treat it like any other non-guess entry, and undoing a change restores the steel blue. It also picks up the current guess shading.
- **Adding a rule** means a new file in `rules/` and one line in `rules/order.py`; nothing else changes. Auto (`a`) will find and make moves one after another, without hints. Rules that need whole rows, columns or boxes (rather than single cells) will need a new solver interface, to be designed with the first such rule.
- **Rules and several layouts (planned, not built yet):** today every layout uses the shared list in `rules/order.py`. The intended direction:
  - **Shared rules stay shared** by working through units the layout supplies (the groups of cells that must each hold every value once: rows, columns and boxes, or a jigsaw's regions, an X-Sudoku's diagonals, and so on), the way `related_cells` already comes from the blocks.
  - **Layout-specific rules** (such as Killer Sudoku cage sums) live with their layout, for example in a `puzzles/<layout>/` package, rather than in the shared `rules/` folder.
  - **A layout chooses its rules** through a `RULES` class attribute that defaults to the shared order; a variant lists shared and its own rules together, in order, and `Puzzle` passes `self.RULES` to its `PuzzleSolver`.
  - Build this when the first layout that needs its own rules arrives.

### 5.7 Layouts and the catalog

- **`Puzzle`** (`puzzle.py`) is an abstract base class (`abc.ABC`) holding everything that does not depend on the block layout. A layout subclass sets `NAME`, calls `super().__init__(v_cells, h_cells)`, builds its blocks, and implements the two `@abstractmethod` hooks `_blocks()` and `_block_at(row, col)`. Python refuses to create a layout that is missing a hook.
- **`PuzzleCatalog.available()`** imports every module in `puzzles/` and returns a `PuzzleLayout` for each `Puzzle` subclass that has its own `NAME` (classes without one, such as shared base classes, are skipped), sorted by name. A new layout is just a new file there.
- **Notes for the player:** a layout is *broken* if its file cannot be loaded or a hook is missing (the class is still abstract), and *not fully functional* if a command in `Commands` has no matching puzzle method (`#` maps to `value_`, every other command to its name plus `_`). `PuzzleLayout.label()` shows these after the name, e.g. "Standard 9x9 (not fully functional, missing: auto)". Detecting them never creates the puzzle, so it has no side effects.
- **With one layout**, its note, if any, is shown under the splash screen; a broken layout then exits instead of starting.
- **With several layouts**, `LayoutMenu` (`layout_menu.py`) lists them all with their notes after the splash. The player types a number and presses ENTER (Backspace corrects it); numbers stay the same on every page. At most 9 digits are kept, so the number always fits in a 32-bit integer; a further digit shows `...` after them and makes the entry too big (ENTER then says "Number too big"), and Backspace removes the `...` before any digit. As many layouts are shown as fit the terminal's height; when they don't all fit, (p)revious and (n)ext turn the page (doing nothing at either end). (q)uit is always offered and asks "Really quit? (y/n)" on the message line (only y confirms); p, n and q act on a single key, even with a number half typed. CTRL-C quits at once. Choosing a broken layout, or a number that isn't listed, shows a yellow message and keeps the menu open.

## 6. Display

- **Cell layout:** each cell is 6 columns by 3 lines. The top line is the border (shared with the cell above), the middle line shows the value, and the bottom line shows the possible values. Box edges use full blocks (`█`); inner lines use `│`, `─` and `┼`.
- **Possible values** are drawn in increasing order as subscript digits. When there are more than 5, `.....` is shown instead.
- **Attributes:** `DisplayAttrs` turns mnemonics into `blessed` style names such as `purple_on_lavender` or `bold_red_on_bright_yellow`. There are two kinds:
  - *Primary* attributes (at most one per cell): `INITIAL` gives purple on lavender, `GUESS` gives green on the current gray, and `SOLVED` (values filled in by `n`) gives steel blue on the current gray.
  - *Optional* attributes: `CONFLICTING` gives bold red on bright yellow. `CONFLICTED` gives the primary color on yellow, so the newest entry stands out from the cells it clashes with. A cell carries at most one of the two; `CONFLICTING` wins.
  - Values with no primary attribute are drawn in `darkorange3`.
  - The gray level travels in the attribute tuple as `{"level": n}`.
- `Display` is a class with class-level state (`term`, `geom`) and functions called on the class, not on an instance.
- Warnings appear in yellow on the status line. Many of them wait for a key press.
- `Display.confirm(msg)` asks a yes/no question the same way and returns `True` only for `y` or `Y`. Any other key, or an interrupted prompt, declines. `quit_()` and `rewind_()` use it.

## 7. Conventions

The full list is in `CLAUDE.md`. The main points:

- **TDD:** write a failing test, make it pass, then refactor. Before starting a new feature, look for refactoring that would make the feature easier to add.
- **Private methods** use the `__` prefix. Tests that need one call the mangled name through a single helper in the test class, rather than making the method public. The one exception is a hook a subclass must override, such as a layout's `_blocks()`: it uses a single `_`, because Python would mangle a `__` name per class.
- **Method order:** a called method is placed as soon after its caller as possible, within its own section (interface or private).
- **Constants first:** class constants go at the top of the class, except constants built from a nested class and long data tables (such as `Display`'s drawing characters), which go at the end.
- **Layer boundaries** are as described in section 4.2.
- **Testing by hand:** the program is run and watched before every commit, because the tests can't show what the terminal looks like.

## 8. Next steps

1. **Auto:** add `auto_` to `Puzzle`, finding and making moves with `PuzzleSolver` while they are `MOVED`, without hints.
2. **More rules for next:** for example, a value that fits only one cell in a row, column or box.
3. **Redo**, if wanted.
