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

import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.res.painterResource
import io.github.aivanov61.sudoku.R

/**
 * The Material 3 top app bar of a screen pushed on top of another: its [title], and Up (←), which calls [onUp] to
 * pop it, as Back does.  It goes in a Scaffold's top bar, so it pads itself clear of the status bar.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UpTopBar(title: String, onUp: () -> Unit) {
    TopAppBar(
        title = { Text(title) },
        navigationIcon = {
            IconButton(onClick = onUp) {
                Icon(painterResource(R.drawable.ic_arrow_back), contentDescription = "Navigate up")
            }
        },
    )
}
