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
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.aivanov61.sudoku.data.GameDialog
import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Edge
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameMessage
import io.github.aivanov61.sudoku.game.MessageKind
import io.github.aivanov61.sudoku.game.Position

/** The narrowest the controls can be beside the board: the digit pad's nine buttons, and the space between them */
private val MIN_CONTROLS_WIDTH = 300.dp

/**
 * The game's screen: the top app bar, the mode and the board, the message area, a digit pad and a few commands; and
 * the game's yes/no questions and messages to be seen, and New puzzle's question, as dialogs.  It only shows the
 * state, and passes what the player does on to the intents.  The Material 3 Scaffold pads the content clear of the
 * system bars; the content places the top app bar itself, as where it goes depends on the space.
 */
@Composable
fun SudokuScreen(state: SudokuUiState, intents: SudokuIntents) {
    Scaffold { padding ->
        GameContent(state, intents, Modifier.padding(padding))
    }
    when (val dialog = state.game.dialog) {
        is GameDialog.Confirm -> ConfirmDialog(dialog.question, intents::onAnswer)
        is GameDialog.Inform -> InformDialog(dialog.message, intents::onInformed)
        null -> {}
    }
    if (state.askingNewPuzzle) {
        NewPuzzleDialog(intents::onNewPuzzleAnswer)
    }
}

// Private functions

/**
 * The game and its top app bar.  When there is room beside a board as tall as the space for the controls, the board
 * takes the full height, and the top app bar, the mode and the controls go beside it; otherwise everything is stacked
 * in a column, the top app bar first.  It goes by the space it is given, not by the device's orientation, since a
 * split screen or a large screen can be wide in portrait.
 */
@Composable
private fun GameContent(state: SudokuUiState, intents: SudokuIntents, modifier: Modifier) {
    val topBar = @Composable { GameTopBar(state.canStartNew, intents::onNewPuzzle) }
    BoxWithConstraints(modifier.fillMaxSize()) {
        val size = state.game.size
        if (size == null || state.game.failure != null || (maxWidth - maxHeight < MIN_CONTROLS_WIDTH)) {
            Stacked(state, intents, topBar)
        } else {
            SideBySide(size, state, intents, topBar)
        }
    }
}

/**
 * The top app bar, then the game: the mode and the board, as large as fits, and the controls at the bottom of the
 * screen, within thumb reach.  Until the game has started, or once it has failed, a notice says so in its place.
 */
@Composable
private fun Stacked(state: SudokuUiState, intents: SudokuIntents, topBar: @Composable () -> Unit) {
    Column {
        topBar()
        val contentModifier = Modifier.weight(1f).fillMaxWidth().padding(8.dp)
        val size = state.game.size
        val failure = state.game.failure
        when {
            failure != null -> Notice("The game stopped: $failure", contentModifier, MaterialTheme.colorScheme.error)
            size == null -> Notice("Starting the game…", contentModifier)
            else -> Column(
                modifier = contentModifier,
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                ModeAndBoard(size, state.game, intents::onCellTapped, Modifier.weight(1f))
                Controls(state, intents, Modifier.fillMaxWidth())
            }
        }
    }
}

/** What the screen says in place of the board */
@Composable
private fun Notice(text: String, modifier: Modifier, color: Color = Color.Unspecified) {
    Box(modifier, contentAlignment = Alignment.TopCenter) {
        Text(text, color = color)
    }
}

/**
 * The mode's name, and below it the board, as large as fits both the width and the height left: the controls are
 * measured first, and the board gets at most the rest (`weight` without fill), at its own aspect ratio
 */
@Composable
private fun ModeAndBoard(size: BoardSize, game: GameState, onTap: (Position) -> Unit, modifier: Modifier) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(game.mode, style = MaterialTheme.typography.titleMedium)
        val boardModifier = Modifier.weight(1f, fill = false).aspectRatio(size.cols.toFloat() / size.rows)
        Board(size, game.cells, game.selected, onTap, boardModifier)
    }
}

