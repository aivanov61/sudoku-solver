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
import io.github.aivanov61.sudoku.data.GameRepository
import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.data.LayoutRepository
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.Position
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/**
 * The game screen's state holder: it turns the game's state (from GameRepository) into SudokuUiState, and the
 * player's intents into the game's actions, each run in viewModelScope so it ends if the screen is closed for good.
 * New puzzle ends the game, and gives the route that starts the next one, from the layouts in the LayoutRepository.
 */
class SudokuViewModel(
    private val repository: GameRepository,
    private val layoutRepository: LayoutRepository,
) : ViewModel(), SudokuIntents {
    private val askingNewPuzzle = MutableStateFlow(false)
    private val next = MutableStateFlow<Route?>(null)

    /** The screen's state, worked out while the screen is shown (and for 5 seconds after, to ride out a rotation) */
    val uiState: StateFlow<SudokuUiState> = combine(repository.state, askingNewPuzzle, next, ::SudokuUiState)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), SudokuUiState(repository.state.value))

    // Interface required for the screen

    override fun onCellTapped(position: Position) = act(GameAction.SELECT, position = position)

    override fun onDigit(digit: Int) = act(GameAction.VALUE, digit = digit)

    override fun onClear() = act(GameAction.DEL)

    override fun onSwitchMode() = act(SudokuUiState(repository.state.value).modeSwitch)

    override fun onAnswer(yes: Boolean) {
        viewModelScope.launch { repository.answer(yes) }
    }

    /** Tell the game the player has seen its message: the OK is the answer it waits for */
    override fun onInformed() = onAnswer(true)

    /** Ask the player first when the board has values, which a new puzzle would lose; else start it at once */
    override fun onNewPuzzle() {
        if (repository.state.value.hasValues) {
            askingNewPuzzle.value = true
        } else {
            startNewPuzzle()
        }
    }

    override fun onNewPuzzleAnswer(yes: Boolean) {
        askingNewPuzzle.value = false
        if (yes) {
            startNewPuzzle()
        }
    }

    // Interface required for the activity

    /** Have the game saved when the app is stopped, since Android may then end it without warning */
    fun onStopped() = repository.save()

    // Private functions

    private fun act(action: GameAction, digit: Int? = null, position: Position? = null) {
        viewModelScope.launch { repository.act(action, digit, position) }
    }

    /**
     * End the game, unless it has already ended (failed), and once it has, give the route that starts the next one:
     * with the saved game deleted as the game ended, the only layout's game, or the picker
     */
    private fun startNewPuzzle() {
        viewModelScope.launch {
            if (!repository.state.value.hasEnded) {
                repository.act(GameAction.FORCE_QUIT)
            }
            val layouts = layoutRepository.layouts()
            repository.state.first { it.hasEnded }
            next.value = Route.toStart(layouts)
        }
    }

    /** Whether any cell has a value */
    private val GameState.hasValues: Boolean
        get() = cells.values.any { it.value != null }

    companion object {
        /** Makes the view model over the game on the [layout] named, and the layouts, from the app's container */
        fun factory(layout: String) = viewModelFactory {
            initializer {
                val container = (checkNotNull(this[APPLICATION_KEY]) as SudokuApplication).container
                SudokuViewModel(container.gameRepository(layout), container.layoutRepository)
            }
        }
    }
}
