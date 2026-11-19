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
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
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

    @Test
    fun itHasEndedAfter5000ms() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModel()
        advanceTimeBy(5_000.milliseconds)
        runCurrent()
        assertTrue(viewModel.uiState.value.hasEnded)
    }

    @Test
    fun itHasNotEndedAt4999ms() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModelAdvancedTo4999ms()
        assertFalse(viewModel.uiState.value.hasEnded)
    }

    @Test
    fun aTapEndsItAtOnce() = runTest(mainDispatcherRule.dispatcher) {
        val viewModel = viewModelAdvancedTo4999ms()
        viewModel.onTap()
        runCurrent() // nothing else due at 4,999ms could have ended it
        assertTrue(viewModel.uiState.value.hasEnded)
    }

    // Private functions

    /** A view model whose fake repository gives it the notice */
    private fun viewModel(notice: String = "the notice") = SplashViewModel(FakeCopyrightRepository(notice))

    /** A view model advanced to 4.999ms with all events drained */
    private fun TestScope.viewModelAdvancedTo4999ms(): SplashViewModel {
        val viewModel = viewModel()
        advanceTimeBy(4_999.milliseconds)
        runCurrent() // Drain any pending events at this time
        return viewModel
    }
}
