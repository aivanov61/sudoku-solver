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

import androidx.compose.ui.test.assertIsEnabled
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.assertIsNotSelected
import androidx.compose.ui.test.assertIsOff
import androidx.compose.ui.test.assertIsOn
import androidx.compose.ui.test.assertIsSelected
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import io.github.aivanov61.sudoku.data.GameDialog
import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameMode
import io.github.aivanov61.sudoku.game.GameMessage
import io.github.aivanov61.sudoku.game.MessageKind
import io.github.aivanov61.sudoku.game.Position
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

/**
 * Compose UI tests of the game screen, run on the device: each shows the screen with a state it makes, without a
 * view model or the game, and checks what the player sees and which intents a tap calls
 */
class SudokuScreenTest {
    @get:Rule
    val composeRule = createComposeRule()

    private val intents = RecordingIntents()

    // The board and the pad

    @Test
    fun aDigitOnThePadIsEntered() {
        show(startedGame())
        composeRule.onNodeWithText("5").performClick()
        assertEquals(listOf("onDigit(5)"), intents.calls)
    }

    @Test
    fun aTappedCellIsSelected() {
        show(startedGame())
        composeRule.onNodeWithContentDescription("Row 3, column 8").performClick()
        assertEquals(listOf("onCellTapped(2, 7)"), intents.calls)
    }

    // The mode switch

    @Test
    fun theModeSwitchShowsTheMode() {
        show(startedGame().copy(mode = GameMode.PLAY))
        composeRule.onNodeWithText("Play").assertIsSelected()
        composeRule.onNodeWithText("Setup").assertIsNotSelected()
    }

    @Test
    fun theOtherModeSwitchesToIt() {
        show(startedGame().copy(mode = GameMode.SETUP))
        composeRule.onNodeWithText("Play").performClick()
        assertEquals(listOf("onSwitchMode()"), intents.calls)
    }

    @Test
    fun theModeInUseStaysAsItIs() {
        show(startedGame().copy(mode = GameMode.SETUP))
        composeRule.onNodeWithText("Setup").performClick()
        assertEquals(emptyList<String>(), intents.calls)
    }

    // The commands

    @Test
    fun undoUndoesTheLastMove() {
        show(startedGame().copy(offered = setOf(GameAction.UNDO)))
        composeRule.onNodeWithText("Undo").performClick()
        assertEquals(listOf("onUndo()"), intents.calls)
    }

    @Test
    fun rewindGoesBackToTheLastGuess() {
        show(startedGame().copy(offered = setOf(GameAction.REWIND)))
        composeRule.onNodeWithText("Rewind").performClick()
        assertEquals(listOf("onRewind()"), intents.calls)
    }

    @Test
    fun eraseDeletesTheValue() {
        show(startedGame().copy(offered = setOf(GameAction.DEL)))
        composeRule.onNodeWithText("Erase").performClick()
        assertEquals(listOf("onErase()"), intents.calls)
    }

    @Test
    fun aCommandTheModeDoesntOfferIsDisabled() {
        show(startedGame().copy(offered = setOf(GameAction.DEL)))
        composeRule.onNodeWithText("Undo").assertIsNotEnabled()
        composeRule.onNodeWithText("Rewind").assertIsNotEnabled()
        composeRule.onNodeWithText("Erase").assertIsEnabled()
    }

    // The Guess toggle

    @Test
    fun theGuessToggleShowsWhetherGuessing() {
        show(startedGame().copy(offered = setOf(GameAction.GUESS)), guessOn = true)
        composeRule.onNodeWithText("Guess").assertIsOn()
    }

    @Test
    fun tappingGuessTogglesIt() {
        show(startedGame().copy(offered = setOf(GameAction.GUESS)))
        composeRule.onNodeWithText("Guess").assertIsOff().performClick()
        assertEquals(listOf("onGuessToggled()"), intents.calls)
    }

    @Test
    fun withoutGuessesTheToggleIsOffAndDisabled() {
        show(startedGame().copy(offered = setOf(GameAction.VALUE)), guessOn = true)
        composeRule.onNodeWithText("Guess").assertIsOff().assertIsNotEnabled()
    }

    // The dialogs

    @Test
    fun yesAnswersTheGamesQuestion() {
        show(startedGame().copy(dialogs = listOf(GameDialog.Confirm("Really rewind?"))))
        composeRule.onNodeWithText("Yes").performClick()
        assertEquals(listOf("onAnswer(true)"), intents.calls)
    }

    @Test
    fun noAnswersTheGamesQuestion() {
        show(startedGame().copy(dialogs = listOf(GameDialog.Confirm("Really rewind?"))))
        composeRule.onNodeWithText("No").performClick()
        assertEquals(listOf("onAnswer(false)"), intents.calls)
    }

    @Test
    fun okSaysTheGamesMessageWasSeen() {
        val warning = GameMessage("Nothing to undo.", MessageKind.WARNING)
        show(startedGame().copy(dialogs = listOf(GameDialog.Inform(warning))))
        composeRule.onNodeWithText("OK").performClick()
        assertEquals(listOf("onInformed()"), intents.calls)
    }

    @Test
    fun startNewAnswersNewPuzzlesQuestion() {
        show(startedGame(), askingNewPuzzle = true)
        composeRule.onNodeWithText("Start new").performClick()
        assertEquals(listOf("onNewPuzzleAnswer(true)"), intents.calls)
    }

    // Private functions

    private fun show(game: GameState, askingNewPuzzle: Boolean = false, guessOn: Boolean = false) {
        val state = SudokuUiState(game, askingNewPuzzle, guessOn = guessOn)
        composeRule.setContent { SudokuScreen(state, intents) }
    }

    /**
     * A started game on an empty 9x9 board whose cells show no small digits, so the only digits on the screen are
     * the pad's
     */
    private fun startedGame(): GameState {
        val empty = CellState(null, CellKind.TYPED, false, 0, emptySet(), emptySet())
        val positions = (0 until 9).flatMap { row -> (0 until 9).map { col -> Position(row, col) } }
        return GameState(size = BoardSize(9, 9), cells = positions.associateWith { empty })
    }
}
