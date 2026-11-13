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

package io.github.aivanov61.sudoku.game

import org.junit.Assert.assertEquals
import org.junit.Test

class PythonScreenTest {
    private val events = mutableListOf<GameEvent>()
    private val screen = PythonScreen { events += it }

    // Cells

    @Test
    fun anEmptyCellHasNoValueAndItsPossibleValues() {
        screen.showCell(0, 1, 0, "", false, 0, intArrayOf(1, 2, 3), arrayOf("top"))
        val cell = CellState(null, CellKind.TYPED, false, 0, setOf(1, 2, 3), setOf(Edge.TOP))
        assertEquals(listOf(GameEvent.CellChanged(Position(0, 1), cell)), events)
    }

    @Test
    fun aFilledCellHasItsValueKindConflictDepthAndEdges() {
        screen.showCell(8, 8, 3, "guess", true, 2, intArrayOf(), arrayOf("right", "bottom"))
        val cell = CellState(3, CellKind.GUESS, true, 2, emptySet(), setOf(Edge.RIGHT, Edge.BOTTOM))
        assertEquals(listOf(GameEvent.CellChanged(Position(8, 8), cell)), events)
    }

    @Test
    fun aKindTheAppDoesNotKnowIsShownAsTyped() {
        screen.showCell(0, 0, 4, "pencilled", false, 0, intArrayOf(), arrayOf())
        val cell = CellState(4, CellKind.TYPED, false, 0, emptySet(), emptySet())
        assertEquals(listOf(GameEvent.CellChanged(Position(0, 0), cell)), events)
    }

    // Everything else

    @Test
    fun theSelectedCellIsReportedByPosition() {
        screen.showSelected(2, 7)
        assertEquals(listOf(GameEvent.Selected(Position(2, 7))), events)
    }

    @Test
    fun aStatusComesWithItsKind() {
        screen.showStatus("Resolve the conflicts before playing. ", "warning")
        val warning = GameMessage("Resolve the conflicts before playing. ", MessageKind.WARNING)
        assertEquals(listOf(GameEvent.StatusChanged(warning)), events)
    }

    @Test
    fun aMessageKindTheAppDoesNotKnowHasNoKind() {
        screen.showStatus("Something new", "celebration")
        assertEquals(listOf(GameEvent.StatusChanged(GameMessage("Something new", MessageKind.NONE))), events)
    }

    @Test
    fun aBlankStatusHasNoKind() {
        screen.showStatus("", "")
        assertEquals(listOf(GameEvent.StatusChanged(GameMessage.NONE)), events)
    }

    @Test
    fun aQuestionIsAsked() {
        screen.askConfirm("Really quit?")
        assertEquals(listOf(GameEvent.Asked("Really quit?")), events)
    }

    @Test
    fun aModeKeepsOnlyTheActionsTheAppKnows() {
        screen.modeChanged("SETUP", arrayOf("play", "value", "up", "select"))
        val known = setOf(GameAction.PLAY, GameAction.VALUE, GameAction.SELECT)
        assertEquals(listOf(GameEvent.ModeChanged("SETUP", known)), events)
    }

    @Test
    fun anAnsweredQuestionIsOver() {
        screen.questionAnswered()
        assertEquals(listOf(GameEvent.Answered), events)
    }

    @Test
    fun theGameCanBeOver() {
        screen.gameOver()
        assertEquals(listOf(GameEvent.Over), events)
    }
}
