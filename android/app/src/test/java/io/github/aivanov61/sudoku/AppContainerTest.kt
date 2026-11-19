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

import io.github.aivanov61.sudoku.game.FakeGame
import io.github.aivanov61.sudoku.game.GameEvent
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotSame
import org.junit.Assert.assertSame
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class AppContainerTest {
    private val games = mutableListOf<FakeGame>()  // every game the container made, in order
    private val layouts = mutableListOf<String>()  // the layout of each game the container made, in order

    @Test
    fun noGameIsMadeUntilOneIsAskedFor() = runTest {
        container()
        assertEquals(0, games.size)
    }

    @Test
    fun theSameRepositoryIsHandedOutWhileTheGameIsOn() = runTest {
        val container = container()
        assertSame(container.gameRepository(LAYOUT), container.gameRepository(LAYOUT))
        assertEquals(listOf(LAYOUT), layouts)
    }

    @Test
    fun aNewGameIsMadeForAnotherLayout() = runTest {
        val container = container()
        val first = container.gameRepository(LAYOUT)
        assertNotSame(first, container.gameRepository("Another layout"))
        assertEquals(listOf(LAYOUT, "Another layout"), layouts)
    }

    @Test
    fun aNewGameIsHandedOutOnceTheGameIsOver() = runTest {
        val container = container()
        val first = container.gameRepository(LAYOUT)
        games.single().report(GameEvent.Over)
        runCurrent()  // let the repository take in the event
        assertNotSame(first, container.gameRepository(LAYOUT))
        assertEquals(listOf(LAYOUT, LAYOUT), layouts)
    }

    // Private functions

    /** A container that makes fake games, noting each one's layout, its work living as long as the test */
    private fun TestScope.container() = DefaultAppContainer(
        newGame = { layout -> FakeGame().also { games += it; layouts += layout } },
        newLayoutRepository = { error("not used in these tests") },
        newCopyrightRepository = { error("not used in these tests") },
        applicationScope = backgroundScope,
    )

    private companion object {
        /** Any name will do: the container only passes it on to newGame, and compares it with the last one */
        const val LAYOUT = "A layout"
    }
}
