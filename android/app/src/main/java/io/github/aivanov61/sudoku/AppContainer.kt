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

import io.github.aivanov61.sudoku.data.CopyrightRepository
import io.github.aivanov61.sudoku.data.GameRepository
import io.github.aivanov61.sudoku.data.LayoutRepository
import io.github.aivanov61.sudoku.data.SavedGameRepository
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
    /** The repository of the game in play on the layout with the name, starting a game when there is none */
    fun gameRepository(layout: String): GameRepository

    val layoutRepository: LayoutRepository
    val copyrightRepository: CopyrightRepository
    val savedGameRepository: SavedGameRepository
}

/**
 * The real dependencies.  It makes each game, on the layout named, with [newGame] (SudokuApplication gives it the
 * game written in Python), the layouts' repository with [newLayoutRepository] (SudokuApplication gives it the game's
 * catalog), the copyright notice's repository with [newCopyrightRepository] (SudokuApplication gives it one over
 * the app's assets) and the saved game's repository with [newSavedGameRepository] (SudokuApplication gives it one
 * over the auto-save file), and keeps the app-long work in [applicationScope].
 */
class DefaultAppContainer(
    private val newGame: (layout: String) -> Game,
    private val newLayoutRepository: () -> LayoutRepository,
    private val newCopyrightRepository: () -> CopyrightRepository,
    private val newSavedGameRepository: () -> SavedGameRepository,

    /**
     * Where the app-long work runs, such as the repository folding the game's events: it is never canceled, and
     * [SupervisorJob] keeps one failing coroutine from canceling the others
     */
    private val applicationScope: CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default),
) : AppContainer {
    private var current: GameRepository? = null
    private var currentLayout: String? = null

    /**
     * Made when first asked for, which starts the game, and made anew for another layout or once that game has ended
     * (over, or failed), so a screen opened after quitting gets a new game rather than the finished one, and one
     * opened after a failure tries again.  Only ViewModel factories ask for
     * it, on the UI thread, so it needs no locking.
     */
    override fun gameRepository(layout: String): GameRepository =
        current?.takeUnless { layout != currentLayout || it.state.value.hasEnded } ?: newRepository(layout)

    /** The layouts' repository, made when first asked for */
    override val layoutRepository: LayoutRepository by lazy { newLayoutRepository() }

    /** The notice's repository, made when first asked for */
    override val copyrightRepository: CopyrightRepository by lazy { newCopyrightRepository() }

    /** The saved game's repository, made when first asked for */
    override val savedGameRepository: SavedGameRepository by lazy { newSavedGameRepository() }

    // Private functions

    private fun newRepository(layout: String): GameRepository =
        GameRepository(newGame(layout), applicationScope).also {
            current = it
            currentLayout = layout
        }
}
