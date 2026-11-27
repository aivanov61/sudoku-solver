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
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Conflict
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameMode
import io.github.aivanov61.sudoku.game.Position
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
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

    // The commands

    @Test
    fun aCommandTheModeOffersCanBeUsed() {
        assertTrue(SudokuUiState(GameState(offered = setOf(GameAction.UNDO))).offers(GameAction.UNDO))
    }

    @Test
    fun aCommandTheModeDoesntOfferCant() {
        assertFalse(SudokuUiState(GameState(offered = setOf(GameAction.UNDO))).offers(GameAction.REWIND))
    }

    // Guessing

    @Test
    fun guessOnInAModeThatOffersGuessesIsGuessing() {
        assertTrue(SudokuUiState(GameState(offered = setOf(GameAction.GUESS)), guessOn = true).guessing)
    }

    @Test
    fun guessOnInAModeWithoutGuessesIsNotGuessing() {
        assertFalse(SudokuUiState(GameState(offered = setOf(GameAction.VALUE)), guessOn = true).guessing)
    }

    @Test
    fun guessOffIsNotGuessing() {
        assertFalse(SudokuUiState(GameState(offered = setOf(GameAction.GUESS)), guessOn = false).guessing)
    }

    // What the pad enters

    @Test
    fun inSetupThePadEntersGivens() {
        assertEquals(CellKind.INITIAL, SudokuUiState(GameState(mode = GameMode.SETUP, offered = setOf(GameAction.VALUE))).entering)
    }

    @Test
    fun inPlayThePadEntersValues() {
        assertEquals(CellKind.TYPED, SudokuUiState(GameState(mode = GameMode.PLAY, offered = setOf(GameAction.GUESS))).entering)
    }

    @Test
    fun whileGuessingThePadEntersGuesses() {
        val state = SudokuUiState(GameState(mode = GameMode.PLAY, offered = setOf(GameAction.GUESS)), guessOn = true)
        assertEquals(CellKind.GUESS, state.entering)
    }

    // The digits left

    @Test
    fun onAnEmptyBoardADigitHasAPlaceInEachRow() {
        assertEquals(9, boardWith().left(5))
    }

    @Test
    fun aValueTakesOneOfItsDigitsPlaces() {
        assertEquals(8, boardWith(value(5)).left(5))
    }

    @Test
    fun aValueTakesNoneOfAnotherDigitsPlaces() {
        assertEquals(9, boardWith(value(3)).left(5))
    }

    @Test
    fun valuesOfEveryKindTakePlaces() {
        val values = CellKind.entries.map { kind -> value(5, kind) }
        assertEquals(9 - CellKind.entries.size, boardWith(*values.toTypedArray()).left(5))
    }

    @Test
    fun aValueInConflictTakesAPlace() {
        assertEquals(8, boardWith(value(5).copy(conflict = Conflict.CONFLICTING)).left(5))
    }

    @Test
    fun moreValuesThanPlacesLeaveNone() {
        val values = List(10) { value(5) }
        assertEquals(0, boardWith(*values.toTypedArray()).left(5))
    }

    @Test
    fun beforeTheGameHasStartedNoneAreLeft() {
        assertEquals(0, SudokuUiState().left(5))
    }

    // Private functions

    /** A started 9x9 game whose first cells, in reading order, are as given, and the rest empty */
    private fun boardWith(vararg cells: CellState): SudokuUiState {
        val positions = (0 until 9).flatMap { row -> (0 until 9).map { col -> Position(row, col) } }
        val all = positions.mapIndexed { index, position -> position to (cells.getOrNull(index) ?: value(null)) }
        return SudokuUiState(GameState(size = BoardSize(9, 9), cells = all.toMap()))
    }

    private fun value(digit: Int?, kind: CellKind = CellKind.TYPED): CellState =
        CellState(digit, kind, Conflict.NONE, 0, emptySet(), emptySet())
}
