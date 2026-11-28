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

import androidx.annotation.DrawableRes
import android.content.res.Configuration
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.aivanov61.sudoku.R
import io.github.aivanov61.sudoku.data.GameDialog
import io.github.aivanov61.sudoku.data.GameState
import io.github.aivanov61.sudoku.game.BoardSize
import io.github.aivanov61.sudoku.game.CellKind
import io.github.aivanov61.sudoku.game.CellState
import io.github.aivanov61.sudoku.game.Conflict
import io.github.aivanov61.sudoku.game.Edge
import io.github.aivanov61.sudoku.game.GameAction
import io.github.aivanov61.sudoku.game.GameMessage
import io.github.aivanov61.sudoku.game.GameMode
import io.github.aivanov61.sudoku.game.MessageKind
import io.github.aivanov61.sudoku.game.Position
import io.github.aivanov61.sudoku.ui.theme.GameColors
import io.github.aivanov61.sudoku.ui.theme.SudokuTheme

/** The narrowest the controls can be beside the board: the commands, and the digit pad's three buttons across */
private val MIN_CONTROLS_WIDTH = 300.dp

/** The digits in each row of a 3x3 square, as both a cell's small digits and the digit pad lay them out */
private val DIGIT_ROWS = listOf(1..3, 4..6, 7..9)

/** How much of its color a disabled control keeps, as Material 3's own components do; a digit with none left too */
private const val DISABLED_ALPHA = 0.38f

/** How thick the selected cell's outline is, and the band that outlines it and its related cells together */
private val SELECTED_OUTLINE = 3.dp
private val RELATED_OUTLINE = 2.dp

/** How thick the lines are between the blocks, and between the cells within a block */
private val BLOCK_EDGE = 2.5.dp
private val CELL_EDGE = 0.5.dp

/**
 * The game's screen: the top app bar, the board, the message area, the command palette and the digit pad; and
 * the game's yes/no questions and messages to be seen, and New puzzle's question, as dialogs.  It only shows the
 * state, and passes what the player does on to the intents.  The Material 3 Scaffold pads the content clear of the
 * system bars; the content places the top app bar itself, as where it goes depends on the space.  The menu's How
 * to play and About are navigation, not intents, so they go up as [onHowToPlay] and [onAbout].
 */
