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

import androidx.navigation3.runtime.NavKey
import kotlinx.serialization.Serializable

/**
 * The app's screens, as Navigation 3's keys: the back stack is a list of them, and the last one is shown.  They are
 * @Serializable so the back stack can be saved through rotation and process death.
 */
@Serializable
sealed interface Route : NavKey {
    /** The splash screen with the copyright notice, shown first */
    @Serializable
    data object Splash : Route

    /** The choice of puzzle layout, when there isn't exactly one to play */
    @Serializable
    data object LayoutPicker : Route

    /** The game, on the [layout] named */
    @Serializable
    data class Game(val layout: String) : Route
}
