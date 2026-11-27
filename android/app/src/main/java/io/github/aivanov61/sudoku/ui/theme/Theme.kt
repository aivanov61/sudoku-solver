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

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.runtime.staticCompositionLocalOf

/** The game's colors of the theme the content is shown in */
private val LocalGameColors = staticCompositionLocalOf { GameColors.Light }

/**
 * The app's theme: Material 3's baseline light or dark color scheme, as the phone is set, with the game's own colors
 * to match.  Dynamic color (Material You) stays off, as the board's colors carry meaning.
 */
@Composable
fun SudokuTheme(dark: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalGameColors provides if (dark) GameColors.Dark else GameColors.Light) {
        MaterialTheme(colorScheme = if (dark) darkColorScheme() else lightColorScheme(), content = content)
    }
}

/** What the theme gives the composables inside it, beside MaterialTheme's */
object SudokuTheme {
    val gameColors: GameColors
        @Composable
        @ReadOnlyComposable
        get() = LocalGameColors.current
}
