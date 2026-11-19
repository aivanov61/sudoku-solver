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

package io.github.aivanov61.sudoku.data

/**
 * A puzzle layout to choose from: its [name], the [label] to show (the name, and any notes on what keeps it from
 * working), and whether it [canPick] at all
 */
data class Layout(val name: String, val label: String, val canPick: Boolean)

/** The data layer's one way to the puzzle layouts, from the game's catalog */
interface LayoutRepository {
    suspend fun layouts(): List<Layout>
}
