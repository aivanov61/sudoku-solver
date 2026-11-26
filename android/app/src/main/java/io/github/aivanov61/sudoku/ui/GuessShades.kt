// -----------------------------------------------------------------------------
// Copyright (c) by Anton Ivanov.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
// -----------------------------------------------------------------------------

package io.github.aivanov61.sudoku.ui

import androidx.compose.ui.graphics.Color

/**
 * The shades of gray behind a cell, by the depth of the guess it was entered at: the first guess the lightest, each
 * deeper one darker, in even steps, and any deeper than the last shade in the last one, as in the terminal.  The game
 * is told how many there are, and warns when guesses go deeper than the last.  The darkest is still light enough for
 * a value to be read on it.
 */
object GuessShades {
    val COLORS = listOf(
        Color(0xFFEEEEEE),
        Color(0xFFE0E0E0),
        Color(0xFFD2D2D2),
        Color(0xFFC4C4C4),
        Color(0xFFB6B6B6),
        Color(0xFFA8A8A8),
        Color(0xFF9A9A9A),
        Color(0xFF8C8C8C),
    )

    /** The shade behind a cell entered [depth] guesses deep, or null for one outside any guess (depth 0) */
    fun of(depth: Int): Color? = if (depth > 0) COLORS[minOf(depth, COLORS.size) - 1] else null
}
