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

import io.github.aivanov61.sudoku.game.Position

/**
 * The screen's intents, for the screen's tests: a spy, as FakeGame is for the game.  It records each intent called,
 * as it would read in the code (e.g. "onDigit(5)"), in order, and does nothing with it.
 */
class RecordingIntents : SudokuIntents {
    val calls = mutableListOf<String>()

    override fun onCellTapped(position: Position) {
        calls += "onCellTapped(${position.row}, ${position.col})"
    }

    override fun onDigit(digit: Int) {
        calls += "onDigit($digit)"
    }

    override fun onErase() {
        calls += "onErase()"
    }

    override fun onUndo() {
        calls += "onUndo()"
    }

    override fun onRewind() {
        calls += "onRewind()"
    }

    override fun onGuessToggled() {
        calls += "onGuessToggled()"
    }

    override fun onSwitchMode() {
        calls += "onSwitchMode()"
    }

    override fun onAnswer(yes: Boolean) {
        calls += "onAnswer($yes)"
    }

    override fun onInformed() {
        calls += "onInformed()"
    }

    override fun onNewPuzzle() {
        calls += "onNewPuzzle()"
    }

    override fun onNewPuzzleAnswer(yes: Boolean) {
        calls += "onNewPuzzleAnswer($yes)"
    }
}
