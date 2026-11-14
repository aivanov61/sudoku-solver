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

package io.github.aivanov61.sudoku

import io.github.aivanov61.sudoku.data.GameRepository
import io.github.aivanov61.sudoku.game.Game
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob

/**
 * The app's dependencies, shared for as long as the app runs: dependency injection by hand, as Google's guide
 * describes it.  SudokuApplication holds the one container; ViewModel factories ask it for what their ViewModels
 * need, instead of making it themselves.
 */
interface AppContainer {
    val gameRepository: GameRepository
}

/**
 * The real dependencies.  It makes each game with newGame (SudokuApplication gives it the game written in Python),
 * and keeps the app-long work in applicationScope.
 */
class DefaultAppContainer(
    private val newGame: () -> Game,
    /**
     * Where the app-long work runs, such as the repository folding the game's events: it is never cancelled, and
     * SupervisorJob keeps one failing coroutine from cancelling the others
     */
    private val applicationScope: CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default),
) : AppContainer {
    private var current: GameRepository? = null

    /**
     * The repository of the game in play: made when first asked for, which starts the game, and made anew once that
     * game is over, so a screen opened after quitting gets a new game rather than the finished one.  Only ViewModel
     * factories ask for it, on the UI thread, so it needs no locking.
     */
    override val gameRepository: GameRepository
        get() = current?.takeUnless { it.state.value.isOver } ?: newRepository()

    // Private functions

    private fun newRepository(): GameRepository =
        GameRepository(newGame(), applicationScope).also { current = it }
}
