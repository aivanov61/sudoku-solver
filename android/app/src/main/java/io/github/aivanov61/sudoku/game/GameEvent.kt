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

/** What the game reports, as it happens (see Game.start()) */
sealed interface GameEvent {
    /** The game has started on a board of this size; its cells follow */
    data class Started(val size: BoardSize) : GameEvent

    /** The cell at the position is now as given */
    data class CellChanged(val position: Position, val cell: CellState) : GameEvent

    /** The cell at the position is selected: the one values go into */
    data class Selected(val position: Position) : GameEvent

    /** The status line now shows the message */
    data class StatusChanged(val message: GameMessage) : GameEvent

    /** The game asks a yes/no question, and waits for Game.answer() */
    data class Asked(val question: String) : GameEvent

    /** The game is now in the mode (its name for the player), which offers these actions */
    data class ModeChanged(val mode: String, val offered: Set<GameAction>) : GameEvent

    /** The game is over */
    data object Over : GameEvent
}

/** A cell's place on the board, counted from 0 at the top left */
data class Position(val row: Int, val col: Int)

data class BoardSize(val rows: Int, val cols: Int)

/**
 * A cell as the game shows it: its value (null for none), how the value got there, whether it is in conflict,
 * the guess depth it was entered at (0 for none), the possible values it shows, and which of its sides are block edges
 */
data class CellState(
    val value: Int?,
    val kind: CellKind,
    val conflicted: Boolean,
    val depth: Int,
    val possible: Set<Int>,
    val edges: Set<Edge>,
)

data class GameMessage(val text: String, val kind: MessageKind) {
    companion object {
        val NONE = GameMessage("", MessageKind.NONE)
    }
}
