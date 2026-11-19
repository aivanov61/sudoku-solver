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

import kotlinx.coroutines.CompletableDeferred

/**
 * A fake layout repository for tests: it returns the layouts it was given.  When [held], it holds them back until
 * [release], as a slow first start of Python would.
 */
class FakeLayoutRepository(private val layouts: List<Layout>, held: Boolean = false) : LayoutRepository {
    private val released = CompletableDeferred<Unit>()

    init {
        if (!held) {
            release()
        }
    }

    override suspend fun layouts(): List<Layout> {
        released.await()
        return layouts
    }

    /** Let the layouts be returned, to callers waiting and to those yet to come */
    fun release() {
        released.complete(Unit)
    }
}
