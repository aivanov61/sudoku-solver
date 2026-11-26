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

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class GuessShadesTest {
    @Test
    fun aCellOutsideAnyGuessIsNotShaded() {
        assertNull(GuessShades.of(0))
    }

    @Test
    fun eachGuessDeeperHasTheNextShade() {
        val shades = (1..GuessShades.COLORS.size).map { GuessShades.of(it) }
        assertEquals(GuessShades.COLORS, shades)
    }

    @Test
    fun guessesDeeperThanTheLastShadeRepeatIt() {
        assertEquals(GuessShades.COLORS.last(), GuessShades.of(GuessShades.COLORS.size + 1))
    }
}
