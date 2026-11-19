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

import android.content.res.AssetManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * The data layer's one way to the GNU GPL copyright notice.
 */
interface CopyrightRepository {
    suspend fun notice(): String
}

/**
 * This reads the notice from the app [assets], reflowed with [String.reflow]: the file breaks its lines for the
 * terminal, and a screen wraps each paragraph to its own width.
 */
class AssetCopyrightRepository(private val assets: AssetManager) : CopyrightRepository {
    override suspend fun notice(): String = withContext(Dispatchers.IO) {
        assets.open("copyright.txt").bufferedReader().use {
            it.readText().reflow()
        }
    }
}
