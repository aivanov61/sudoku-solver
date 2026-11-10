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

/**
 * The screen as the Python game sees it: ui/android/screen.py's Screen, which AndroidUI calls on the game's thread
 * by these names, with plain values.  Each call becomes a typed GameEvent.
 */
class PythonScreen(private val onEvent: (GameEvent) -> Unit) {
    fun showCell(row: Int, col: Int, value: Int, kind: String, conflicted: Boolean, depth: Int, possible: IntArray, edges: Array<String>) {
        val cell = CellState(
            value = value.takeIf { it > 0 },
            kind = fromGameName<CellKind>(kind) ?: CellKind.TYPED,
            conflicted = conflicted,
            depth = depth,
            possible = possible.toSet(),
            edges = edges.mapNotNull { fromGameName<Edge>(it) }.toSet(),
        )
        onEvent(GameEvent.CellChanged(Position(row, col), cell))
    }

    fun showSelected(row: Int, col: Int) = onEvent(GameEvent.Selected(Position(row, col)))

    fun showStatus(text: String, kind: String) =
        onEvent(GameEvent.StatusChanged(GameMessage(text, fromGameName<MessageKind>(kind) ?: MessageKind.NONE)))

    fun askConfirm(question: String) = onEvent(GameEvent.Asked(question))

    fun modeChanged(mode: String, actions: Array<String>) =
        onEvent(GameEvent.ModeChanged(mode, actions.mapNotNull { fromGameName<GameAction>(it) }.toSet()))

    fun gameOver() = onEvent(GameEvent.Over)
}
