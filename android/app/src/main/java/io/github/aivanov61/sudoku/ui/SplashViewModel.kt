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
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.time.Duration.Companion.seconds

/** Everything the splash screen holds: the notice and if the splash has ended or not */
data class SplashUiState(val notice: String = "", val hasEnded: Boolean = false)

/**
 * The splash screen's state holder: it reads the GNU GPL notice from the [CopyrightRepository] for the screen to
 * show, and ends the splash after five seconds, or as soon as the player taps the screen ([onTap]).
 */
class SplashViewModel(private val copyright: CopyrightRepository) : ViewModel() {
    private val state = MutableStateFlow(SplashUiState())

    /** The screen's state while it is shown */
    val uiState: StateFlow<SplashUiState> = state.asStateFlow()

    // Read the notice and start the timer, each in its own coroutine
    init {
        // The notice
        viewModelScope.launch {
            val notice = copyright.notice()
            state.update { it.copy(notice = notice) }
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
    private fun end() = state.update { it.copy(hasEnded = true) }

    companion object {
        /** How long the splash screen is shown if the screen is never tapped */
        private val SHOWN_FOR = 5.seconds

        /** Makes the splash screen view model over the copyright repository, from the app's container */
        val Factory = viewModelFactory {
            initializer {
                val application = checkNotNull(this[APPLICATION_KEY]) as SudokuApplication
                SplashViewModel(application.container.copyrightRepository)
            }
        }
    }
}
