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

package io.github.aivanov61.sudoku.ui.theme

import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Immutable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Conflict
import io.github.aivanov61.sudoku.game.MessageKind

/**
 * The game's own colors, which Material 3 has no names for: the terminal's (ui/terminal/display_attrs.py), each as
 * it reads on the theme's background (see CLAUDE.md's Colors).  The board itself is the theme's surface, which shows
 * through a cell outside any guess or conflict.
 */
@Immutable
data class GameColors(
    val guessShades: List<Color>,  // behind a cell by the depth of the guess it was entered at, the first the nearest the surface
    val givenBackground: Color,
    val conflictingBackground: Color,  // behind the value just entered that clashes with a related cell
    val conflictedBackground: Color,  // behind a value it clashes with
    val highlight: Color,  // see-through, over each cell related to the selected one
    val values: ValueColors,
    val valuesOnYellow: ValueColors,  // the values on the conflicted background
    val conflicting: Color,  // the value just entered that clashes
    val hint: Color,  // successes and hints
    val notice: Color,  // every other message
) {
    init {
        require(guessShades.size == GUESS_SHADES) { "the game is told there are $GUESS_SHADES shades" }
    }

    /**
     * What is drawn behind the cell: its conflict's yellow, else a given's background, else its guess's shade, else
     * nothing, so the board shows through; with the highlight over it when the cell is [related] to the selected one
     */
    fun background(cell: CellState?, related: Boolean): Color {
        val own = when {
            cell == null -> Color.Transparent
            cell.conflict == Conflict.CONFLICTING -> conflictingBackground
            cell.conflict == Conflict.CONFLICTED -> conflictedBackground
            cell.kind == CellKind.INITIAL -> givenBackground
            cell.depth > 0 -> guessShades[minOf(cell.depth, GUESS_SHADES) - 1]
            else -> Color.Transparent
        }
        return if (related) highlight.compositeOver(own) else own
    }

    /** The color of the cell's value: the conflict's, or its kind's, in the colors that read on its background */
    fun value(cell: CellState): Color = when (cell.conflict) {
        Conflict.CONFLICTING -> conflicting
        Conflict.CONFLICTED -> valuesOnYellow.of(cell.kind)
        Conflict.NONE -> values.of(cell.kind)
    }

    /** The color of a message of the kind, as the terminal colors it: successes and hints, or anything else */
    fun message(kind: MessageKind): Color = when (kind) {
        MessageKind.SUCCESS, MessageKind.HINT -> hint
        else -> notice
    }

    companion object {
        /** How many shades of gray there are for guesses, the same in both themes; the game warns past the last */
        const val GUESS_SHADES = 8

        private val LIGHT_VALUES = ValueColors(
            given = Color(0xFFA020F0),  // the terminal's purple
            typed = Color(0xFF9C4A00),  // the terminal's darkorange3, darker
            guessed = Color(0xFF1B5E20),  // the terminal's green, darker
            solved = Color(0xFF01579B),  // the terminal's lightskyblue, darker
        )

        val Light = GameColors(
            guessShades = grays(first = 0xF2, step = -6),  // darker each guess, away from the light surface
            givenBackground = Color(0xFFE6E6FA),  // lavender
            conflictingBackground = Color(0xFFF9F1A5),  // bright yellow
            conflictedBackground = Color(0xFFF5D547),  // yellow, light enough for the values
            highlight = lightColorScheme().primary.copy(alpha = 0.12f),
            values = LIGHT_VALUES,
            valuesOnYellow = LIGHT_VALUES,
            conflicting = Color(0xFFC50F1F),  // red
            hint = LIGHT_VALUES.solved,
            notice = Color(0xFF7A5900),  // the terminal's yellow, as dark as body text needs on a light surface
        )

        val Dark = Light.copy(
            guessShades = grays(first = 0x24, step = 6),  // lighter each guess, away from the dark surface, as in the terminal
            highlight = Color.White.copy(alpha = 0.08f),
            values = ValueColors(
                given = LIGHT_VALUES.given,  // on its lavender in both themes
                typed = Color(0xFFFFA500),  // orange
                guessed = Color(0xFF32CD32),  // limegreen
                solved = Color(0xFF87CEFA),  // lightskyblue
            ),
            hint = Color(0xFF87CEFA),  // lightskyblue
            notice = Color(0xFFC19C00),  // yellow
        )

        /** The guess shades: GUESS_SHADES grays, from the first level, each step further (0 to 255) */
        private fun grays(first: Int, step: Int) = List(GUESS_SHADES) { index ->
            val level = first + step * index
            Color(level, level, level)
        }
    }
}

/** The colors of the values, one for each kind */
@Immutable
data class ValueColors(val given: Color, val typed: Color, val guessed: Color, val solved: Color) {
    fun of(kind: CellKind): Color = when (kind) {
        CellKind.INITIAL -> given
        CellKind.TYPED -> typed
        CellKind.GUESS -> guessed
        CellKind.SOLVED -> solved
    }
}
