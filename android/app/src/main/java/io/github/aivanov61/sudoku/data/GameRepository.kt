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

package io.github.aivanov61.sudoku.data

import io.github.aivanov61.sudoku.game.Game
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.Position
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.runningFold
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.withContext

/**
 * The data layer's one way to the game.  It keeps the game's state as last reported, for as long as the scope
 * lives (the app's, so it outlasts any screen), and carries out the player's actions off the UI thread, in order.
 */
class GameRepository(
    private val game: Game,
    scope: CoroutineScope,
    private val inOrder: CoroutineDispatcher = OFF_UI_THREAD_IN_ORDER,  // runs calls one at a time, first in first out
) {
    /** The game as it last reported itself; the game starts as soon as the repository is made */
    val state: StateFlow<GameState> = game.events
        .runningFold(GameState()) { state, event -> state.after(event) }
        .stateIn(scope, SharingStarted.Eagerly, GameState())

    suspend fun act(action: GameAction, digit: Int? = null, position: Position? = null) =
        withContext(inOrder) { game.act(action, digit, position) }

    suspend fun answer(yes: Boolean) = withContext(inOrder) { game.answer(yes) }

    private companion object {
        /**
         * Calls into the game run off the UI thread, and one at a time, so the game gets the player's actions in the
         * order they were made: on Dispatchers.IO itself, a pool of threads, a tap and the digit right after it
         * could overtake each other.
         */
        val OFF_UI_THREAD_IN_ORDER = Dispatchers.IO.limitedParallelism(1)
    }
}