@Composable
fun SudokuScreen(state: SudokuUiState, intents: SudokuIntents, onHowToPlay: () -> Unit, onAbout: () -> Unit) {
    Scaffold { padding ->
        val topBar = @Composable { GameTopBar(state.canStartNew, intents::onNewPuzzle, onHowToPlay, onAbout) }
        GameContent(state, intents, topBar, Modifier.padding(padding))
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
 * takes the full height, and the top app bar and the controls go beside it; otherwise everything is stacked
 * in a column, the top app bar first.  It goes by the space it is given, not by the device's orientation, since a
 * split screen or a large screen can be wide in portrait.
 */
@Composable
private fun GameContent(state: SudokuUiState, intents: SudokuIntents, topBar: @Composable () -> Unit, modifier: Modifier) {
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
 * The top app bar, then the game: the board, as large as fits, and the controls at the bottom of the screen, within
 * thumb reach.  Until the game has started, or once it has failed, a notice says so in its place.  The board fits
 * both the width and the height left: the controls are measured first, and the board gets at most the rest (`weight`
 * without fill), at its own aspect ratio.
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
                val boardModifier = Modifier.weight(1f, fill = false).aspectRatio(size.cols.toFloat() / size.rows)
                Board(size, state, intents::onCellTapped, boardModifier)
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
 * The cells, and in the color of the kind of value the pad enters, the selected one outlined, and it and its related
 * cells outlined together
 */
@Composable
private fun Board(size: BoardSize, state: SudokuUiState, onTap: (Position) -> Unit, modifier: Modifier) {
    val game = state.game
    val outline = SudokuTheme.gameColors.values.of(state.entering)
    val board = modifier.drawWithContent {
        drawContent()
        drawRelatedOutline(size, state, outline)
    }
    Column(board) {
        for (row in 0 until size.rows) {
            Row(Modifier.weight(1f)) {
                for (col in 0 until size.cols) {
                    val position = Position(row, col)
                    val modifier = Modifier
                        .weight(1f)
                        .fillMaxSize()
                        .clickable { onTap(position) }
                        .semantics { contentDescription = "Row ${row + 1}, column ${col + 1}" }
                    Cell(game.cells[position], if (position == game.selected) outline else null, modifier)
                }
            }
        }
    }
}

/** A cell in the game's colors, outlined in [outline] if any */
@Composable
private fun Cell(cell: CellState?, outline: Color?, modifier: Modifier) {
    val colors = MaterialTheme.colorScheme
    val gameColors = SudokuTheme.gameColors
    Box(
        modifier = modifier
            .background(gameColors.background(cell))
            .drawBehind { drawEdges(cell?.edges.orEmpty(), colors.onSurface) }
            .then(if (outline != null) Modifier.border(SELECTED_OUTLINE, outline) else Modifier),
        contentAlignment = Alignment.Center,
    ) {
        val value = cell?.value
        when {
            cell == null -> {}
            value != null -> Text(
                value.toString(),
                fontSize = 22.sp,
                fontWeight = if (cell.kind == CellKind.INITIAL || cell.conflict != Conflict.NONE) FontWeight.Bold else FontWeight.Normal,
                color = gameColors.value(cell),
            )
            else -> PossibleValues(cell.possible, colors.onSurfaceVariant)
        }
    }
}

/** Thin lines around every cell, thick ones on the sides that are block edges ([edges]) */
private fun DrawScope.drawEdges(edges: Set<Edge>, color: Color) {
    val (w, h) = size.width to size.height
    drawLine(color, Offset(0f, 0f), Offset(w, 0f), edgeWidth(Edge.TOP, edges))
    drawLine(color, Offset(0f, h), Offset(w, h), edgeWidth(Edge.BOTTOM, edges))
    drawLine(color, Offset(0f, 0f), Offset(0f, h), edgeWidth(Edge.LEFT, edges))
    drawLine(color, Offset(w, 0f), Offset(w, h), edgeWidth(Edge.RIGHT, edges))
}

/** How thick the line on the side of a cell is: a block edge's, if it is one of the cell's [edges], else a cell's */
private fun DrawScope.edgeWidth(edge: Edge, edges: Set<Edge>): Float = (if (edge in edges) BLOCK_EDGE else CELL_EDGE).toPx()

/**
 * The band, [RELATED_OUTLINE] wide, that outlines the selected cell and its related cells together: inside them, just
 * within the grid's lines, on their [SudokuUiState.outlined] sides.  The board draws it over the cells, so it runs
 * unbroken across the lines between them.
 */
private fun DrawScope.drawRelatedOutline(board: BoardSize, state: SudokuUiState, color: Color) {
    val (cellWidth, cellHeight) = size.width / board.cols to size.height / board.rows
    val band = RELATED_OUTLINE.toPx()
    for (position in state.game.related + state.game.selected) {
        val (left, top) = position.col * cellWidth to position.row * cellHeight
        val (right, bottom) = left + cellWidth to top + cellHeight
        val edges = state.game.cells[position]?.edges.orEmpty()
        for (edge in state.outlined(position)) {
            val inset = edgeWidth(edge, edges) / 2 + band / 2  // the band's middle, from the middle of the grid's line
            when (edge) {
                Edge.TOP -> drawLine(color, Offset(left, top + inset), Offset(right, top + inset), band)
                Edge.BOTTOM -> drawLine(color, Offset(left, bottom - inset), Offset(right, bottom - inset), band)
                Edge.LEFT -> drawLine(color, Offset(left + inset, top), Offset(left + inset, bottom), band)
                Edge.RIGHT -> drawLine(color, Offset(right - inset, top), Offset(right - inset, bottom), band)
            }
        }
    }
}

/** The possible values in small digits, each in its place of a 3x3 square */
@Composable
private fun PossibleValues(possible: Set<Int>, color: Color) {
    Column(Modifier.fillMaxSize().padding(2.dp)) {
        for (digits in DIGIT_ROWS) {
            Row(Modifier.weight(1f)) {
                for (digit in digits) {
                    Box(Modifier.weight(1f).fillMaxSize(), contentAlignment = Alignment.Center) {
                        if (digit in possible) {
                            Text(digit.toString(), fontSize = 9.sp, lineHeight = 9.sp, color = color)
                        }
                    }
                }
            }
        }
    }
}

/**
 * What goes below or beside the board: the message area, the mode switch, and nearest the thumb, the commands and,
 * on their right, the digit pad
 */
@Composable
private fun Controls(state: SudokuUiState, intents: SudokuIntents, modifier: Modifier) {
    Column(modifier, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        MessageArea(state.game.message)
        ModeSwitch(state.game.mode, intents::onSwitchMode)
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
            CommandPalette(state, intents, Modifier.weight(1f))
            DigitPad(state::left, SudokuTheme.gameColors.values.of(state.entering), intents::onDigit, Modifier.weight(1f))
        }
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
private fun messageColor(kind: MessageKind): Color = SudokuTheme.gameColors.message(kind)

/**
 * The nine digits in a 3x3 square, each in the place it has among a cell's small digits, in the [color] of the kind
 * of value they enter, each with how many places it has left ([left]); every digit can be entered, even with none left
 */
@Composable
private fun DigitPad(left: (Int) -> Int, color: Color, onDigit: (Int) -> Unit, modifier: Modifier) {
    Column(modifier, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        for (digits in DIGIT_ROWS) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                for (digit in digits) {
                    FilledTonalButton(
                        onClick = { onDigit(digit) },
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(0.dp),
                    ) {
                        DigitKey(digit, left(digit), color)
                    }
                }
            }
        }
    }
}

/**
 * The digit in its [color], with the number of its places left small below it in the key's own, which TalkBack reads
 * as "3 left"; once none are left, the digit is dimmed and the number left out, its line kept so the pad doesn't move
 */
@Composable
private fun DigitKey(digit: Int, left: Int, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(digit.toString(), fontSize = 18.sp, color = color, modifier = Modifier.alpha(if (left > 0) 1f else DISABLED_ALPHA))
        Text(
            if (left > 0) left.toString() else "",
            style = MaterialTheme.typography.labelSmall,
            modifier = Modifier.clearAndSetSemantics {
                contentDescription = if (left > 0) "$left left" else "none left"
            },
        )
    }
}

/**
 * The game-play commands, two by two: Undo and Erase, and below them Rewind beside the Guess toggle, as Rewind takes
 * back to the last guess
 */
@Composable
private fun CommandPalette(state: SudokuUiState, intents: SudokuIntents, modifier: Modifier) {
    val undo = Command("Undo", R.drawable.ic_undo, GameAction.UNDO, intents::onUndo)
    val erase = Command("Erase", R.drawable.ic_ink_eraser, GameAction.DEL, intents::onErase)
    val rewind = Command("Rewind", R.drawable.ic_fast_rewind, GameAction.REWIND, intents::onRewind)
    Column(modifier, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(Modifier.fillMaxWidth()) {
            for (command in listOf(undo, erase)) {
                CommandButton(command, enabled = state.offers(command.action), Modifier.weight(1f))
            }
        }
        Row(Modifier.fillMaxWidth()) {
            CommandButton(rewind, enabled = state.offers(rewind.action), Modifier.weight(1f))
            GuessToggle(state.guessing, state.offers(GameAction.GUESS), intents::onGuessToggled, Modifier.weight(1f))
        }
    }
}

/**
 * Setup | Play, a Material 3 segmented button.  The selected segment is the mode the game last reported, so a tap on
 * the other one only asks the game to switch: if the game refuses, the segment stays where it was.
 */
@Composable
private fun ModeSwitch(mode: GameMode?, onSwitch: () -> Unit) {
    val segments = listOf(GameMode.SETUP to "Setup", GameMode.PLAY to "Play")
    SingleChoiceSegmentedButtonRow(Modifier.fillMaxWidth()) {
        segments.forEachIndexed { index, (segment, label) ->
            SegmentedButton(
                selected = segment == mode,
                onClick = {
                    if (segment != mode) {
                        onSwitch()
                    }
                },
                shape = SegmentedButtonDefaults.itemShape(index, segments.size),
            ) {
                Text(label)
            }
        }
    }
}

/** A command of the palette: its label and icon, the game's action it asks for, and the intent that asks for it */
private data class Command(
    val label: String,
    @param:DrawableRes val icon: Int,
    val action: GameAction,
    val onClick: () -> Unit,
)

/** The command's icon with its label below, as one button, so the whole of it can be tapped */
@Composable
private fun CommandButton(command: Command, enabled: Boolean, modifier: Modifier) {
    TextButton(
        onClick = command.onClick,
        modifier = modifier,
        enabled = enabled,
        contentPadding = PaddingValues(4.dp),
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(painterResource(command.icon), contentDescription = null)  // the label says what it is
            Text(command.label, style = MaterialTheme.typography.labelMedium)
        }
    }
}

