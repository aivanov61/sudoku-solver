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

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider.AndroidViewModelFactory.Companion.APPLICATION_KEY
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import io.github.aivanov61.sudoku.SudokuApplication
import io.github.aivanov61.sudoku.data.CopyrightRepository
import io.github.aivanov61.sudoku.data.Layout
import io.github.aivanov61.sudoku.data.LayoutRepository
import io.github.aivanov61.sudoku.data.SavedGameRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.time.Duration.Companion.seconds

/** Everything the splash screen holds: the notice, and the route that replaces the splash once it has ended */
data class SplashUiState(val notice: String = "", val next: Route? = null)

/**
 * The splash screen's state holder: it reads the GNU GPL notice from the [CopyrightRepository] for the screen to
 * show, and the layouts from the [LayoutRepository] and the saved game's layout from the [SavedGameRepository]
 * (which start Python behind the splash).  It ends the splash after five seconds, or as soon as the player taps the
 * screen ([onTap]); once it has ended and the route that follows is known, it gives that route.
 */
class SplashViewModel(
    private val copyright: CopyrightRepository,
    private val layoutRepository: LayoutRepository,
    private val savedGameRepository: SavedGameRepository,
) : ViewModel() {
    private val state = MutableStateFlow(SplashUiState())
    private var hasEnded = false
    private var following: Route? = null  // null until the layouts and the saved game are read

    /** The screen's state while it is shown */
    val uiState: StateFlow<SplashUiState> = state.asStateFlow()

    // Read the notice and the layouts, and start the timer, each in its own coroutine
    init {
        // The notice
        viewModelScope.launch {
            val notice = copyright.notice()
            state.update { it.copy(notice = notice) }
        }

        // The route that follows, from the layouts and the saved game: one after the other, as both go through Python
        viewModelScope.launch {
            following = next(layoutRepository.layouts(), savedGameRepository.savedLayout())
            showNextOnceKnown()
        }

        // The timer
        viewModelScope.launch {
            delay(SHOWN_FOR)
            end()
        }
    }

    /** End the splash screen when tapped */
    fun onTap() = end()

    /** End the splash screen */
    private fun end() {
        hasEnded = true
        showNextOnceKnown()
    }

    /** Give the route that follows, once the splash has ended and the route is known */
    private fun showNextOnceKnown() {
        val known = following
        if (hasEnded && known != null) {
            state.update { it.copy(next = known) }
        }
    }

    companion object {
        /** How long the splash screen is shown if the screen is never tapped */
        private val SHOWN_FOR = 5.seconds

        /** Makes the splash screen view model over its repositories, from the app's container */
        val Factory = viewModelFactory {
            initializer {
                val container = (checkNotNull(this[APPLICATION_KEY]) as SudokuApplication).container
                SplashViewModel(container.copyrightRepository, container.layoutRepository, container.savedGameRepository)
            }
        }

        /**
         * The game on the [savedLayout], resuming it, when that layout can be picked; else the game when there is
         * exactly one layout and it can be picked, as the terminal plays it; else the picker
         */
        private fun next(layouts: List<Layout>, savedLayout: String?): Route {
            val saved = layouts.find { it.name == savedLayout }
            val layout = saved?.takeIf { it.canPick } ?: layouts.singleOrNull()?.takeIf { it.canPick }
            return layout?.let { Route.Game(it.name) } ?: Route.LayoutPicker
        }
    }
}
