# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

from display import Display


class Commands:
    """
    Establish puzzle commands
    """

    DIGITS = "123456789"
    SHIFTED_DIGITS = "!@#$%^&*("
    unshifted_value = str.maketrans(SHIFTED_DIGITS, DIGITS)

    COMMON_CMDS = {
        "help": {
            "keys": ["?"],
            "short": "?",
            "long": 'The "?" key will give this help screen',
        },
        "#": {
            "keys": DIGITS + SHIFTED_DIGITS,
            "short": "1-9/shift=guess",
            "long": "Enter a single digit [1-9]; when SHIFTED, it is a rewindable guess",
        },
        "up": {
            "keys": ["k", "K", "KEY_UP"],
            "short": "k/^",
            "long": 'Use "k" or UP-arrow to move up one cell',
        },
        "down": {
            "keys": ["j", "J", "KEY_DOWN"],
            "short": "j/v",
            "long": 'Use "j" or DOWN-arrow to move down one cell',
        },
        "left": {
            "keys": ["h", "H", "KEY_LEFT"],
            "short": "h/<",
            "long": 'Use "h" or LEFT-arrow to move left one cell',
        },
        "right": {
            "keys": ["l", "L", "KEY_RIGHT"],
            "short": "l/>",
            "long": 'Use "l" or RIGHT-arrow to move right one cell',
        },
        "quit": {
            "keys": "qQ",
            "short": "q/CTRL-C",
            "long": 'Use "q" or CTRL-C to quit the Sudoku puzzle',
        },
    }

    INIT_COMMANDS = {
        "play": {
            "keys": ["KEY_ESCAPE"],
            "short": "ESC " + Display.term.yellow("[initializing puzzle]"),
            "long": "Hit ESC to exit initialization mode and start playing the puzzle",
        },
    }

    PLAY_COMMANDS = {
        "undo": {
            "keys": "uU",
            "short": "u",
            "long": 'Use "u" to undo the last entered cell value',
        },
        "rewind": {
            "keys": "rR",
            "short": "r",
            "long": 'Use "r" to rewind to the most recent guess (to choose a new guess)',
        },
        "auto": {
            "keys": "aA",
            "short": "a",
            "long": 'Use "a" to auto-play up to point where a guess must be made - if any',
        },
        "next": {
            "keys": "nN",
            "short": "n",
            "long": 'Use "n" to auto-play the next "must be" cell value',
        },
        "init": {
            "keys": ["KEY_ESCAPE"],
            "short": None,
            "long": Display.term.yellow("[hidden]") + " Hit ESC to re-enter initialization mode",
        },
    }

    # Note: this is the starting value of CMDS; the puzzle can change it as desired
    CMDS = dict(list(COMMON_CMDS.items()) + list(INIT_COMMANDS.items()))

    def is_value(cmd):
        return cmd in Commands.DIGITS + Commands.SHIFTED_DIGITS

    def val_with_guess(cmd):
        return int(str(cmd).translate(Commands.unshifted_value)), cmd in Commands.SHIFTED_DIGITS

    def short_help():
        """Short help - a one-liner"""
        return ", ".join(
            [
                f'{k.upper()}={Display.term.red(Commands.CMDS[k]["short"])}'
                for k in Commands.CMDS.keys()
                if Commands.CMDS[k]["short"]
            ]
        )

    def long_help():
        """Long help - a one-pager"""
        return "\n".join(
            [f'{k.upper()} - {Commands.CMDS[k]["long"]}' for k in Commands.CMDS.keys() if Commands.CMDS[k]["long"]]
        )