/**
 * Guess, laid out as the commands are, and filled while it is on, when the pad enters guesses.  The whole of it
 * toggles, and TalkBack reads it as a switch, on or off.
 */
@Composable
private fun GuessToggle(on: Boolean, enabled: Boolean, onToggle: () -> Unit, modifier: Modifier) {
    val colors = MaterialTheme.colorScheme
    val contentColor = when {
        !enabled -> colors.onSurface.copy(alpha = DISABLED_ALPHA)
        on -> colors.onSecondaryContainer
        else -> colors.primary  // as a TextButton's
    }
    Column(
        modifier = modifier
            .clip(ButtonDefaults.textShape)
            .background(if (on) colors.secondaryContainer else Color.Transparent)
            .toggleable(value = on, enabled = enabled, role = Role.Switch, onValueChange = { onToggle() })
            .defaultMinSize(minHeight = ButtonDefaults.MinHeight)
            .padding(4.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(painterResource(R.drawable.ic_question_mark), contentDescription = null, tint = contentColor)
        Text("Guess", style = MaterialTheme.typography.labelMedium, color = contentColor)
    }
}

/**
 * The board, as tall as the space, and beside it the top app bar and the controls, so the board gets
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
        Board(size, state, intents::onCellTapped, boardModifier)
        Column(
            modifier = Modifier.weight(1f),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            topBar()
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
@Preview(name = "Portrait, dark", showBackground = true, widthDp = 393, heightDp = 851, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Preview(name = "Landscape", showBackground = true, widthDp = 851, heightDp = 393)
@Composable
private fun SudokuScreenPreview() {
    val empty = CellState(null, CellKind.TYPED, Conflict.NONE, 0, (1..9).toSet(), emptySet())
    val value = empty.copy(possible = emptySet())
    val cells = (0 until 9).flatMap { row -> (0 until 9).map { col -> Position(row, col) to empty } }.toMap() + mapOf(
        Position(4, 4) to value.copy(value = 5, kind = CellKind.INITIAL),
        Position(4, 0) to value.copy(value = 3),
        Position(0, 4) to value.copy(value = 7, kind = CellKind.SOLVED),
        Position(7, 7) to value.copy(value = 1, kind = CellKind.GUESS, depth = 1),
        Position(7, 8) to value.copy(value = 2, kind = CellKind.GUESS, depth = GameColors.GUESS_SHADES),
        Position(1, 1) to value.copy(value = 8, conflict = Conflict.CONFLICTED),
        Position(1, 7) to value.copy(value = 8, kind = CellKind.GUESS, conflict = Conflict.CONFLICTING, depth = 2),
    )
    val selected = Position(4, 4)
    val related = (0 until 9).flatMap { listOf(Position(4, it), Position(it, 4)) } +
        (3..5).flatMap { row -> (3..5).map { col -> Position(row, col) } }
    val game = GameState(
        size = BoardSize(9, 9),
        cells = cells,
        selected = selected,
        related = related.toSet() - selected,
        message = GameMessage("A hint", MessageKind.HINT),
        mode = GameMode.SETUP,
        offered = setOf(GameAction.PLAY, GameAction.VALUE, GameAction.DEL),
    )
    val state = SudokuUiState(game)
    SudokuTheme {
        Surface {
            SudokuScreen(state, PreviewIntents, onHowToPlay = {}, onAbout = {})
        }
    }
}

/** Intents that do nothing, for the preview */
private object PreviewIntents : SudokuIntents {
    override fun onCellTapped(position: Position) {}
    override fun onDigit(digit: Int) {}
    override fun onErase() {}
    override fun onUndo() {}
    override fun onRewind() {}
    override fun onGuessToggled() {}
    override fun onSwitchMode() {}
    override fun onAnswer(yes: Boolean) {}
    override fun onInformed() {}
    override fun onNewPuzzle() {}
    override fun onNewPuzzleAnswer(yes: Boolean) {}
}

