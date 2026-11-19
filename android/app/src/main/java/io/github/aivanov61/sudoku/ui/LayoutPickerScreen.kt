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
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ListItem
import androidx.compose.material3.ListItemDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import io.github.aivanov61.sudoku.data.Layout

/**
 * The choice of puzzle layout: a list of the layouts, each with its label.  A broken one is shown, with its notes,
 * but can't be picked; when none can be picked, the screen says so above the list.  A pick is reported with
 * [onPick].
 */
@Composable
fun LayoutPickerScreen(state: LayoutPickerUiState, onPick: (Layout) -> Unit) {
    Column(modifier = Modifier.fillMaxSize().safeDrawingPadding()) {
        Text(
            "Choose a puzzle layout",
            modifier = Modifier.padding(24.dp),
            style = MaterialTheme.typography.headlineMedium,
        )
        if (state.noneCanBePicked) {
            Text(
                "No puzzle layout can be played.",
                modifier = Modifier.padding(horizontal = 24.dp),
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyLarge,
            )
        }
        LazyColumn {
            items(state.layouts.orEmpty()) { layout -> LayoutItem(layout, onPick) }
        }
    }
}

// Private functions

/** One layout in the list: it can be tapped only when it can be picked, and is dimmed otherwise */
@Composable
private fun LayoutItem(layout: Layout, onPick: (Layout) -> Unit) {
    ListItem(
        headlineContent = { Text(layout.label) },
        modifier = Modifier.clickable(enabled = layout.canPick) { onPick(layout) },
        colors = ListItemDefaults.colors(
            headlineColor = MaterialTheme.colorScheme.onSurface.copy(alpha = if (layout.canPick) 1f else DIMMED),
        ),
    )
}

/** How much of a color shows in content that can't be used, as Material 3 dims disabled content */
private const val DIMMED = 0.38f

@Preview(showBackground = true)
@Composable
private fun LayoutPickerScreenPreview() {
    MaterialTheme {
        Surface {
            LayoutPickerScreen(
                LayoutPickerUiState(
                    listOf(
                        Layout("Standard 9x9", "Standard 9x9", canPick = true),
                        Layout("Broken", "Broken (it has no blocks)", canPick = false),
                    ),
                ),
                onPick = {},
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun LayoutPickerScreenNonePreview() {
    MaterialTheme {
        Surface {
            LayoutPickerScreen(
                LayoutPickerUiState(listOf(Layout("Broken", "Broken (it has no blocks)", canPick = false))),
                onPick = {},
            )
        }
    }
}
