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
import io.github.aivanov61.sudoku.game.FakeGame
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameEvent
import io.github.aivanov61.sudoku.game.Position
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class GameRepositoryTest {
    private val game = FakeGame()

    @Test
    fun theStateIsWhatTheGameReported() = runTest {
        val repository = repository()
        game.report(GameEvent.Started(BoardSize(9, 9)), GameEvent.Selected(Position(3, 1)))
        runCurrent()  // let the repository's collecting coroutine take in the events
        assertEquals(BoardSize(9, 9), repository.state.value.size)
        assertEquals(Position(3, 1), repository.state.value.selected)
    }

    @Test
    fun anActionIsPassedOnToTheGame() = runTest {
        repository().act(GameAction.SELECT, position = Position(2, 7))
        assertEquals(listOf(FakeGame.Act(GameAction.SELECT, position = Position(2, 7))), game.acts)
    }

    @Test
    fun anActionIsPassedOnWithTheDefaultDispatcherToo() = runTest {
        GameRepository(game, backgroundScope).act(GameAction.DEL)  // on Dispatchers.IO, the real default
        assertEquals(listOf(FakeGame.Act(GameAction.DEL)), game.acts)
    }

    @Test
    fun anAnswerIsPassedOnToTheGame() = runTest {
        repository().answer(false)
        assertEquals(listOf(false), game.answers)
    }

    // Private functions

    /** A repository over the fake game, living as long as the test, with every coroutine run at once */
    private fun TestScope.repository() = GameRepository(game, backgroundScope, UnconfinedTestDispatcher(testScheduler))
}
