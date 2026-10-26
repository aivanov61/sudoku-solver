# Sudoku: Design Document

This document explains how the terminal Sudoku program is built: its layers, how a keystroke becomes a change on screen, and the conventions the code follows. It is written for developers working on the code. For how to play, see the User Guide.

## 1. Purpose and scope

The program lets a player type in a published 9x9 Sudoku puzzle and then solve it in the terminal. It helps by showing each cell's remaining possible values and by marking conflicting entries. Guesses are shaded so the player can see what depends on them and undo back to them.

The code is also meant as an example of clean, object-oriented Python built with test-driven development. The structure is designed to grow to other Sudoku layouts. Today only the standard layout of 3x3 boxes exists, in `Puzzle3x3`.

## 2. Current status

| Area | Status |
|---|---|
| Entering initial values, moving around, help, quit | Working |
| Guesses with gray shading | Working |
| Undo | Working |
| Possible values | Removed from the row, column and box when a value is entered, and given back when it is deleted, undone or changed, unless another related cell still holds it. An emptied cell works out its whole set again. |
| Conflict marking | The cell just entered is marked `CONFLICTING` (bold red on yellow). The cell it clashes with is not marked: `CONFLICTED` is defined but never applied. Other cells' marks don't update when related cells change. |
| Rewind (`r`), auto (`a`), next (`n`) | **Not implemented.** The keys are defined in `Commands`, but `Puzzle3x3` has no `rewind_`, `auto_` or `next_` method, so `Main` shows "This puzzle does not support…". |
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
Main (sudoku.py)  ── reads keys via Input, dispatches to the puzzle
  └── Puzzle3x3          knows the block layout and the selected cell
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

`doit.py` is a standalone `blessed` experiment and is not part of the program.

### 4.2 Responsibilities between layers

Each layer talks only to the layer next to it. Requests travel up and are routed back down:

- **A cell** never looks at other cells. It asks its parent block (`values()`, `remove_possible()`, `add_possible()`, `is_held_by_related_cell()`).
- **A block** answers each request by visiting the cell's *related cells* (every other cell in the same box, row or column, once each) through the private generator `__related_cells(row, col)`. It yields its own box cells first, then the row and column cells it gets from the puzzle, skipping any in its own box. `add_possible`, `remove_possible` and `is_held_by_related_cell` are each a short loop over it, and `is_held_by_related_cell` stops at the first match.
- **The puzzle** knows only its block layout. Its single method for blocks, `cells_in_row_or_col(row, col)`, yields from every block's `cells_in_row_or_col`. Each block decides which of its own cells are in the row or column. The puzzle passes those cells along but never reads or changes them, because in other Sudoku layouts the blocks may not form a regular grid, and only a block knows which of its cells lie in a given row or column.
- **The one exception** is the selected cell. The cursor moves by row and column, and a Sudoku's outer edge is always rectangular, so `Puzzle3x3` finds the selected cell itself (`__selected_cell` → `__cell` → `__block`). Revisit this if a puzzle with a non-rectangular outer edge is ever designed.

Each class groups its methods under comments naming who calls them, for example `# Interface required for cell instances` in `RectangularBlock` and `# Interface required for blocks` in `Puzzle3x3`.

### 4.3 Coordinates

Every cell stores its **puzzle-wide** `row` and `col` (0–8), set by `RectangularBlock.__phys_pos` when the block creates it. All requests between layers use these puzzle-wide positions. That's why a block can pick out "its cells in row 6 or column 8" without knowing where it sits relative to the cell that asked. `RectangularBlock.cell(row, col)` accepts puzzle-wide positions and reduces them with `%`.

## 5. Key flows

### 5.1 Startup and the main loop (`sudoku.py`)

1. Show the GPL splash; continue after 5 seconds or any key.
2. Create the puzzle. `Puzzle3x3.__init__` sets the display geometry, checks the screen size, clears `History` and builds 9 blocks of 9 cells.
3. `render()` draws the whole grid and the status line.
4. Loop while `puzzle.is_playing`: re-check the screen size (redraw if it was resized), move the cursor to the selected cell, read a command and handle it.

### 5.2 Command dispatch

- `Commands.CMDS` maps command names to their keys and help text. It is swapped between `COMMON_CMDS + INIT_COMMANDS` and `COMMON_CMDS + PLAY_COMMANDS` when the mode changes.
- `Input.get_cmd()` reads a key. Digits and shifted digits are returned as the character itself. Other keys become the command name plus `_` (for example `up_`), so they can't clash with Python reserved words. Unknown keys are ignored. CTRL-C or any input error returns `quit_`.
- `Main` sends values to `puzzle.value_(value, guess)`. For anything else, it calls the puzzle method of that name with `getattr`. A missing method gives "This puzzle does not support the "…" command". A method that raises an exception gives "This puzzle's "…" command is broken!". If the failing command was `quit_`, `Main` forces the program to quit.

