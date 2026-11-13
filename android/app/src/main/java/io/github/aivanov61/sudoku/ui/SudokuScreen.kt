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

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Edge
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameMessage
import io.github.aivanov61.sudoku.game.MessageKind
import io.github.aivanov61.sudoku.game.Position

/**
 * The game's screen, a first try: the mode, the board, the status line, a digit pad and a few commands, and the
 * game's yes/no questions as dialogs.  It only shows the state, and passes what the player does on to the intents.
 */
@Composable
fun SudokuScreen(state: SudokuUiState, intents: SudokuIntents) {
    Column(
        modifier = Modifier.fillMaxSize().safeDrawingPadding().padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        val game = state.game
        Text(game.mode, style = MaterialTheme.typography.titleMedium)
        val size = game.size
        if (size == null) {
            Text("Starting the game…")
        } else {
            Board(size, game.cells, game.selected, intents::onCellTapped)
            StatusLine(game.message)
            DigitPad(intents::onDigit)
            Commands(state.modeSwitch, intents)
        }
    }
    state.game.question?.let { question -> Confirm(question, intents::onAnswer) }
}

// Private functions

@Composable
private fun Board(size: BoardSize, cells: Map<Position, CellState>, selected: Position, onTap: (Position) -> Unit) {
    Column(Modifier.fillMaxWidth().aspectRatio(size.cols.toFloat() / size.rows)) {
        for (row in 0 until size.rows) {
            Row(Modifier.weight(1f)) {
                for (col in 0 until size.cols) {
                    val position = Position(row, col)
                    val modifier = Modifier.weight(1f).fillMaxSize().clickable { onTap(position) }
                    Cell(cells[position], position == selected, modifier)
                }
            }
        }
    }
}

@Composable
private fun Cell(cell: CellState?, isSelected: Boolean, modifier: Modifier) {
    Box(
        modifier = modifier
            .background(cellBackground(cell, isSelected))
            .drawBehind { drawEdges(cell?.edges.orEmpty()) },
        contentAlignment = Alignment.Center,
    ) {
        val value = cell?.value
        when {
            cell == null -> {}
            value != null -> Text(
                value.toString(),
                fontSize = 22.sp,
                fontWeight = if (cell.kind == CellKind.INITIAL) FontWeight.Bold else FontWeight.Normal,
                color = valueColor(cell),
            )
            else -> PossibleValues(cell.possible)
        }
    }
}

private fun cellBackground(cell: CellState?, isSelected: Boolean): Color = when {
    isSelected -> Palette.SELECTED
    cell != null && cell.depth > 0 -> Palette.GUESS_SHADE.copy(alpha = minOf(0.1f * cell.depth, 0.5f))
    else -> Color.White
}

/** Thin lines around every cell, thick ones on the sides that are block edges */
private fun DrawScope.drawEdges(edges: Set<Edge>) {
    val (w, h) = size.width to size.height
    fun width(edge: Edge) = (if (edge in edges) 2.dp else 0.5.dp).toPx()
    drawLine(Color.Black, Offset(0f, 0f), Offset(w, 0f), width(Edge.TOP))
    drawLine(Color.Black, Offset(0f, h), Offset(w, h), width(Edge.BOTTOM))
    drawLine(Color.Black, Offset(0f, 0f), Offset(0f, h), width(Edge.LEFT))
    drawLine(Color.Black, Offset(w, 0f), Offset(w, h), width(Edge.RIGHT))
}

private fun valueColor(cell: CellState): Color = when {
    cell.conflicted -> Palette.CONFLICT
    cell.kind == CellKind.INITIAL -> Color.Black
    cell.kind == CellKind.SOLVED -> Palette.SOLVED
    else -> Palette.TYPED
}

/** The possible values in small digits, each in its place of a 3x3 square */
@Composable
private fun PossibleValues(possible: Set<Int>) {
    Column(Modifier.fillMaxSize().padding(2.dp)) {
        for (first in listOf(1, 4, 7)) {
            Row(Modifier.weight(1f)) {
                for (digit in first until first + 3) {
                    Box(Modifier.weight(1f).fillMaxSize(), contentAlignment = Alignment.Center) {
                        if (digit in possible) {
                            Text(digit.toString(), fontSize = 9.sp, lineHeight = 9.sp, color = Color.Gray)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StatusLine(status: GameMessage) {
    val color = when (status.kind) {
        MessageKind.WARNING -> Palette.WARNING
        MessageKind.SUCCESS, MessageKind.HINT -> Palette.SOLVED
        else -> MaterialTheme.colorScheme.onSurface
    }
    Text(status.text, color = color, modifier = Modifier.fillMaxWidth())
}

@Composable
private fun DigitPad(onDigit: (Int) -> Unit) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
        for (digit in 1..9) {
            FilledTonalButton(
                onClick = { onDigit(digit) },
                modifier = Modifier.weight(1f),
                contentPadding = PaddingValues(0.dp),
            ) {
                Text(digit.toString(), fontSize = 18.sp)
            }
        }
    }
}

/** Clear, the switch between setup and play, and quit */
@Composable
private fun Commands(modeSwitch: GameAction, intents: SudokuIntents) {
    val switchLabel = if (modeSwitch == GameAction.PLAY) "Play" else "Setup"
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        val commands = listOf(
            "Clear" to intents::onClear,
            switchLabel to intents::onSwitchMode,
            "Quit" to intents::onQuit,
        )
        for ((label, onClick) in commands) {
            OutlinedButton(onClick = onClick, modifier = Modifier.weight(1f)) {
                Text(label)
            }
        }
    }
}

@Composable
private fun Confirm(question: String, onAnswer: (Boolean) -> Unit) {
    AlertDialog(
        onDismissRequest = { onAnswer(false) },
        text = { Text(question) },
        confirmButton = { TextButton(onClick = { onAnswer(true) }) { Text("Yes") } },
        dismissButton = { TextButton(onClick = { onAnswer(false) }) { Text("No") } },
    )
}

@Preview(showBackground = true, heightDp = 640)
@Composable
private fun SudokuScreenPreview() {
    val empty = CellState(null, CellKind.TYPED, false, 0, (1..9).toSet(), emptySet())
    val cells = (0 until 9).flatMap { row -> (0 until 9).map { col -> Position(row, col) to empty } }.toMap() +
        (Position(4, 4) to empty.copy(value = 5, kind = CellKind.INITIAL, possible = emptySet()))
    val game = GameState(
        size = BoardSize(9, 9),
        cells = cells,
        selected = Position(4, 4),
        message = GameMessage("A hint", MessageKind.HINT),
        mode = "SETUP",
    )
    val state = SudokuUiState(game)
    MaterialTheme {
        Surface {
            SudokuScreen(state, PreviewIntents)
        }
    }
}

/** Intents that do nothing, for the preview */
private object PreviewIntents : SudokuIntents {
    override fun onCellTapped(position: Position) {}
    override fun onDigit(digit: Int) {}
    override fun onClear() {}
    override fun onSwitchMode() {}
    override fun onQuit() {}
    override fun onAnswer(yes: Boolean) {}
}

/** The screen's own colors */
private object Palette {
    val SELECTED = Color(0xFFFFF59D)
    val GUESS_SHADE = Color.Gray
    val CONFLICT = Color(0xFFD32F2F)
    val SOLVED = Color(0xFF0288D1)
    val TYPED = Color(0xFF1A237E)
    val WARNING = Color(0xFFB26A00)
}
