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
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Edge
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameEvent
import io.github.aivanov61.sudoku.game.GameMessage
import io.github.aivanov61.sudoku.game.MessageKind
import io.github.aivanov61.sudoku.game.Position
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SudokuUiStateTest {
    private val start = SudokuUiState()

    // Events

    @Test
    fun startingGivesTheBoardItsSize() {
        assertEquals(BoardSize(9, 9), start.after(GameEvent.Started(BoardSize(9, 9))).size)
    }

    @Test
    fun aChangedCellReplacesWhatWasShownBefore() {
        val position = Position(4, 4)
        val state = start.after(GameEvent.CellChanged(position, EMPTY)).after(GameEvent.CellChanged(position, GIVEN_5))
        assertEquals(mapOf(position to GIVEN_5), state.cells)
    }

    @Test
    fun selectingMovesTheSelection() {
        assertEquals(Position(2, 7), start.after(GameEvent.Selected(Position(2, 7))).selected)
    }

    @Test
    fun aStatusReplacesTheOneBefore() {
        val message = GameMessage("Well done", MessageKind.SUCCESS)
        assertEquals(message, start.after(GameEvent.StatusChanged(message)).status)
    }

    @Test
    fun aQuestionIsAskedUntilAnswered() {
        val asked = start.after(GameEvent.Asked("Really quit?"))
        assertEquals("Really quit?", asked.question)
        assertNull(asked.answered().question)
    }

    @Test
    fun aNewModeComesWithWhatItOffers() {
        val state = start.after(GameEvent.ModeChanged("SETUP", setOf(GameAction.PLAY, GameAction.VALUE)))
        assertEquals("SETUP", state.mode)
        assertEquals(setOf(GameAction.PLAY, GameAction.VALUE), state.offered)
    }

    @Test
    fun theGameCanBeOver() {
        assertTrue(start.after(GameEvent.Over).isOver)
    }

    // Switching modes

    @Test
    fun setupSwitchesToPlay() {
        assertEquals(GameAction.PLAY, start.after(GameEvent.ModeChanged("SETUP", setOf(GameAction.PLAY))).modeSwitch)
    }

    @Test
    fun playSwitchesBackToSetup() {
        assertEquals(GameAction.INIT, start.after(GameEvent.ModeChanged("PLAY", setOf(GameAction.INIT))).modeSwitch)
    }

    private companion object {
        val EMPTY = CellState(null, CellKind.TYPED, false, 0, (1..9).toSet(), setOf(Edge.TOP))
        val GIVEN_5 = CellState(5, CellKind.INITIAL, false, 0, emptySet(), setOf(Edge.TOP))
    }
}
