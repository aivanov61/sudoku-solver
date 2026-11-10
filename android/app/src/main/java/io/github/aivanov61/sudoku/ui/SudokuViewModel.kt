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
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import io.github.aivanov61.sudoku.game.Game
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.Position
import io.github.aivanov61.sudoku.game.PythonGame
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

/**
 * The game's state for the screen, kept for as long as the app runs, through rotations: it starts the game, turns
 * what the game reports into SudokuUiState, and turns the player's intents into the game's actions.
 */
class SudokuViewModel(private val game: Game) : ViewModel(), SudokuIntents {
    private val state = MutableStateFlow(SudokuUiState())
    val uiState: StateFlow<SudokuUiState> = state.asStateFlow()

    init {
        game.start { event -> state.update { it.after(event) } }
    }

    // Interface required for the screen

    override fun onCellTapped(position: Position) = game.act(GameAction.SELECT, position = position)

    override fun onDigit(digit: Int) = game.act(GameAction.VALUE, digit = digit)

    override fun onClear() = game.act(GameAction.DEL)

    override fun onSwitchMode() = game.act(state.value.modeSwitch)

    override fun onQuit() = game.act(GameAction.QUIT)

    override fun onAnswer(yes: Boolean) {
        state.update { it.answered() }
        game.answer(yes)
    }

    companion object {
        /** Makes the view model with the real game, written in Python */
        val Factory = viewModelFactory {
            initializer { SudokuViewModel(PythonGame(checkNotNull(this[APPLICATION_KEY]))) }
        }
    }
}
