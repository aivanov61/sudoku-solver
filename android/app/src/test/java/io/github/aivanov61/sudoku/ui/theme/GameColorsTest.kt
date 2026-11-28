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

import androidx.compose.material3.ColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import androidx.compose.ui.graphics.luminance
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Conflict
import io.github.aivanov61.sudoku.game.MessageKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class GameColorsTest {
    private val colors = GameColors.Light

    // Backgrounds

    @Test
    fun aCellOutsideAnyGuessLetsTheBoardShowThrough() {
        assertEquals(Color.Transparent, colors.background(cell()))
    }

    @Test
    fun eachGuessDeeperHasTheNextShade() {
        val shades = (1..GameColors.GUESS_SHADES).map { colors.background(cell(depth = it)) }
        assertEquals(colors.guessShades, shades)
    }

    @Test
    fun guessesDeeperThanTheLastShadeRepeatIt() {
        val deeper = colors.background(cell(depth = GameColors.GUESS_SHADES + 1))
        assertEquals(colors.guessShades.last(), deeper)
    }

    @Test
    fun aGivenLetsTheBoardShowThrough() {
        assertEquals(Color.Transparent, colors.background(cell(CellKind.INITIAL)))
    }

    @Test
    fun aConflictShowsOverTheKindAndTheShade() {
        val conflicting = cell(CellKind.INITIAL, Conflict.CONFLICTING)
        val conflicted = cell(CellKind.GUESS, Conflict.CONFLICTED, depth = 2)
        assertEquals(colors.conflictingBackground, colors.background(conflicting))
        assertEquals(colors.conflictedBackground, colors.background(conflicted))
    }

    @Test
    fun bothThemesHaveTheSameNumberOfShades() {
        assertEquals(GameColors.GUESS_SHADES, GameColors.Light.guessShades.size)
        assertEquals(GameColors.GUESS_SHADES, GameColors.Dark.guessShades.size)
    }

    // Values

    @Test
    fun aValueHasItsKindsColor() {
        val kinds = CellKind.entries.map { colors.value(cell(it)) }
        assertEquals(CellKind.entries.map { colors.values.of(it) }, kinds)
    }

    @Test
    fun theValueJustEnteredThatClashesHasTheConflictsColor() {
        assertEquals(colors.conflicting, colors.value(cell(CellKind.SOLVED, Conflict.CONFLICTING)))
    }

    @Test
    fun aValueItClashesWithHasItsKindsColorForTheYellow() {
        assertEquals(GameColors.Dark.valuesOnYellow.solved, GameColors.Dark.value(cell(CellKind.SOLVED, Conflict.CONFLICTED)))
    }

    // Messages

    @Test
    fun successesAndHintsHaveTheHintColorAndEverythingElseTheNoticeColor() {
        val hints = MessageKind.entries.filter { colors.message(it) == colors.hint }
        assertEquals(listOf(MessageKind.SUCCESS, MessageKind.HINT), hints)
        assertTrue(MessageKind.entries.all { it in hints || colors.message(it) == colors.notice })
    }

    // Readable in both themes

    @Test
    fun everyValueReadsOnEveryBackgroundItCanBeDrawnOn() {
        assertReadable(VALUE_CONTRAST) { gameColors, scheme ->
            everyCell().map { cell -> Triple("$cell", gameColors.value(cell), gameColors.background(cell).over(scheme)) }
        }
    }

    @Test
    fun thePossibleValuesReadOnAnEmptyCell() {
        assertReadable(TEXT_CONTRAST) { gameColors, scheme ->
            listOf(Triple("empty", scheme.onSurfaceVariant, gameColors.background(cell()).over(scheme)))
        }
    }

    @Test
    fun everyKindThePadEntersReadsOnItsKeys() {
        val entered = listOf(CellKind.INITIAL, CellKind.TYPED, CellKind.GUESS)
        assertReadable(VALUE_CONTRAST) { gameColors, scheme ->
            entered.map { Triple("$it", gameColors.values.of(it), scheme.secondaryContainer) }  // a filled tonal button's
        }
    }

    @Test
    fun everyMessageReadsInTheMessageArea() {
        assertReadable(TEXT_CONTRAST) { gameColors, scheme ->
            MessageKind.entries.map { Triple("$it", gameColors.message(it), scheme.surfaceContainerHigh) }
        }
    }

    // Private functions

    private fun cell(kind: CellKind = CellKind.TYPED, conflict: Conflict = Conflict.NONE, depth: Int = 0) =
        CellState(5, kind, conflict, depth, emptySet(), emptySet())

    /**
     * A cell of every kind, conflict and guess depth, one deeper than the last shade too; a given only outside any
     * guess, as givens are entered in setup, where there are no guesses
     */
    private fun everyCell() = CellKind.entries.flatMap { kind ->
        Conflict.entries.flatMap { conflict ->
            depths(kind).map { depth -> cell(kind, conflict, depth) }
        }
    }

    private fun depths(kind: CellKind) = if (kind == CellKind.INITIAL) 0..0 else 0..GameColors.GUESS_SHADES + 1

    /** The color as it shows on the theme's surface, which shows through where it is see-through */
    private fun Color.over(scheme: ColorScheme) = compositeOver(scheme.surface)

    /** Assert that each (what, text, background) the pairs give, in both themes, has at least the contrast ratio */
    private fun assertReadable(ratio: Float, pairs: (GameColors, ColorScheme) -> List<Triple<String, Color, Color>>) {
        val themes = listOf(Theme("light", GameColors.Light, lightColorScheme()), Theme("dark", GameColors.Dark, darkColorScheme()))
        val unreadable = themes.flatMap { theme ->
            pairs(theme.colors, theme.scheme)
                .filter { (_, text, background) -> contrast(text, background) < ratio }
                .map { (what, text, background) -> "${theme.name}: $what, %.2f".format(contrast(text, background)) }
        }
        assertEquals(emptyList<String>(), unreadable)
    }

    /** The game's colors and Material's, in one theme */
    private class Theme(val name: String, val colors: GameColors, val scheme: ColorScheme)

    /** WCAG's contrast ratio, from 1 (none) to 21 (black on white) */
    private fun contrast(first: Color, second: Color): Float {
        val (lighter, darker) = listOf(first.luminance(), second.luminance()).sortedDescending()
        return (lighter + 0.05f) / (darker + 0.05f)
    }

    companion object {
        const val VALUE_CONTRAST = 3f  // WCAG's least for large text, as a cell's value is
        const val TEXT_CONTRAST = 4.5f  // WCAG's least for body text
    }
}
