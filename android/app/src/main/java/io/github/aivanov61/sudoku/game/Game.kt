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

import kotlinx.coroutines.flow.Flow

/**
 * The game, as the app sees it: the data source behind GameRepository.  It reports what happens as GameEvents,
 * and carries out the player's actions and answers.  PythonGame is the real one.
 */
interface Game {
    /** What the game reports, as it happens; collecting it starts the game, so it is collected once */
    val events: Flow<GameEvent>

    /** Carry out the action, with its digit (values) or the position of the cell it points at (selecting) */
    fun act(action: GameAction, digit: Int? = null, position: Position? = null)

    /** Answer the question the game asked (GameEvent.Asked) */
    fun answer(yes: Boolean)
}
