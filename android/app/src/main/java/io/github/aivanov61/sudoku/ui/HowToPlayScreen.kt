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

import androidx.annotation.StringRes
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import io.github.aivanov61.sudoku.R
import io.github.aivanov61.sudoku.ui.theme.SudokuTheme

/** How to play's paragraphs, in order: each a heading and its text */
private val PARAGRAPHS = listOf(
    R.string.how_to_play_setup_heading to R.string.how_to_play_setup,
    R.string.how_to_play_play_heading to R.string.how_to_play_play,
    R.string.how_to_play_guesses_heading to R.string.how_to_play_guesses,
    R.string.how_to_play_mistakes_heading to R.string.how_to_play_mistakes,
)

/**
 * How to play, pushed on top of the game: a short guide to setting up and playing a puzzle, from the string
 * resources, scrolling when it doesn't fit.  It is stateless and has no view model: it has no state and no data.
 * Up calls [onUp].
 */
@Composable
fun HowToPlayScreen(onUp: () -> Unit) {
    Scaffold(topBar = { UpTopBar(stringResource(R.string.how_to_play), onUp) }) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            for ((heading, text) in PARAGRAPHS) {
                Paragraph(heading, text)
            }
        }
    }
}

// Private functions

/** A paragraph: its heading, and its text below it */
@Composable
private fun Paragraph(@StringRes heading: Int, @StringRes text: Int) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(stringResource(heading), style = MaterialTheme.typography.titleMedium)
        Text(stringResource(text), style = MaterialTheme.typography.bodyLarge)
    }
}

@Preview(showBackground = true)
@Composable
private fun HowToPlayScreenPreview() {
    SudokuTheme {
        HowToPlayScreen(onUp = {})
    }
}
