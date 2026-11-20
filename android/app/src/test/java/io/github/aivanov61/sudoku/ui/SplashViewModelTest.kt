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
import io.github.aivanov61.sudoku.data.FakeCopyrightRepository
import io.github.aivanov61.sudoku.data.FakeLayoutRepository
import io.github.aivanov61.sudoku.data.FakeSavedGameRepository
import io.github.aivanov61.sudoku.data.Layout
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test
import kotlin.time.Duration.Companion.milliseconds

@OptIn(ExperimentalCoroutinesApi::class)
class SplashViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun theNoticeComesFromTheRepository() = runTest(mainDispatcherRule.dispatcher) {
        assertEquals("the notice", viewModel().uiState.value.notice)
    }

    // When the splash ends

    @Test
    fun itEndsAfter5000ms() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        advanceTimeBy(5_000.milliseconds)
        runCurrent()
        assertEquals(STANDARD, viewModel.uiState.value.next.gameLayout)
    }

    @Test
    fun itHasNotEndedAt4999ms() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModelAdvancedTo4999ms()
        assertNull(viewModel.uiState.value.next)
    }

    @Test
    fun aTapEndsItAtOnce() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModelAdvancedTo4999ms()
        viewModel.onTap()
        runCurrent() // nothing else due at 4,999ms could have ended it
        assertEquals(STANDARD, viewModel.uiState.value.next.gameLayout)
    }

    @Test
    fun aTapWaitsForTheLayouts() = runTest(mainDispatcherRule.dispatcher) {
        val layouts = FakeLayoutRepository(listOf(layout(STANDARD)), held = true)
        val viewModel = viewModel(layouts)
        viewModel.onTap()
        assertNull(viewModel.uiState.value.next)
        layouts.release()
        assertEquals(STANDARD, viewModel.uiState.value.next.gameLayout)
    }

    // What follows the splash (Route.toStart, tested in KeysTest, works out which)

    @Test
    fun severalLayoutsGoToThePicker() = runTest(mainDispatcherRule.dispatcher) {
        assertEquals(Route.LayoutPicker, nextAfterTap(layout(STANDARD), layout(ANOTHER)))
    }

    @Test
    fun theSavedGamesLayoutIsPlayed() = runTest(mainDispatcherRule.dispatcher) {
        assertEquals(ANOTHER, nextAfterTap(layout(STANDARD), layout(ANOTHER), saved = ANOTHER).gameLayout)
    }

    // Private functions

    /** A view model whose fake repositories give it the notice, the layouts and the saved game's layout ([saved]) */
    private fun viewModel(
        layouts: FakeLayoutRepository = FakeLayoutRepository(listOf(layout(STANDARD))),
        saved: String? = null,
    ) = SplashViewModel(FakeCopyrightRepository("the notice"), layouts, FakeSavedGameRepository(saved))

    /** A view model advanced to 4.999ms with all events drained */
    private fun TestScope.viewModelAdvancedTo4999ms(): SplashViewModel {
        val viewModel = viewModel()
        advanceTimeBy(4_999.milliseconds)
        runCurrent() // Drain any pending events at this time
        return viewModel
    }

    /** The route that follows the splash over the layouts and the saved game's layout, once it is tapped */
    private fun nextAfterTap(vararg layouts: Layout, saved: String? = null): Route? {
        val viewModel = viewModel(FakeLayoutRepository(layouts.toList()), saved)
        viewModel.onTap()
        return viewModel.uiState.value.next
    }

    /** A layout with the name, which can be picked unless [canPick] says otherwise */
    private fun layout(name: String, canPick: Boolean = true) = Layout(name, label = name, canPick)

    private companion object {
        const val STANDARD = "Standard 9x9"
        const val ANOTHER = "Another"
    }
}
