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
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.channels.trySendBlocking
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlin.concurrent.thread

/**
 * The game written in Python (the repository's game/ and ui/android/), run through Chaquopy, on the board of the
 * [layout] named: AndroidUI.play() runs on the game's own thread, reporting through a PythonScreen, and takes the
 * player's actions from a queue.
 */
class PythonGame(private val application: Application, private val layout: String) : Game {
    @Volatile
    private var ui: PyObject? = null  // the game's AndroidUI, once Python has started

    /**
     * The game's reports, as a Flow: callbackFlow turns PythonScreen's calls into the flow's values.  Each is handed
     * over with trySendBlocking, which holds the game's thread until the collector has room, so none is lost.
     */
    override val events: Flow<GameEvent> = callbackFlow {
        thread(name = "game", isDaemon = true) {
            play { event -> trySendBlocking(event) }
            close()  // the game is over: end the flow, so its collector ends too
        }
        awaitClose()  // the game's thread can't be stopped from here: it ends when the game is over
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

    /** Set up the layout's board (starting Python, if the layouts haven't yet), then play until the game is over */
    private fun play(onEvent: (GameEvent) -> Unit) {
        try {
            val python = AppPython.of(application)
            val board = python.getModule("ui.android.catalog")["Catalog"]!!.callAttr("board", layout)
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
