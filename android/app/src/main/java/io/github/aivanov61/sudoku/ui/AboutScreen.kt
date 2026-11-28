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

/**
 * About, pushed on top of the game: the app's name and [version], and the GNU GPL [notice] below them, scrolling
 * when it doesn't fit.  Up calls [onUp].
 */
@Composable
fun AboutScreen(version: String, notice: String, onUp: () -> Unit) {
    Scaffold(topBar = { UpTopBar(stringResource(R.string.about), onUp) }) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Column {
                Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineSmall)
                Text(stringResource(R.string.about_version, version), style = MaterialTheme.typography.bodyMedium)
            }
            Text(notice, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

// Private functions

@Preview(showBackground = true)
@Composable
private fun AboutScreenPreview() {
    SudokuTheme {
        AboutScreen(version = "1.0", notice = "Copyright (c) by ...\n\nThis program is free software: ...", onUp = {})
    }
}
