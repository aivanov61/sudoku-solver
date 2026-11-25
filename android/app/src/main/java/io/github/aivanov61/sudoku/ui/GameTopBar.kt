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

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import io.github.aivanov61.sudoku.R

/**
 * The game screen's Material 3 top app bar: the app's name, and the app-level menu behind the overflow button (⋮).
 * New puzzle is enabled once a new puzzle [canStartNew]; choosing it calls [onNewPuzzle].  Material 3 still marks
 * its app bars experimental, though they are its standard ones.  It goes inside content the screen has already
 * padded clear of the system bars (it may be beside the board), so it adds no insets of its own.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameTopBar(canStartNew: Boolean, onNewPuzzle: () -> Unit) {
    TopAppBar(
        title = { Text(stringResource(R.string.app_name)) },
        actions = { OverflowMenu(canStartNew, onNewPuzzle) },
        windowInsets = WindowInsets(0.dp),
    )
}

// Private functions

/**
 * The overflow button, and the menu it opens.  Whether the menu is open is kept here, not in the ViewModel: it is
 * UI element state with no logic behind it, which Google's guide on state hoisting lets a composable keep.
 */
@Composable
private fun OverflowMenu(canStartNew: Boolean, onNewPuzzle: () -> Unit) {
    var isOpen by remember { mutableStateOf(false) }
    Box {  // the menu opens anchored to the box, so below the button
        IconButton(onClick = { isOpen = true }) {
            Icon(painterResource(R.drawable.ic_more_vert), contentDescription = "More options")
        }
        DropdownMenu(expanded = isOpen, onDismissRequest = { isOpen = false }) {
            DropdownMenuItem(
                text = { Text("New puzzle") },
                onClick = {
                    isOpen = false
                    onNewPuzzle()
                },
                enabled = canStartNew,
            )
        }
    }
}

@Preview
@Composable
private fun GameTopBarPreview() {
    MaterialTheme {
        GameTopBar(canStartNew = true, onNewPuzzle = {})
    }
}
