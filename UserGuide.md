# Sudoku: User Guide

This program lets you type in a 9x9 Sudoku puzzle, such as one from a newspaper or puzzle book, and then solve it in your terminal. As you play, each cell shows the values still possible for it, mistakes are highlighted, and you can undo moves.

## Getting started

1. Install Python 3, then the `blessed` package: `pip install -r requirements.txt`
2. In a terminal, go to the program's folder and run: `python sudoku.py`
3. A copyright notice appears. It goes away after 5 seconds, or press any key.

The terminal window needs to be at least **54 columns wide and 29 lines tall**. If it's smaller, the program asks you to resize it. Press `Enter` when you're done, or `CTRL-C` to quit.

## The screen

- **The grid:** 81 cells in nine 3x3 boxes. Thick borders mark the boxes.
- **Each cell** shows its value in the middle line and, along its bottom line, the values still possible for it, in small digits. They update as you enter, change, delete or undo values. When more than 5 values are possible, you'll see `.....` instead.
- **The cursor** sits on the selected cell. That's where your next entry goes.
- **The status line** under the grid lists the main keys for the current mode. Warnings also appear there in yellow.

## Two modes

You start in **setup mode**, where you type in the puzzle's given numbers. Then you switch to **play mode** to solve it.

### Setup mode: entering the puzzle

| Key | Action |
|---|---|
| Arrow keys, or `h` `j` `k` `l` | Move left, down, up, right |
| `1`–`9` | Enter a given number. Givens are shown in purple on lavender. |
| `Delete` | Clear the selected cell |
| `ESC` | Finish setup and start playing |
| `?` | Show all commands |
| `q` or `CTRL-C` | Quit |

### Play mode: solving

| Key | Action |
|---|---|
| Arrow keys, or `h` `j` `k` `l` | Move left, down, up, right |
| `1`–`9` | Enter a value |
| Shifted `1`–`9` (`!` `@` `#` `$` `%` `^` `&` `*` `(` on a US keyboard) | Enter a **guess** (see below) |
| `u` | Undo your last entry |
| `ESC` | Go back to setup mode (only once everything has been undone) |
| `?` | Show all commands, including ones not listed on the status line |
| `q` or `CTRL-C` | Quit |

You can't change the puzzle's given numbers during play. To fix a typo in the setup, undo all your moves, press `ESC` to go back to setup mode, correct it and press `ESC` again.

## Guesses

When you're stuck and need to try a value, enter it as a guess with a shifted digit. Guesses are shown in green on a gray background.

Every value you enter after a guess gets the same gray background, so you can see everything that depends on it. Each new guess makes the gray a shade lighter. If a guess turns out wrong, press `u` repeatedly to undo back to it. After ten nested guesses there are no lighter shades left, and the program warns you and reuses the last one.

## Conflicts

If you enter a value that's already in the same row, column or box, the cell turns **bold red on bright yellow**, and each cell it clashes with gets a **yellow background**. Replace, delete or undo the clashing value, and the cells go back to normal. A cell that clashes with more than one other cell stays marked until all of its clashes are gone.

## Colors at a glance

| Looks like | Meaning |
|---|---|
| Purple on lavender | A given number from setup |
| Orange | A value you entered |
| Green on gray | A guess; gray backgrounds also mark values entered after a guess |
| Bold red on bright yellow | The value you just entered is already in the same row, column or box |
| Usual color on yellow | Holds a value that a newer entry clashes with |
| Yellow text on the status line | A warning. If it waits, press any key to continue. |

## Current limitations

- **Rewind (`r`), auto (`a`) and next (`n`)** are listed in the help but not available yet. Pressing them shows a "does not support" warning.
- There's no redo, and puzzles can't be saved.

## Troubleshooting

- **The grid looks broken or there are odd characters:** make sure your terminal uses UTF-8 and a font with box-drawing characters.
- **The program asks you to resize:** make the window at least 54 × 29 and press `Enter`.
- **Something looks wrong on screen:** press `?` and then any key. Returning from help redraws the whole screen.
