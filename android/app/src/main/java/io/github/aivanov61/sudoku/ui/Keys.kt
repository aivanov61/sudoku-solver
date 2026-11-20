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
import io.github.aivanov61.sudoku.data.Layout
import kotlinx.serialization.Serializable
import java.util.UUID

/**
 * The app's screens, as Navigation 3's keys: the back stack is a list of them, and the last one is shown.  They are
 * @Serializable so the back stack can be saved through rotation and process death.
 */
@Serializable
sealed interface Route : NavKey {
    companion object {
        /**
         * The route that starts a game: the game on the [savedLayout], resuming it, when that layout can be picked;
         * else the game when there is exactly one layout and it can be picked, as the terminal plays it; else the picker
         */
        fun toStart(layouts: List<Layout>, savedLayout: String? = null): Route {
            val saved = layouts.find { it.name == savedLayout }
            val layout = saved?.takeIf { it.canPick } ?: layouts.singleOrNull()?.takeIf { it.canPick }
            return layout?.let { Game(it.name) } ?: LayoutPicker
        }
    }

    /** The splash screen with the copyright notice, shown first */
    @Serializable
    data object Splash : Route

    /** The choice of puzzle layout, when there isn't exactly one to play */
    @Serializable
    data object LayoutPicker : Route

    /**
     * The game, on the [layout] named.  Each game's route has an [id] of its own, as Navigation 3 tells its entries
     * apart by their keys: a new game on the same layout then gets an entry of its own, with ViewModels of its own.
     * The id has no default, so it is saved with the back stack, and the game keeps its entry after process death.
     */
    @Serializable
    data class Game(val layout: String, val id: String) : Route {
        /** A new game's route, on the [layout] named */
        constructor(layout: String) : this(layout, UUID.randomUUID().toString())
    }
}
