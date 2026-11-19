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
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

/**
 * The app's one Python, through Chaquopy, started on first use: slow the first time after an install, while
 * Chaquopy unpacks it.  The layouts and the game both use it, from different threads, so starting it is synchronized.
 */
object AppPython {
    @Synchronized
    fun of(application: Application): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(application))
        }
        return Python.getInstance()
    }
}
