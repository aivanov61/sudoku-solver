# Sudoku: User Guide

This program lets you type in a 9x9 Sudoku puzzle, such as one from a newspaper or puzzle book, and then solve it in your terminal. As you play, each cell shows the values still possible for it, mistakes are highlighted, and you can undo moves.

## Getting started

1. Install Python 3, then the `blessed` package: `pip install -r requirements.txt`
2. In a terminal, go to the program's folder and run: `python sudoku.py`
3. A copyright notice appears. It goes away after 5 seconds, or press any key.
4. If there's more than one puzzle layout, a menu lists them, with the chosen one highlighted. Use the up and down arrows to choose a layout and press `ENTER` to play it, or press `ESC` or `q` to quit (it asks you to confirm with `y`). If the list doesn't fit on the screen, `---more---` shows at the top or bottom, and the arrows scroll the rest into view. Scrolling can take the highlighted layout off the screen; `ENTER` then brings it back into view, and a second `ENTER` plays it. A layout that can't be played is grayed out, with a note after its name, **(broken: …)**, and the arrows skip it. If no layout can be played, `ENTER` ends the program.

   If there's only one layout, there's no menu. Any note about it appears in yellow under the copyright notice instead, and a broken layout ends the program.

The terminal window needs to be at least **80 columns wide and 29 lines tall**. If it's smaller, the program asks you to resize it. Press `Enter` when you're done, or `CTRL-C` to quit. A message too long for the status line is split onto the lines below it if the window has any, and cut short with `…` if it runs out of lines; the grid never moves.

For a narrow screen, such as a phone, run `python sudoku.py --no-panel`. The command panel beside the grid is left out, so 55 columns are enough; the window needs 31 lines, two more than usual, so long messages such as `n`'s explanations have room below the status line. While the status line is blank, it shows the mode in gray (`PLAY - ? for commands`), and `?` lists the commands as usual. On Android, the Termux app (from F-Droid) runs the program: install `python` and `git` with `pkg install`, then follow the steps above.

## The screen

- **The grid:** 81 cells in nine 3x3 boxes. Thick borders mark the boxes.
- **Each cell** shows its value in the middle line (or, if it's empty, any "must be" marks you've turned on, in small digits) and, along its bottom line, the values still possible for it, in small digits. They update as you enter, change, delete or undo values. When more than 5 values are possible, you'll see `.....` instead.
- **The cursor** sits on the selected cell. That's where your next entry goes.
- **The command panel** to the right of the grid shows the current mode (SETUP or PLAY) and lists its keys, one per line.
- **The status line** under the grid is blank most of the time. It shows explanations from `n`, when the puzzle is finished, warnings (in yellow) and questions.

## Two modes

You start in **setup mode**, where you type in the puzzle's given numbers. Then you switch to **play mode** to solve it.

### Setup mode: entering the puzzle

| Key | Action |
|---|---|
| Arrow keys, or `h` `j` `k` `l` | Move left, down, up, right |
| `1`–`9` | Enter a given number. Givens are shown in purple on lavender. |
| `Delete` | Clear the selected cell |
| `m` | Tag (mark) the selected cell, or untag it (see below) |
| `u` `r` `a` `n`, shifted `1`–`9` | Not available in setup (no guesses either); they remind you to press `ESC` to start playing |
| `ESC` | Finish setup and start playing. Not allowed while given numbers clash, or while an empty cell has no possible values left (the cursor moves to that cell). |
| `?` | Show the setup commands, with a longer description of each |
| `s` | Save the puzzle to a file (see below) |
| `o` | Restore a saved puzzle (see below) |
| `q` | Quit (asks you to confirm) |
| `CTRL-C` | Quit at once, without asking |

### Play mode: solving

