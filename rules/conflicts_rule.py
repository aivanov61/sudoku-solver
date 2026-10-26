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

from cell import Cell
from display import Display
from rules.rule import Outcome, Rule


class ConflictsRule(Rule):
    """Solving cannot go on while values conflict"""

    def apply(self, puzzle) -> Outcome:
        if puzzle.first_cell_where(Cell.is_marked_in_conflict) is None:
            return Outcome.NONE
        Display.warn("Resolve the conflicts first. ", wait=True)
        return Outcome.STOPPED
