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
import io.github.aivanov61.sudoku.game.GameAction

/**
 * Everything the game screen shows: the game as last reported, and what the screen works out from it; and the
 * screen's own state: whether New puzzle is asking the player first, and the route that replaces the game, null
 * until a new puzzle has been asked for and the game has ended
 */
data class SudokuUiState(
    val game: GameState = GameState(),
    val askingNewPuzzle: Boolean = false,
    val next: Route? = null,
) {
    /** The action that switches between setup and play: whichever of the two the mode offers */
    val modeSwitch: GameAction
        get() = if (GameAction.PLAY in game.offered) GameAction.PLAY else GameAction.INIT

    /**
     * Whether a new puzzle can be started: once the game has started or failed.  Before that, the game may still be
     * restoring the saved game, which ending it would then delete unasked.
     */
    val canStartNew: Boolean
        get() = game.size != null || game.failure != null
}
