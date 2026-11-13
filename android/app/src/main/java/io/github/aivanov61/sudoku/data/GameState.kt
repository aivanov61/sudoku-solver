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

import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameEvent
import io.github.aivanov61.sudoku.game.GameMessage
import io.github.aivanov61.sudoku.game.Position

/** The game as it last reported itself: never more than the game said, as the game is the source of truth */
data class GameState(
    val size: BoardSize? = null,  // null until the game has started
    val cells: Map<Position, CellState> = emptyMap(),
    val selected: Position = Position(0, 0),
    val message: GameMessage = GameMessage.NONE,
    val question: String? = null,  // the question asked, until it is answered
    val mode: String = "",
    val offered: Set<GameAction> = emptySet(),
    val isOver: Boolean = false,
) {
    /** The state once the event has happened */
    fun after(event: GameEvent): GameState = when (event) {
        is GameEvent.Started -> copy(size = event.size)
        is GameEvent.CellChanged -> copy(cells = cells + (event.position to event.cell))
        is GameEvent.Selected -> copy(selected = event.position)
        is GameEvent.StatusChanged -> copy(message = event.message)
        is GameEvent.Asked -> copy(question = event.question)
        GameEvent.Answered -> copy(question = null)
        is GameEvent.ModeChanged -> copy(mode = event.mode, offered = event.offered)
        GameEvent.Over -> copy(isOver = true)
    }
}
