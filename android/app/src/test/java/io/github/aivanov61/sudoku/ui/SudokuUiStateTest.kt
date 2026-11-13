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

import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.game.GameAction
import org.junit.Assert.assertEquals
import org.junit.Test

class SudokuUiStateTest {
    // Switching modes

    @Test
    fun setupSwitchesToPlay() {
        assertEquals(GameAction.PLAY, SudokuUiState(GameState(offered = setOf(GameAction.PLAY))).modeSwitch)
    }

    @Test
    fun playSwitchesBackToSetup() {
        assertEquals(GameAction.INIT, SudokuUiState(GameState(offered = setOf(GameAction.INIT))).modeSwitch)
    }
}
