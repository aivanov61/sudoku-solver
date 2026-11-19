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
import io.github.aivanov61.sudoku.data.Layout
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class LayoutPickerViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun theLayoutsComeFromTheRepository() = runTest(mainDispatcherRule.dispatcher) {
        assertEquals(listOf(STANDARD, BROKEN), uiState(STANDARD, BROKEN).layouts)
    }

    @Test
    fun theLayoutsAreUnknownUntilRead() = runTest(mainDispatcherRule.dispatcher) {
        val state = LayoutPickerViewModel(FakeLayoutRepository(listOf(STANDARD), held = true)).uiState.value
        assertNull(state.layouts)
        assertFalse(state.noneCanBePicked)  // not said before it is known
    }

    @Test
    fun oneThatCanBePickedIsEnough() = runTest(mainDispatcherRule.dispatcher) {
        assertFalse(uiState(BROKEN, STANDARD).noneCanBePicked)
    }

    @Test
    fun noneCanBePickedWhenAllAreBroken() = runTest(mainDispatcherRule.dispatcher) {
        assertTrue(uiState(BROKEN).noneCanBePicked)
    }

    @Test
    fun noneCanBePickedWhenThereAreNone() = runTest(mainDispatcherRule.dispatcher) {
        assertTrue(uiState().noneCanBePicked)
    }

    // Private functions

    /** The picker's state over the layouts, once read */
    private fun uiState(vararg layouts: Layout) =
        LayoutPickerViewModel(FakeLayoutRepository(layouts.toList())).uiState.value

    private companion object {
        val STANDARD = Layout("Standard 9x9", "Standard 9x9", canPick = true)
        val BROKEN = Layout("Broken", "Broken (no blocks)", canPick = false)
    }
}
