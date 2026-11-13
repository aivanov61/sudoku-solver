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
import io.github.aivanov61.sudoku.data.GameRepository
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.Position
import io.github.aivanov61.sudoku.game.PythonGame
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/**
 * The game screen's state holder: it turns the game's state (from GameRepository) into SudokuUiState, and the
 * player's intents into the game's actions, each run in viewModelScope so it ends if the screen is closed for good.
 */
class SudokuViewModel(private val repository: GameRepository) : ViewModel(), SudokuIntents {
    /** The screen's state, worked out while the screen is shown (and for 5 seconds after, to ride out a rotation) */
    val uiState: StateFlow<SudokuUiState> = repository.state
        .map { SudokuUiState(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), SudokuUiState(repository.state.value))

    // Interface required for the screen

    override fun onCellTapped(position: Position) = act(GameAction.SELECT, position = position)

    override fun onDigit(digit: Int) = act(GameAction.VALUE, digit = digit)

    override fun onClear() = act(GameAction.DEL)

    override fun onSwitchMode() = act(SudokuUiState(repository.state.value).modeSwitch)

    override fun onQuit() = act(GameAction.QUIT)

    override fun onAnswer(yes: Boolean) {
        viewModelScope.launch { repository.answer(yes) }
    }

    // Private functions

    private fun act(action: GameAction, digit: Int? = null, position: Position? = null) {
        viewModelScope.launch { repository.act(action, digit, position) }
    }

    companion object {
        /**
         * Makes the view model over the real game, written in Python.  For now the repository is made here, in a
         * scope of its own for the app's lifetime; phase 2 moves it into an app container (dependency injection).
         */
        val Factory = viewModelFactory {
            initializer {
                val game = PythonGame(checkNotNull(this[APPLICATION_KEY]))
                SudokuViewModel(GameRepository(game, CoroutineScope(SupervisorJob())))
            }
        }
    }
}