@Composable
private fun Board(
    size: BoardSize,
    cells: Map<Position, CellState>,
    selected: Position,
    onTap: (Position) -> Unit,
    modifier: Modifier,
) {
    Column(modifier) {
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

/** What goes below or beside the board: the message area, the digit pad and the commands */
@Composable
private fun Controls(state: SudokuUiState, intents: SudokuIntents, modifier: Modifier) {
    Column(modifier, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        MessageArea(state.game.message)
        DigitPad(intents::onDigit)
        Commands(state.modeSwitch, intents)
    }
}

/**
 * The status message, colored by its kind, in a tonal surface always three lines of text tall (at the player's font
 * size), so neither a blank message nor a long one moves the controls; a longer one scrolls, from its top
 */
@Composable
private fun MessageArea(status: GameMessage) {
    val style = MaterialTheme.typography.bodyLarge
    val height = with(LocalDensity.current) { (style.lineHeight * 3).toDp() }
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.medium,
        color = MaterialTheme.colorScheme.surfaceContainerHigh,
    ) {
        key(status) {
            Text(
                status.text,
                style = style,
                color = messageColor(status.kind),
                modifier = Modifier
                    .padding(horizontal = 12.dp, vertical = 8.dp)
                    .height(height)
                    .verticalScroll(rememberScrollState()),
            )
        }
    }
}

/** The color of a message of the kind, the same on the status line and in a dialog */
@Composable
private fun messageColor(kind: MessageKind): Color = when (kind) {
    MessageKind.WARNING -> Palette.WARNING
    MessageKind.SUCCESS, MessageKind.HINT -> Palette.SOLVED
    else -> MaterialTheme.colorScheme.onSurface
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

/** Clear, and the switch between setup and play */
@Composable
private fun Commands(modeSwitch: GameAction, intents: SudokuIntents) {
    val switchLabel = if (modeSwitch == GameAction.PLAY) "Play" else "Setup"
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        val commands = listOf(
            "Clear" to intents::onClear,
            switchLabel to intents::onSwitchMode,
        )
        for ((label, onClick) in commands) {
            OutlinedButton(onClick = onClick, modifier = Modifier.weight(1f)) {
                Text(label)
            }
        }
    }
}

/**
 * The board, as tall as the space, and beside it the top app bar, the mode and the controls, so the board gets
 * every row of the screen that a top app bar above it would take
 */
@Composable
private fun SideBySide(
    size: BoardSize,
    state: SudokuUiState,
    intents: SudokuIntents,
    topBar: @Composable () -> Unit,
) {
    Row(Modifier.padding(8.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        val ratio = size.cols.toFloat() / size.rows
        val boardModifier = Modifier.fillMaxHeight().aspectRatio(ratio, matchHeightConstraintsFirst = true)
        Board(size, state.game.cells, state.game.selected, intents::onCellTapped, boardModifier)
        Column(
            modifier = Modifier.weight(1f),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            topBar()
            Text(state.game.mode, style = MaterialTheme.typography.titleMedium)
            Controls(state, intents, Modifier.fillMaxWidth())
        }
    }
}

/** The game's yes/no question: [onAnswer] gets the player's answer, and Back or a tap outside is No */
@Composable
private fun ConfirmDialog(question: String, onAnswer: (Boolean) -> Unit) {
    AlertDialog(
        onDismissRequest = { onAnswer(false) },
        text = { Text(question) },
        confirmButton = { TextButton(onClick = { onAnswer(true) }) { Text("Yes") } },
        dismissButton = { TextButton(onClick = { onAnswer(false) }) { Text("No") } },
    )
}

/**
 * The game's message, until the player has seen it: [onSeen] is called on OK, and on Back or a tap outside, since
 * the game only waits until the message has been seen.  A warning is titled so.
 */
@Composable
private fun InformDialog(message: GameMessage, onSeen: () -> Unit) {
    AlertDialog(
        onDismissRequest = onSeen,
        title = if (message.kind == MessageKind.WARNING) { { Text("Warning") } } else null,
        text = { Text(message.text, color = messageColor(message.kind)) },
        confirmButton = { TextButton(onClick = onSeen) { Text("OK") } },
    )
}

/** New puzzle's question, asked when the board has values: [onAnswer] gets whether to start new */
@Composable
private fun NewPuzzleDialog(onAnswer: (Boolean) -> Unit) {
    AlertDialog(
        onDismissRequest = { onAnswer(false) },
        title = { Text("Start a new puzzle?") },
        text = { Text("The one in progress will be lost.") },
        confirmButton = { TextButton(onClick = { onAnswer(true) }) { Text("Start new") } },
        dismissButton = { TextButton(onClick = { onAnswer(false) }) { Text("Cancel") } },
    )
}

@Preview(name = "Portrait", showBackground = true, widthDp = 393, heightDp = 851)
@Preview(name = "Landscape", showBackground = true, widthDp = 851, heightDp = 393)
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
    override fun onAnswer(yes: Boolean) {}
    override fun onInformed() {}
    override fun onNewPuzzle() {}
    override fun onNewPuzzleAnswer(yes: Boolean) {}
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
