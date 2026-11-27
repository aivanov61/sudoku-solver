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

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import io.github.aivanov61.sudoku.R
import io.github.aivanov61.sudoku.ui.theme.SudokuTheme

/**
 * The game's splash screen, which informs the player about the copyright and GNU GPL.  The splash screen shows
 * the notice and reports a tap with [onTap].
 */
@Composable
fun SplashScreen(text: String, onTap: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .safeDrawingPadding()
            .clickable(interactionSource = null, indication = null, onClick = onTap)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)
        Box(
            modifier = Modifier.weight(1f),
            contentAlignment = Alignment.Center,
        ) {
            Text(text, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

// Private functions

@Preview(showBackground = true)
@Composable
private fun SplashScreenPreview() {
    SudokuTheme {
        Surface {
            SplashScreen(
                text = """Hello, World!
                    |This is a test program to see how well it does what I'm asking it to do.
                    |This is a long string so I can see how the centering and spacing works out.""".trimMargin(),
                onTap = {},
            )
        }
    }
}
