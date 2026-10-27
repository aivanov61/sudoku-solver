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

from display import Display


class Commands:
    """
    Establish puzzle commands
    """

    DIGITS = "123456789"
    SHIFTED_DIGITS = "!@#$%^&*("
    unshifted_value = str.maketrans(SHIFTED_DIGITS, DIGITS)

    # Each command's "panel" lists the lines it shows in the command panel: (keys, name)
    HELP_CMD = {
        "help": {
            "keys": ["?"],
            "panel": [("?", "help")],
            "long": 'The "?" key will give this help screen',
        },
    }

    MOVE_CMDS = {
        "up": {
            "keys": ["k", "K", "KEY_UP"],
            "panel": [("k ↑", "up")],
            "long": 'Use "k" or UP-arrow to move up one cell',
        },
        "down": {
            "keys": ["j", "J", "KEY_DOWN"],
            "panel": [("j ↓", "down")],
            "long": 'Use "j" or DOWN-arrow to move down one cell',
        },
        "left": {
            "keys": ["h", "H", "KEY_LEFT"],
            "panel": [("h ←", "left")],
            "long": 'Use "h" or LEFT-arrow to move left one cell',
        },
        "right": {
            "keys": ["l", "L", "KEY_RIGHT"],
            "panel": [("l →", "right")],
            "long": 'Use "l" or RIGHT-arrow to move right one cell',
        },
    }

    COMMON_CMDS = {
        "save": {
            "keys": "sS",
            "panel": [("s", "save")],
            "long": 'Use "s" to save the puzzle to a file',
        },
        "open": {
            "keys": "oO",
            "panel": [("o", "open")],
            "long": 'Use "o" to restore a puzzle saved to a file - it replaces the current puzzle (asks first)',
        },
        "quit": {
            "keys": "qQ",
            "panel": [("q CTRL-C", "quit")],
            "long": 'Use "q" to quit the Sudoku puzzle (asks first) or CTRL-C to quit at once',
        },
    }

    INIT_COMMANDS = {
        "play": {
            "keys": ["KEY_ESCAPE"],
            "panel": [("ESC", "PLAY")],
            "long": "Hit ESC to exit initialization mode and start playing the puzzle",
        },
        **HELP_CMD,
        "#": {
            "keys": DIGITS + SHIFTED_DIGITS,
            "panel": [("1-9", "value")],
            "long": "Enter a given number [1-9]",
        },
        **MOVE_CMDS,
        "del": {
            "keys": ["KEY_DELETE"],
            "panel": [("Del", "clear")],
            "long": "Delete/clear initialized value",
        },
        "undo": {
            "keys": "uU",
            "panel": [],
            "long": Display.term.yellow("[hidden]") + ' "u" (undo) is available only while playing',
        },
        "rewind": {
            "keys": "rR",
            "panel": [],
            "long": Display.term.yellow("[hidden]") + ' "r" (rewind) is available only while playing',
        },
        "auto": {
            "keys": "aA",
            "panel": [],
            "long": Display.term.yellow("[hidden]") + ' "a" (auto) is available only while playing',
        },
        "next": {
            "keys": "nN",
            "panel": [],
            "long": Display.term.yellow("[hidden]") + ' "n" (next) is available only while playing',
        },
    }

    PLAY_COMMANDS = {
        "init": {
            "keys": ["KEY_ESCAPE"],
            "panel": [("ESC", "SETUP")],
            "long": "Hit ESC to re-enter initialization mode (once everything has been undone)",
        },
        **HELP_CMD,
        "#": {
            "keys": DIGITS + SHIFTED_DIGITS,
            "panel": [("1-9", "value"), ("shift 1-9", "guess")],
            "long": "Enter a single digit [1-9]; when SHIFTED, it is a rewindable guess",
        },
        **MOVE_CMDS,
        "undo": {
            "keys": "uU",
            "panel": [("u", "undo")],
            "long": 'Use "u" to undo the last entered cell value',
        },
        "rewind": {
            "keys": "rR",
            "panel": [("r", "rewind")],
            "long": 'Use "r" to rewind to the most recent guess (to choose a new guess) - asks first',
        },
        "auto": {
            "keys": "aA",
            "panel": [("a", "auto")],
            "long": 'Use "a" to auto-play up to point where a guess must be made - if any',
        },
        "next": {
            "keys": "nN",
            "panel": [("n", "next")],
            "long": 'Use "n" to auto-play the next "must be" cell value',
        },
        "del": {
            "keys": ["KEY_DELETE"],
            "panel": [],
            "long": Display.term.yellow("[hidden]") + " DEL key is available only in initialization mode",
        },
    }

    # Note: this is the starting value of CMDS; the puzzle can change it as desired
    CMDS = {**INIT_COMMANDS, **COMMON_CMDS}

    def use(mode_cmds):
        """Make the given mode's commands plus the common commands the active ones"""
        Commands.CMDS = {**mode_cmds, **Commands.COMMON_CMDS}

    def is_value(cmd):
        return cmd in Commands.DIGITS + Commands.SHIFTED_DIGITS

    def val_with_guess(cmd):
        return int(str(cmd).translate(Commands.unshifted_value)), cmd in Commands.SHIFTED_DIGITS

    def panel() -> list:
        """The active commands' lines for the command panel: (keys, name)"""
        return [line for cmd in Commands.CMDS.values() for line in cmd["panel"]]

    def long_help():
        """Long help - a one-pager"""
        return "\n".join(
            [f'{k.upper()} - {Commands.CMDS[k]["long"]}' for k in Commands.CMDS.keys() if Commands.CMDS[k]["long"]]
        )
