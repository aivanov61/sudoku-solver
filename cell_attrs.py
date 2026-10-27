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

class CellAttrs:
    """
    What a cell's attributes mean, whatever way the cell is shown.  A cell's attributes are a tuple of:
    - at most one primary attribute, telling how the value got there: INITIAL (a given), GUESS or SOLVED
      (found by next or auto); a typed value has none
    - at most one conflict mark: CONFLICTING (the value just entered clashes with a related cell) or
      CONFLICTED (a value the one just entered clashes with)
    - dict(depth=n) when the value was entered while n guesses were in play

    The values are also written to save files, so they must not change.
    """

    INITIAL = "initial"
    GUESS = "guess"
    SOLVED = "solved"
    CONFLICTING = "conflicting"
    CONFLICTED = "conflicted"
    PRIMARY = (INITIAL, GUESS, SOLVED)
    CONFLICT_ATTRS = (CONFLICTING, CONFLICTED)
