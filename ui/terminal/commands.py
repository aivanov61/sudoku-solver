# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import sys

sys.path.insert(0, ".")

from game.actions import Action


class Commands:
    """
    The terminal's key bindings: for each command, its keys, how the command panel shows it and its help.

    A command is one of the game's actions, or HELP, the terminal's own help screen.  A key always maps to
    its command, even where the mode doesn't offer it, so that the game can refuse it with a warning; a key
    bound to a command for each mode (ESC) maps to the one the mode offers.
    """

    HELP = "help"
    DIGITS = "123456789"
    SHIFTED_DIGITS = "!@#$%^&*("
    unshifted_value = str.maketrans(SHIFTED_DIGITS, DIGITS)

    # In command panel order; "label" shows the keys in the panel and the help, "name" what the command does
    BINDINGS = [
        {
            "command": Action.PLAY,
            "keys": ["KEY_ESCAPE"],
            "label": "ESC",
            "name": "PLAY",
            "long": "Hit ESC to exit initialization mode and start playing the puzzle",
        },
        {
            "command": Action.INIT,
            "keys": ["KEY_ESCAPE"],
            "label": "ESC",
            "name": "SETUP",
            "long": "Hit ESC to re-enter initialization mode (once everything has been undone)",
        },
        {
            "command": HELP,
            "keys": ["?"],
            "label": "?",
            "name": "help",
            "long": 'The "?" key will give this help screen',
        },
        {
            "command": Action.VALUE,
            "keys": DIGITS,
            "label": "1-9",
            "name": "value",
            "long": "Enter a single digit [1-9]; while setting up, it is a given number",
        },
        {
            "command": Action.GUESS,
            "keys": SHIFTED_DIGITS,
            "label": "shift 1-9",
            "name": "guess",
            "long": "Enter a SHIFTED digit [1-9] as a guess, which rewind can go back to",
        },
        {
            "command": Action.UP,
            "keys": ["k", "K", "KEY_UP"],
            "label": "k ↑",
            "name": "up",
            "long": 'Use "k" or UP-arrow to move up one cell',
        },
        {
            "command": Action.DOWN,
            "keys": ["j", "J", "KEY_DOWN"],
            "label": "j ↓",
            "name": "down",
            "long": 'Use "j" or DOWN-arrow to move down one cell',
        },
        {
            "command": Action.LEFT,
            "keys": ["h", "H", "KEY_LEFT"],
            "label": "h ←",
            "name": "left",
            "long": 'Use "h" or LEFT-arrow to move left one cell',
        },
        {
            "command": Action.RIGHT,
            "keys": ["l", "L", "KEY_RIGHT"],
            "label": "l →",
            "name": "right",
            "long": 'Use "l" or RIGHT-arrow to move right one cell',
        },
        {
            "command": Action.DEL,
            "keys": ["KEY_DELETE"],
            "label": "Del",
            "name": "clear",
            "long": "Delete/clear a given number",
        },
        {
            "command": Action.UNDO,
            "keys": "uU",
            "label": "u",
            "name": "undo",
            "long": 'Use "u" to undo the last entered cell value',
        },
        {
            "command": Action.REWIND,
            "keys": "rR",
            "label": "r",
            "name": "rewind",
            "long": 'Use "r" to rewind to the most recent guess (to choose a new guess) - asks first',
        },
        {
            "command": Action.AUTO,
            "keys": "aA",
            "label": "a",
            "name": "auto",
            "long": 'Use "a" to auto-play up to point where a guess must be made - if any',
        },
        {
            "command": Action.NEXT,
            "keys": "nN",
            "label": "n",
            "name": "next",
            "long": 'Use "n" to auto-play the next "must be" cell value',
        },
        {
            "command": Action.TAG,
            "keys": "mM",
            "label": "m",
            "name": "tag",
            "long": 'Use "m" to tag (mark) a cell, or untag it - while empty, it shows its small digits in steel blue',
        },
        {
            "command": Action.CONFIGURE,
            "keys": "cC",
            "label": "c",
            "name": "config",
            "long": 'Use "c" to configure the game, such as the "must be" marks; ESC goes back to the puzzle',
        },
        {
            "command": Action.SAVE,
            "keys": "sS",
            "label": "s",
            "name": "save",
            "long": 'Use "s" to save the puzzle to a file',
        },
        {
            "command": Action.OPEN,
            "keys": "oO",
            "label": "o",
            "name": "open",
            "long": 'Use "o" to restore a puzzle saved to a file - it replaces the current puzzle (asks first)',
        },
        {
            "command": Action.QUIT,
            "keys": "qQ",
            "label": "q CTRL-C",
            "name": "quit",
            "long": 'Use "q" to quit the Sudoku puzzle (asks first) or CTRL-C to quit at once',
        },
    ]

    def command_for(key, offered) -> tuple:
        """Return (command, digit) for a key, the digit only for values and guesses; None if the key is not bound"""
        bindings = [binding for binding in Commands.BINDINGS if key in binding["keys"]]
        if not bindings:
            return None
        binding = next((binding for binding in bindings if Commands.__is_offered(binding["command"], offered)), bindings[0])
        is_digit = key in Commands.DIGITS + Commands.SHIFTED_DIGITS
        return binding["command"], int(key.translate(Commands.unshifted_value)) if is_digit else None

    def panel(offered) -> list:
        """The offered commands' lines for the command panel: (keys, name)"""
        return [(binding["label"], binding["name"]) for binding in Commands.BINDINGS if Commands.__is_offered(binding["command"], offered)]

    def long_help(offered) -> str:
        """Long help - a one-pager of the offered commands, their descriptions lined up after their keys"""
        bindings = [binding for binding in Commands.BINDINGS if Commands.__is_offered(binding["command"], offered)]
        width = max(len(binding["label"]) for binding in bindings)
        return "\n".join(f'{binding["label"].ljust(width)} - {binding["long"]}' for binding in bindings)

    # Private functions

    def __is_offered(command, offered) -> bool:
        return command == Commands.HELP or command in offered