### 5.3 Entering a value

```
Puzzle3x3.value_(val, guess)
  ├─ guess (in play mode)  → raise the gray level
  ├─ __attributes()        → INITIAL (init mode) or GUESS, plus the gray level if any
  ├─ refuse to change an INITIAL cell in play mode (warning)
  └─ __accept_user_value()
       ├─ play mode → History.add(Entry(cell, new value, previous value))
       └─ Cell.update(val, attrs)
            └─ Cell.set()  →  __smart_update(value)
                 ├─ parent.is_held_by_related_cell(row, col, value)? → add CONFLICTING
                 ├─ assign the new value (before notifying, so related cells see the board as it now is)
                 ├─ old value → parent.add_possible(...)     each related cell takes it back if it is empty
                 │                                          and none of its own related cells holds it
                 ├─ new value → parent.remove_possible(...)  each related cell removes it
                 ├─ new value → the cell clears its own possible values
                 └─ no value  → the cell adds back every value no related cell holds
```

- A cell redraws its possible values only when they actually change. That way, cells reached twice (by the box and by the row or column) don't flicker.
- `update()` then redraws the cell: only its value and possible values if its attributes are unchanged, or the whole cell if they changed.

**Conflicts** are worked out from the values on the board, never from a cell's possible values. The block checks its box, then the puzzle asks every block about the row and column. A cell's own position is always skipped, so its current value never counts against it. The same check decides whether a value can be given back: a cell regains a value only if `is_held_by_related_cell` says no related cell holds it, so a duplicate left on the board keeps the value blocked.

### 5.4 Modes

- **Initialization mode** (the start mode): values get `INITIAL` and are not recorded in `History`. `Delete` clears a cell. `ESC` calls `play_()`.
- **Play mode:** values are recorded in `History`. `ESC` calls `init_()`, which is refused while there is anything to undo ("Cannot initialize puzzle while playing - undo everything first."). `Delete` is mapped to `del_()` only to show a warning.

### 5.5 Undo and guess shading

- `History` is a class-level list of `Entry(cell, valueinfo, previous_valueinfo)`. `ValueInfo` stores the value and its primary attribute (`INITIAL`, `GUESS` or `None`).
- `undo_()` pops the last entry, moves the cursor to that cell and restores the previous value with `cell.update()`. With nothing to undo, it warns "Cannot undo initialized puzzle. ESC will re-enter initialization mode."
- **Guess shading:** each guess raises `_bg_level` by 10. Every value entered afterwards, guess or not, gets that gray background, which shows what depends on the guess. Undoing a guess lowers the level by 10. Above `MAX_GRAY_LEVEL` (100), the program warns and keeps reusing the last shade.

## 6. Display

- **Cell layout:** each cell is 6 columns by 3 lines. The top line is the border (shared with the cell above), the middle line shows the value, and the bottom line shows the possible values. Box edges use full blocks (`█`); inner lines use `│`, `─` and `┼`.
- **Possible values** are drawn in increasing order as subscript digits. When there are more than 5, `.....` is shown instead.
- **Attributes:** `DisplayAttrs` turns mnemonics into `blessed` style names such as `purple_on_lavender` or `bold_red_on_yellow`. There are two kinds:
  - *Primary* attributes (at most one per cell): `INITIAL` gives purple on lavender, and `GUESS` gives green on the current gray.
  - *Optional* attributes: `CONFLICTING` gives bold red on yellow. `CONFLICTED` (the primary color on yellow) is defined but not yet used.
  - Values with no primary attribute are drawn in `darkorange3`.
  - The gray level travels in the attribute tuple as `{"level": n}`.
- `Display` is a class with class-level state (`term`, `geom`) and functions called on the class, not on an instance.
- Warnings appear in yellow on the status line. Many of them wait for a key press.

## 7. Conventions

The full list is in `CLAUDE.md`. The main points:

- **TDD:** write a failing test, make it pass, then refactor. Before starting a new feature, look for refactoring that would make the feature easier to add.
- **Private methods** use the `__` prefix. Tests that need one call the mangled name through a single helper in the test class, rather than making the method public.
- **Method order:** a called method is placed as soon after its caller as possible, within its own section (interface or private).
- **Constants first:** class constants go at the top of the class, except constants built from a nested class and long data tables (such as `Display`'s drawing characters), which go at the end.
- **Layer boundaries** are as described in section 4.2.
- **Testing by hand:** the program is run and watched before every commit, because the tests can't show what the terminal looks like.

## 8. Next steps

1. **`CONFLICTED` marking:** mark the cell a new value clashes with, and clear both marks when the clash goes away. This can loop over the same related cells as the other requests.
2. **Rewind, auto and next:** add `rewind_`, `auto_` and `next_` to `Puzzle3x3`. Rewind needs the guess points already stored in `History`. Auto and next need solving logic in `CellSolver`, starting with cells that have a single possible value.
3. **Redo**, if wanted.
