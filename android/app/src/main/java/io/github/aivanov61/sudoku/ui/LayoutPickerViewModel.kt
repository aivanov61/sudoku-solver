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
import io.github.aivanov61.sudoku.data.Layout
import io.github.aivanov61.sudoku.data.LayoutRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** Everything the layout picker holds: the [layouts] to choose from, null until read */
data class LayoutPickerUiState(val layouts: List<Layout>? = null) {
    /** Whether the layouts are known and none of them can be picked, so the picker says why it offers nothing */
    val noneCanBePicked: Boolean = layouts?.none { it.canPick } == true
}

/**
 * The layout picker's state holder: it reads the layouts from the [LayoutRepository] for the picker to show.  A pick
 * is navigation, so the screen passes it up to the app rather than to this view model.
 */
class LayoutPickerViewModel(private val layoutRepository: LayoutRepository) : ViewModel() {
    private val state = MutableStateFlow(LayoutPickerUiState())

    /** The screen's state while it is shown */
    val uiState: StateFlow<LayoutPickerUiState> = state.asStateFlow()

    init {
        viewModelScope.launch {
            state.value = LayoutPickerUiState(layoutRepository.layouts())
        }
    }

    companion object {
        /** Makes the layout picker's view model over the layout repository, from the app's container */
        val Factory = viewModelFactory {
            initializer {
                val application = checkNotNull(this[APPLICATION_KEY]) as SudokuApplication
                LayoutPickerViewModel(application.container.layoutRepository)
            }
        }
    }
}
