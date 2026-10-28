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

from enum import Enum


class Action(Enum):
    """Everything the player can ask the game to do; each value names the puzzle method that does it (plus "_")"""

    PLAY = "play"
    INIT = "init"
    VALUE = "value"
    GUESS = "guess"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    DEL = "del"
    UNDO = "undo"
    REWIND = "rewind"
    AUTO = "auto"
    NEXT = "next"
    MARKS = "marks"
    SAVE = "save"
    OPEN = "open"
    QUIT = "quit"
    FORCE_QUIT = "force_quit"  # stop at once, without asking (e.g. CTRL-C); never offered for a key


class Mode(Enum):
    """The puzzle's modes; the value is the mode's name for the player"""

    SETUP = "SETUP"
    PLAY = "PLAY"


# The actions each mode offers; the puzzle refuses the others with a warning
OFFERED_ACTIONS = {
    Mode.SETUP: (
        Action.PLAY, Action.VALUE, Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.DEL,
        Action.SAVE, Action.OPEN, Action.QUIT,
    ),
    Mode.PLAY: (
        Action.INIT, Action.VALUE, Action.GUESS, Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT,
        Action.UNDO, Action.REWIND, Action.AUTO, Action.NEXT, Action.MARKS, Action.SAVE, Action.OPEN, Action.QUIT,
    ),
}
