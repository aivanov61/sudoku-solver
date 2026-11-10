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

package io.github.aivanov61.sudoku.ui

import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.Game
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameEvent
import io.github.aivanov61.sudoku.game.Position
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class SudokuViewModelTest {
    private val game = FakeGame()
    private val viewModel = SudokuViewModel(game)

    // The game's events

    @Test
    fun theGameIsStartedOnce() {
        assertEquals(1, game.starts)
    }

    @Test
    fun whatTheGameReportsBecomesTheState() {
        game.report(GameEvent.Started(BoardSize(9, 9)))
        game.report(GameEvent.Selected(Position(3, 1)))
        assertEquals(BoardSize(9, 9), viewModel.uiState.value.size)
        assertEquals(Position(3, 1), viewModel.uiState.value.selected)
    }

    // The player's intents

    @Test
    fun tappingACellSelectsIt() {
        viewModel.onCellTapped(Position(2, 7))
        assertEquals(listOf(Act(GameAction.SELECT, position = Position(2, 7))), game.acts)
    }

    @Test
    fun aDigitIsEnteredAsAValue() {
        viewModel.onDigit(5)
        assertEquals(listOf(Act(GameAction.VALUE, digit = 5)), game.acts)
    }

    @Test
    fun clearDeletesTheValue() {
        viewModel.onClear()
        assertEquals(listOf(Act(GameAction.DEL)), game.acts)
    }

    @Test
    fun switchingModesUsesTheSwitchTheModeOffers() {
        game.report(GameEvent.ModeChanged("PLAY", setOf(GameAction.INIT)))
        viewModel.onSwitchMode()
        assertEquals(listOf(Act(GameAction.INIT)), game.acts)
    }

    @Test
    fun quitAsksTheGameToQuit() {
        viewModel.onQuit()
        assertEquals(listOf(Act(GameAction.QUIT)), game.acts)
    }

    @Test
    fun anAnswerGoesToTheGameAndEndsTheQuestion() {
        game.report(GameEvent.Asked("Really quit?"))
        viewModel.onAnswer(false)
        assertEquals(listOf(false), game.answers)
        assertNull(viewModel.uiState.value.question)
    }

    // Private functions

    private data class Act(val action: GameAction, val digit: Int? = null, val position: Position? = null)

    /** A stand-in game that records what it is asked to do, and reports the events it is given */
    private class FakeGame : Game {
        var starts = 0
        val acts = mutableListOf<Act>()
        val answers = mutableListOf<Boolean>()
        private var onEvent: (GameEvent) -> Unit = {}

        override fun start(onEvent: (GameEvent) -> Unit) {
            starts++
            this.onEvent = onEvent
        }

        override fun act(action: GameAction, digit: Int?, position: Position?) {
            acts += Act(action, digit, position)
        }

        override fun answer(yes: Boolean) {
            answers += yes
        }

        fun report(event: GameEvent) = onEvent(event)
    }
}
