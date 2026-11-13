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

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.receiveAsFlow

/**
 * A stand-in game for tests.  Despite its name, it is NOT a fake: it is only a stub and a spy.  It is named
 * FakeGame anyway, as Android's testing guides call such stand-ins fakes, and that is the name developers look for.
 *
 * - Stub: it reports exactly the events a test gives it (report()), and nothing else.
 * - Spy: it records the actions and answers it is asked for (acts, answers), and does nothing with them.
 *
 * It has no game logic: an action changes nothing and reports nothing, so a test that needs the game's response
 * must report it itself.  Keep it that way: don't make it work out events, moves or rules.  A test that needs real
 * game behavior belongs with the Python game's own tests, or in an instrumented test that runs Python.
 */
class FakeGame : Game {
    val acts = mutableListOf<Act>()
    val answers = mutableListOf<Boolean>()
    private val reported = Channel<GameEvent>(Channel.UNLIMITED)  // kept until collected, so none is lost

    override val events: Flow<GameEvent> = reported.receiveAsFlow()

    override fun act(action: GameAction, digit: Int?, position: Position?) {
        acts += Act(action, digit, position)
    }

    override fun answer(yes: Boolean) {
        answers += yes
    }

    fun report(vararg events: GameEvent) = events.forEach { reported.trySend(it) }

    /** One action the game was asked to carry out */
    data class Act(val action: GameAction, val digit: Int? = null, val position: Position? = null)
}
