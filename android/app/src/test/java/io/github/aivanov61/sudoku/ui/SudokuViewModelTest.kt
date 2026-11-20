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
import io.github.aivanov61.sudoku.data.FakeLayoutRepository
import io.github.aivanov61.sudoku.data.GameRepository
import io.github.aivanov61.sudoku.data.Layout
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
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
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
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
    fun anAnswerGoesToTheGame() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onAnswer(false)
        assertEquals(listOf(false), game.answers)
    }

    // The app's lifecycle

    @Test
    fun theGameIsSavedWhenTheAppIsStopped() = runTest(mainDispatcherRule.dispatcher) {
        viewModel().onStopped()
        assertEquals(1, game.saves)
    }

    // New puzzle

    @Test
    fun newPuzzleCanStartOnlyOnceTheGameHasStarted() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        assertFalse(viewModel.uiState.value.canStartNew)  // it would restore the saved game, then delete it unasked
        game.report(GameEvent.Started(BoardSize(9, 9)))
        assertTrue(viewModel.uiState.value.canStartNew)
    }

    @Test
    fun newPuzzleCanStartOnceTheGameHasFailed() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        game.report(GameEvent.Failed("no such layout"))
        assertTrue(viewModel.uiState.value.canStartNew)
    }

    @Test
    fun newPuzzleAsksFirstWhenTheBoardHasValues() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = startedViewModel(cellWith(5))
        viewModel.onNewPuzzle()
        assertTrue(viewModel.uiState.value.askingNewPuzzle)
        assertEquals(emptyList<Act>(), game.acts)
    }

    @Test
    fun newPuzzleOnAnEmptyBoardEndsTheGameWithoutAsking() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = startedViewModel(cellWith(null))
        viewModel.onNewPuzzle()
        assertFalse(viewModel.uiState.value.askingNewPuzzle)
        assertEquals(listOf(Act(GameAction.FORCE_QUIT)), game.acts)
    }

    @Test
    fun startingNewEndsTheGame() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = startedViewModel(cellWith(5))
        viewModel.onNewPuzzle()
        viewModel.onNewPuzzleAnswer(true)
        assertFalse(viewModel.uiState.value.askingNewPuzzle)
        assertEquals(listOf(Act(GameAction.FORCE_QUIT)), game.acts)
    }

    @Test
    fun cancelLeavesTheGameAsItWas() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = startedViewModel(cellWith(5))
        viewModel.onNewPuzzle()
        viewModel.onNewPuzzleAnswer(false)
        assertFalse(viewModel.uiState.value.askingNewPuzzle)
        assertEquals(emptyList<Act>(), game.acts)
        assertNull(viewModel.uiState.value.next)
    }

    @Test
    fun theNewPuzzleFollowsOnceTheGameIsOver() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = startedViewModel(cellWith(null))
        viewModel.onNewPuzzle()
        assertNull(viewModel.uiState.value.next)  // the game hasn't deleted its saved game yet
        game.report(GameEvent.Over)
        assertEquals(STANDARD, viewModel.uiState.value.next.gameLayout)
    }

    @Test
    fun withSeveralLayoutsTheNewPuzzleIsPicked() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = startedViewModel(cellWith(null), layouts = listOf(layout(STANDARD), layout(ANOTHER)))
        viewModel.onNewPuzzle()
        game.report(GameEvent.Over)
        assertEquals(Route.LayoutPicker, viewModel.uiState.value.next)
    }

    @Test
    fun aFailedGameGoesStraightToTheNewPuzzle() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        game.report(GameEvent.Failed("no such layout"))
        viewModel.onNewPuzzle()
        assertEquals(emptyList<Act>(), game.acts)  // it has already ended
        assertEquals(STANDARD, viewModel.uiState.value.next.gameLayout)
    }

    // Private functions

    /**
     * A view model over a repository of the fake game, and over the layouts, everything running at once on the test's
     * dispatcher
     */
    private fun TestScope.viewModel(layouts: List<Layout> = listOf(layout(STANDARD))): SudokuViewModel {
        val repository = GameRepository(game, backgroundScope, mainDispatcherRule.dispatcher)
        val viewModel = SudokuViewModel(repository, FakeLayoutRepository(layouts))
        backgroundScope.launch { viewModel.uiState.collect() }  // for as long as the test runs, as the screen would
        return viewModel
    }

    /** A view model whose game has started, on a board of the one cell given */
    private fun TestScope.startedViewModel(
        cell: CellState,
        layouts: List<Layout> = listOf(layout(STANDARD)),
    ): SudokuViewModel {
        val viewModel = viewModel(layouts)
        game.report(GameEvent.Started(BoardSize(1, 1)), GameEvent.CellChanged(Position(0, 0), cell))
        return viewModel
    }

    /** A cell with the value, or none */
    private fun cellWith(value: Int?) = CellState(value, CellKind.TYPED, false, 0, emptySet(), emptySet())

    /** A layout with the name, which can be picked */
    private fun layout(name: String) = Layout(name, label = name, canPick = true)

    private companion object {
        const val STANDARD = "Standard 9x9"
        const val ANOTHER = "Another"
    }
}
