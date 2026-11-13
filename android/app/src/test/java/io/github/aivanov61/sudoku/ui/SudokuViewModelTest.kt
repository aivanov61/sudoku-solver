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

import io.github.aivanov61.sudoku.MainDispatcherRule
import io.github.aivanov61.sudoku.data.GameRepository
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.FakeGame
import io.github.aivanov61.sudoku.game.FakeGame.Act
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameEvent
import io.github.aivanov61.sudoku.game.Position
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class SudokuViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val game = FakeGame()

    // The game's state

    @Test
    fun whatTheGameReportsBecomesTheScreensState() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        game.report(GameEvent.Started(BoardSize(9, 9)), GameEvent.Selected(Position(3, 1)))
        assertEquals(BoardSize(9, 9), viewModel.uiState.value.game.size)
        assertEquals(Position(3, 1), viewModel.uiState.value.game.selected)
    }

    // The player's intents

    @Test
    fun tappingACellSelectsIt() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onCellTapped(Position(2, 7))
        assertEquals(listOf(Act(GameAction.SELECT, position = Position(2, 7))), game.acts)
    }

    @Test
    fun aDigitIsEnteredAsAValue() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onDigit(5)
        assertEquals(listOf(Act(GameAction.VALUE, digit = 5)), game.acts)
    }

    @Test
    fun clearDeletesTheValue() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onClear()
        assertEquals(listOf(Act(GameAction.DEL)), game.acts)
    }

    @Test
    fun switchingModesUsesTheSwitchTheModeOffers() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        game.report(GameEvent.ModeChanged("PLAY", setOf(GameAction.INIT)))
        viewModel.onSwitchMode()
        assertEquals(listOf(Act(GameAction.INIT)), game.acts)
    }

    @Test
    fun quitAsksTheGameToQuit() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onQuit()
        assertEquals(listOf(Act(GameAction.QUIT)), game.acts)
    }

    @Test
    fun anAnswerGoesToTheGame() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onAnswer(false)
        assertEquals(listOf(false), game.answers)
    }

    // Private functions

    /** A view model over a repository of the fake game, everything running at once on the test's dispatcher */
    private fun TestScope.viewModel(): SudokuViewModel {
        val viewModel = SudokuViewModel(GameRepository(game, backgroundScope, mainDispatcherRule.dispatcher))
        backgroundScope.launch { viewModel.uiState.collect() }  // for as long as the test runs, as the screen would
        return viewModel
    }
}
