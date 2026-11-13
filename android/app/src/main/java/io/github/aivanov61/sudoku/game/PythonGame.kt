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

package io.github.aivanov61.sudoku.game

import android.app.Application
import com.chaquo.python.Kwarg
import com.chaquo.python.PyException
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.channels.trySendBlocking
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlin.concurrent.thread

/**
 * The game written in Python (the repository's game/ and ui/android/), run through Chaquopy: AndroidUI.play()
 * runs on the game's own thread, reporting through a PythonScreen, and takes the player's actions from a queue.
 */
class PythonGame(private val application: Application) : Game {
    @Volatile
    private var ui: PyObject? = null  // the game's AndroidUI, once Python has started

    /**
     * The game's reports, as a Flow: callbackFlow turns PythonScreen's calls into the flow's values.  Each is handed
     * over with trySendBlocking, which holds the game's thread until the collector has room, so none is lost.
     */
    override val events: Flow<GameEvent> = callbackFlow {
        thread(name = "game", isDaemon = true) { play { event -> trySendBlocking(event) } }
        awaitClose()  // the game's thread can't be stopped: it ends with the app
    }

    override fun act(action: GameAction, digit: Int?, position: Position?) {
        val kwargs = listOfNotNull(
            digit?.let { Kwarg("digit", it) },
            position?.let { Kwarg("row", it.row) },
            position?.let { Kwarg("col", it.col) },
        )
        ui?.callAttr("act", action.gameName, *kwargs.toTypedArray())
    }

    override fun answer(yes: Boolean) {
        ui?.callAttr("answer", yes)
    }

    // Private functions

    /**
     * Start Python (slow the first time, as it unpacks), set up the standard board, then play until the game is over
     */
    private fun play(onEvent: (GameEvent) -> Unit) {
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(application))
            }
            val python = Python.getInstance()
            val board = python.getModule("game.puzzles.board_3x3").callAttr("Board3x3")
            val gameUi = python.getModule("ui.android.android_ui").callAttr("AndroidUI", PythonScreen(onEvent))
            val puzzle = python.getModule("game.puzzle").callAttr("Puzzle", board, gameUi)
            onEvent(GameEvent.Started(BoardSize(board["v_cells"]!!.toInt(), board["h_cells"]!!.toInt())))
            ui = gameUi
            gameUi.callAttr("play", puzzle)
        } catch (error: PyException) {
            onEvent(GameEvent.StatusChanged(GameMessage("The game stopped: ${error.message}", MessageKind.WARNING)))
        }
    }
}
