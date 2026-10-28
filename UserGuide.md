# Sudoku: User Guide

This program lets you type in a 9x9 Sudoku puzzle, such as one from a newspaper or puzzle book, and then solve it in your terminal. As you play, each cell shows the values still possible for it, mistakes are highlighted, and you can undo moves.

## Getting started

1. Install Python 3, then the `blessed` package: `pip install -r requirements.txt`
2. In a terminal, go to the program's folder and run: `python sudoku.py`
3. A copyright notice appears. It goes away after 5 seconds, or press any key.
4. If there's more than one puzzle layout, a menu lists them. Type a layout's number and press `ENTER` to play it (`Backspace` fixes a typo), or press `q` to quit (it asks you to confirm with `y`). If the list doesn't fit on the screen, `p` and `n` show the previous and next page. A layout that can't be played has a note after its name, **(broken: …)**; choosing it shows why, and you can pick another.

   If there's only one layout, there's no menu. Any note about it appears in yellow under the copyright notice instead, and a broken layout ends the program.

The terminal window needs to be at least **80 columns wide and 29 lines tall**. If it's smaller, the program asks you to resize it. Press `Enter` when you're done, or `CTRL-C` to quit. At exactly 80 columns, a few long messages on the status line may spill onto the line below it; the grid isn't affected, and a wider window avoids it.

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
| `m` | Marks: change which "must be" marks are shown (see below) |
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

It finds two kinds of move, and ends each explanation with the name of the rule in brackets:
- **A single value** `[single value]`: only one value fits the cell, because every other value is already in its row, column or box.
- **A hidden single** `[hidden single]`: a value can go nowhere else in the cell's box, row or column, even though other values would still fit the cell.

If a cell qualifies both ways, it explains the single value.

You don't have to press `n` the second time: with the cursor already on the cell, you can type the value yourself. You can even enter it as a guess, with a shifted digit, although it isn't really a guess. That turns it into a checkpoint. `r` rewinds to the most recent guess, and everything entered after it is shaded, so making guesses at the points you consider key decisions lets you solve the puzzle in stages and step back to any of them.

It won't move if:
- **There are conflicts on the board:** it asks you to resolve them first.
- **There's a dead end** (see "Dead ends" above): it moves the cursor there and suggests undoing (`u`) or rewinding to a previous guess (`r`), because an earlier entry or guess must be wrong.
- **There's no obvious move:** it tells you that you'll have to make a guess.

## Auto: all the obvious moves

Press `a` to fill in, without explanations, every move that `n` would find, one after another, until there are none left. The values are shown in steel blue, the cursor ends on the last one filled in, and the bottom line tells you why it stopped, for the same reasons as `n`. Each value is a separate entry, so `u` takes them back one at a time. To take them all back at once, enter a guess before pressing `a` and use `r`.

## "Must be" marks

A "must be" mark is a small digit in the middle of an empty cell: that value has only a few places left in the cell's box, and this cell is one of them. Solvers call this Snyder notation. A mark in two cells of a box means the value must be in one of those two. A value with a single mark in its box is a hidden single: it can go only there.

Marks are off at first. Each press of `m` (while playing) moves to the next setting and names it on the bottom line:
- **Configs 1 to 4** mark values with 2, 3, 4 or 5 places or fewer in their box, e.g. "Must-be marks (config 1 of 8): 2 or fewer 'must be' values in their box."
- **Configs 5 to 8** do the same for the box, row or column: a value is marked if it has few enough places in any of the three.
- **The next press** turns them off again.

The marks update after every key, as values are entered, deleted, undone or filled in. Up to three marks are spaced out; four or five are shown closed up; more than that show `.....`. During setup the marks are hidden, and they come back when you start playing.

Box marks are the safest to read: two marks in a box always mean "one of these two". With rows and columns included, two marks that happen to line up in a row may come from two different houses (say one from its row, the other from its box), so they don't necessarily mean the value must be in one of them.

## Finishing the puzzle

When the last empty cell is filled in, the status line says, until your next key, that the puzzle is **solved** (in steel blue) or **complete, with errors** (in yellow) if any values clash. You can still type over values, or undo, to fix errors. The status line reports again whenever that changes: once the errors are fixed, or when the puzzle is complete again after undo or rewind emptied a cell. `n` and `a` have nothing left to do, so they just remind you that the puzzle is solved, or that it's complete with errors and you should undo or change values to fix them.

## Saving and restoring

Press `s` at any time, in either mode, to save the puzzle to a file. The status line asks for the file name and offers the last one you used (`sudoku` the first time). Save files always end in `.json`, which is shown after the name but never typed: the cursor starts just before it, and the left and right arrows move within the name but not into the `.json`. Type to insert at the cursor, `Backspace` to remove the character before it and `Delete` the one at it; press `ENTER` to accept the name, or `ESC` to cancel. A name without a folder is kept in the `saved_games` folder, which is created the first time you save; to put a file anywhere else, include its folder in the name, for example `.\sudoku` for the current folder. If the file already exists, it asks before replacing it. If the board is still empty, there's nothing to save, and it just tells you so.

Press `o` to restore a saved puzzle the same way. It brings back everything: the givens, every value you entered, guesses and their shading, the mode, where the cursor was, and which "must be" marks were shown (files saved before marks existed come back with marks off). Undo and rewind keep working through the restored moves. The restored puzzle replaces the current one completely, so if the board holds any values, it asks you to confirm first.

A puzzle can only be restored into the layout it was saved from. A file saved by a newer version of the program can't be restored; the program says so, and you can update the program to restore it.

## Colors at a glance

| Looks like | Meaning |
|---|---|
| Purple on lavender | A given number from setup |
| Orange | A value you entered |
| Green on gray | A guess; gray backgrounds also mark values entered after a guess |
| Steel blue | A value filled in by `n` or `a`; "solved" on the status line |
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
