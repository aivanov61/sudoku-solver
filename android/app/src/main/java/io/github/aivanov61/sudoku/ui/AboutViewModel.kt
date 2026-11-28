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
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** Everything the About screen holds: the GNU GPL notice, empty until read */
data class AboutUiState(val notice: String = "")

/** The About screen's state holder: it reads the GNU GPL notice from the [CopyrightRepository], as the splash does */
class AboutViewModel(private val copyright: CopyrightRepository) : ViewModel() {
    private val state = MutableStateFlow(AboutUiState())

    /** The screen's state while it is shown */
    val uiState: StateFlow<AboutUiState> = state.asStateFlow()

    init {
        viewModelScope.launch {
            val notice = copyright.notice()
            state.update { it.copy(notice = notice) }
        }
    }

    companion object {
        /** Makes the About screen's view model over the copyright repository, from the app's container */
        val Factory = viewModelFactory {
            initializer {
                val container = (checkNotNull(this[APPLICATION_KEY]) as SudokuApplication).container
                AboutViewModel(container.copyrightRepository)
            }
        }
    }
}
