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

package io.github.aivanov61.sudoku.game

import android.app.Application
import io.github.aivanov61.sudoku.data.Layout
import io.github.aivanov61.sudoku.data.LayoutRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * The layouts from the game's catalog, through Chaquopy (ui/android/catalog.py), off the UI thread: asking for them
 * first starts Python, which is slow the first time after an install
 */
class PythonLayoutRepository(private val application: Application) : LayoutRepository {
    override suspend fun layouts(): List<Layout> = withContext(Dispatchers.IO) {
        val catalog = AppPython.of(application).getModule("ui.android.catalog")["Catalog"]!!
        catalog.callAttr("layouts").asList().map { layout ->
            val (name, label, canPick) = layout.asList()
            Layout(name.toString(), label.toString(), canPick.toBoolean())
        }
    }
}
