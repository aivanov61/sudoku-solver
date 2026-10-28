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

"""Shared by the rule tests: ask a rule for its move in a mock puzzle"""

import sys
from unittest.mock import MagicMock

sys.path.insert(0, ".")


def board_puzzle(board):
    """A mock puzzle whose houses and cells are those of a real board, for rules that look at houses"""
    puzzle = MagicMock()
    puzzle.houses.side_effect = board.houses
    puzzle.first_cell_where.side_effect = board.first_cell_where
    return puzzle


def find_with(rule, cell):
    """Return the rule's move in a mock puzzle whose first matching cell is the given one, and the puzzle"""
    puzzle = MagicMock()
    puzzle.first_cell_where.return_value = cell
    return rule.find(puzzle), puzzle
