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

import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameMode

/**
 * Everything the game screen shows: the game as last reported, and what the screen works out from it; and the
 * screen's own state: whether New puzzle is asking the player first, the route that replaces the game, null until a
 * new puzzle has been asked for and the game has ended, and whether the player has turned Guess on
 */
data class SudokuUiState(
    val game: GameState = GameState(),
    val askingNewPuzzle: Boolean = false,
    val next: Route? = null,
    val guessOn: Boolean = false,
) {
    /** The action that switches between setup and play: whichever of the two the mode offers */
    val modeSwitch: GameAction
        get() = if (GameAction.PLAY in game.offered) GameAction.PLAY else GameAction.INIT

    /** Whether the mode offers the action, so its command can be used; the game refuses the others with a warning */
    fun offers(action: GameAction): Boolean = action in game.offered

    /** Whether the pad enters guesses: Guess is on, and the mode offers guesses (so never in setup) */
    val guessing: Boolean
        get() = guessOn && offers(GameAction.GUESS)

    /** The kind of value the pad enters, whose color the pad and the selected cell's outline take: givens in setup */
    val entering: CellKind
        get() = when {
            game.mode == GameMode.SETUP -> CellKind.INITIAL
            guessing -> CellKind.GUESS
            else -> CellKind.TYPED
        }

    /**
     * How many places the digit has left for the pad to show: one in each row, less the cells that hold it, whatever
     * their kind and even in conflict, as the app doesn't know the solution; never fewer than none
     */
    fun left(digit: Int): Int {
        val places = game.size?.rows ?: 0
        return (places - game.cells.values.count { it.value == digit }).coerceAtLeast(0)
    }

    /**
     * Whether a new puzzle can be started: once the game has started or failed.  Before that, the game may still be
     * restoring the saved game, which ending it would then delete unasked.
     */
    val canStartNew: Boolean
        get() = game.size != null || game.failure != null
}