| Key | Action |
|---|---|
| Arrow keys, or `h` `j` `k` `l` | Move left, down, up, right |
| `1`–`9` | Enter a value |
| Shifted `1`–`9` (`!` `@` `#` `$` `%` `^` `&` `*` `(` on a US keyboard) | Enter a **guess** (see below) |
| `u` | Undo your last entry |
| `r` | Rewind: undo everything entered after your most recent guess, keeping the guess (or undo everything, if there's no guess). Asks you to confirm, since it can't be undone. |
| `n` | Next: show an obvious next move and why; press `n` again to fill it in (see below) |
| `a` | Auto: fill in every obvious move, one after another (see below) |
| `m` | Tag (mark) the selected cell, or untag it (see below); works in setup too |
| `c` | Configure: change settings such as the "must be" marks (see below); works in setup too |
| `ESC` | Go back to setup mode (only once everything has been undone) |
| `?` | Show the playing commands, with a longer description of each |
| `s` | Save the puzzle to a file (see below) |
| `o` | Restore a saved puzzle (see below) |
| `q` | Quit (asks you to confirm) |
| `CTRL-C` | Quit at once, without asking |

When the program asks you to confirm, press `y` to go ahead. Any other key cancels.

You can't change the puzzle's given numbers during play. To fix a typo in the setup, undo all your moves, press `ESC` to go back to setup mode, correct it and press `ESC` again.

## Dead ends

A dead end is either an empty cell with no possible values left, or a value that is missing from a box, row or column but has no place left there. Whenever you enter a value, in either mode, or restore a saved puzzle, and the board has a dead end, the cursor moves to the first one and the bottom line warns you until your next key, without stopping you. For a missing value, the cursor moves to an empty cell of that box, row or column, and the value is shown there in white on red until your next key; during setup the warning also says which value has no place left, and where. During play it suggests undoing (`u`) or rewinding to a previous guess (`r`); during setup it asks you to change the setup. The warning comes after every value you enter until the dead end is gone.

## Guesses

When you're stuck and need to try a value, enter it as a guess with a shifted digit. Guesses are shown in green on a gray background.

Every value you enter after a guess gets the same gray background, so you can see everything that depends on it. Each new guess makes the gray a shade lighter. If a guess turns out wrong, press `r` to rewind: everything entered after the guess is undone, and the cursor lands on the guessed cell so you can type a different guess over it. Pressing `r` again also undoes that guess and rewinds to the guess before it. After ten nested guesses there are no lighter shades left: the program warns you when you go past the last shade and then reuses it for any deeper guesses. If you undo back within the shades and later go past the last one again, it warns you again.

Guesses also make good checkpoints, even for values you're sure of: see "Next: an obvious move" below.

## Conflicts

If you enter a value that's already in the same row, column or box, the cell turns **bold red on bright yellow**, and each cell it clashes with gets a **yellow background**. Replace, delete or undo the clashing value, and the cells go back to normal. A cell that clashes with more than one other cell stays marked until all of its clashes are gone.

## Next: an obvious move

Press `n` to be shown the next obvious move. It looks, left to right and top to bottom, for an empty cell whose value can be worked out from the board, moves the cursor there and explains on the bottom line, in steel blue, why that value must go there. Press `n` again to fill it in (also in steel blue), or press any other key to carry on yourself. Press `u` to take a filled-in move back.

It finds these kinds of move, and ends each explanation with the name of the rule in brackets:
- **A single value** `[single value]`: only one value fits the cell, because every other value is already in its row, column or box.
- **A hidden single** `[hidden single]`: a value can go nowhere else in the cell's box, row or column, even though other values would still fit the cell.
- **A pointing pair** `[pointing pair]`: when, within one box, a value can only go in one row (or column), the value in that row must be in this box, so it can't go anywhere else in the row. When that leaves a cell a single value, or a value only one place, `n` explains both steps, e.g. "Only 9 fits here: in one box, 4 can only go in one row, which rules 4 out here."
- **A box/line reduction** `[box/line reduction]`: the other way round. When, within one row (or column), a value can only go in one box, it can't go anywhere else in that box.

`n` tries them in this order, so if a cell qualifies more than one way, it explains the simplest. Values ruled out by pointing pairs and box/line reductions aren't taken off the cells' bottom lines; `n` only shows them when they lead to a value to fill in, and tagged cells leave them out of what they must be (see Tags).

You don't have to press `n` the second time: with the cursor already on the cell, you can type the value yourself. You can even enter it as a guess, with a shifted digit, although it isn't really a guess. That turns it into a checkpoint. `r` rewinds to the most recent guess, and everything entered after it is shaded, so making guesses at the points you consider key decisions lets you solve the puzzle in stages and step back to any of them.

It won't move if:
- **There are conflicts on the board:** it asks you to resolve them first.
- **There's a dead end** (see "Dead ends" above): it moves the cursor there and suggests undoing (`u`) or rewinding to a previous guess (`r`), because an earlier entry or guess must be wrong.
- **There's no obvious move:** it tells you that you'll have to make a guess.

## Auto: all the obvious moves

Press `a` to fill in, without explanations, every move that `n` would find, one after another, until there are none left. The values are shown in steel blue, the cursor ends on the last one filled in, and the bottom line tells you why it stopped, for the same reasons as `n`. Each value is a separate entry, so `u` takes them back one at a time. To take them all back at once, enter a guess before pressing `a` and use `r`.

## "Must be" marks

A "must be" mark is a small digit in the middle of an empty cell: that value has only a few places left in the cell's box, and this cell is one of them. Solvers call this Snyder notation. A mark in two cells of a box means the value must be in one of those two. A value with a single mark in its box is a hidden single: it can go only there.

Snyder marks are off at first; a cell you tag with `m` shows what it must be instead (see Tags below). Press `c` to open the configure menu, which lists the settings under the heading **Must-be marks (Snyder notation)**:
- **Kind of house:** `box` (the default) marks values with few places left in their box; `box, row or column` marks a value with few enough places in any of the three.
- **Threshold:** how few places a value must have left to be marked, from `2 or fewer places` (the default) to `5 or fewer places`.
- **Whole puzzle:** `off` (the default) shows no Snyder marks; `on` shows them in every empty cell that isn't tagged. Kind of house and threshold apply only here.

Each line shows its choice and where it is among them, e.g. `Threshold .......... 2 or fewer places (1 of 4)`. Use the up and down arrows to choose a line, and `TAB` or the right arrow to move to the next choice (`Shift-TAB` or the left arrow for the previous one); the choices go round at either end. A gray line under a setting explains the choice made, such as which cells show marks. Press `ENTER` to go back to the puzzle with the new settings, or `ESC` (or `q`) to go back with the settings as they were.

The marks update after every key, as values are entered, deleted, undone or filled in. Up to three marks are spaced out; four or five are shown closed up; more than that show `.....`. With a high threshold and rows and columns included, that happens often: in a row, column or box with 5 or fewer empty cells, every possible value has 5 or fewer places, so every one is marked. During setup the marks are hidden, and they come back when you start playing.

Box marks are the safest to read: two marks in a box always mean "one of these two". With rows and columns included, two marks that happen to line up in a row may come from two different houses (say one from its row, the other from its box), so they don't necessarily mean the value must be in one of them.

## Tags

Press `m` to tag the selected cell, to pick it out while you think, and `m` again to untag it. A tagged empty cell shows its small digits in steel blue: its possible values on the bottom line and, while playing, what it must be on the middle line, whatever the "must be" settings:
- If the cell is forced, just that value: its only possible value, or a value that has no other place in its row, column or box.
- Otherwise, its possible values, less any value that a cell in its row, column or box is forced to hold, and less any value a pointing pair or box/line reduction rules out of it (see Next).

So in a row that needs 4, 8 and 9, where the 4 can only go in one of the three cells, that cell shows **4** and the other two show **8 9**. This looks only at what is forced or ruled out right now, one step, so it never gives away more than the next move would; it gets sharper as the program learns more solving rules. Once the cell has a value the steel blue is gone, since the value takes the place of the small digits, but the tag stays: when the value is deleted or undone, the steel blue comes back. Tags work in both modes, undo and rewind leave them alone, and they are saved with the puzzle.

## Finishing the puzzle

When the last empty cell is filled in, the status line says, until your next key, that the puzzle is **solved** (in steel blue) or **complete, with errors** (in yellow) if any values clash. You can still type over values, or undo, to fix errors. The status line reports again whenever that changes: once the errors are fixed, or when the puzzle is complete again after undo or rewind emptied a cell. `n` and `a` have nothing left to do, so they just remind you that the puzzle is solved, or that it's complete with errors and you should undo or change values to fix them.

## Saving and restoring

Press `s` at any time, in either mode, to save the puzzle to a file. The status line asks for the file name and offers the last one you used (`sudoku` the first time). Save files always end in `.json`, which is shown after the name but never typed: the cursor starts just before it, and the left and right arrows move within the name but not into the `.json`. Type to insert at the cursor, `Backspace` to remove the character before it and `Delete` the one at it; press `ENTER` to accept the name, or `ESC` to cancel. A name without a folder is kept in the `saved_games` folder, which is created the first time you save; to put a file anywhere else, include its folder in the name, for example `.\sudoku` for the current folder. If the file already exists, it asks before replacing it. If the board is still empty, there's nothing to save, and it just tells you so.

Press `o` to restore a saved puzzle the same way. It brings back everything: the givens, every value you entered, guesses and their shading, the mode, where the cursor was, which cells you tagged, and how the "must be" marks were configured (files saved before marks existed come back with the defaults: marks in tagged cells only). Undo and rewind keep working through the restored moves. The restored puzzle replaces the current one completely, so if the board holds any values, it asks you to confirm first.

A puzzle can only be restored into the layout it was saved from. A file saved by a newer version of the program can't be restored; the program says so, and you can update the program to restore it. A file that only adds something newer, such as a new setting, is restored without it, and the bottom line names what was ignored (or just counts it, when the names don't fit). Saving the puzzle again leaves the ignored entries out.

## Colors at a glance

| Looks like | Meaning |
|---|---|
| Purple on lavender | A given number from setup |
| Orange | A value you entered |
| Green on gray | A guess; gray backgrounds also mark values entered after a guess |
| Steel blue | A value filled in by `n` or `a`; "solved" on the status line |
| Steel blue small digits | A cell you tagged with `m` |
| Bold red on bright yellow | The value you just entered is already in the same row, column or box |
| Usual color on yellow | Holds a value that a newer entry clashes with |
| Yellow text on the status line | A warning. If it waits, press any key to continue. |

## Current limitations

- **Next (`n`) and auto (`a`)** know only a few solving techniques so far, so on harder puzzles they will often tell you to make a guess.
- There's no redo.

## Troubleshooting

- **The grid looks broken or there are odd characters:** make sure your terminal uses UTF-8 and a font with box-drawing characters.
- **The program asks you to resize:** make the window at least 80 × 29 and press `Enter`.
- **Something looks wrong on screen:** press `?` and then any key. Returning from help redraws the whole screen.
