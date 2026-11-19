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

import org.junit.Assert.assertEquals
import org.junit.Test

class ReflowTest {
    @Test
    fun theLinesOfAParagraphAreJoinedWithASpace() {
        assertEquals("This program is free software", "This program\nis free\nsoftware".reflow())
    }

    @Test
    fun paragraphsStaySeparatedByOneBlankLine() {
        assertEquals("First one.\n\nSecond one.", "First\none.\n\nSecond\none.".reflow())
    }

    @Test
    fun windowsLineEndingsAreReflowedToo() {
        assertEquals("First one.\n\nSecond one.", "First\r\none.\r\n\r\nSecond\r\none.\r\n".reflow())
    }

    @Test
    fun spacesAtTheEndsOfLinesAndOfTheTextAreDropped() {
        assertEquals("First one.\n\nSecond one.", "\n  First \n one.\n \nSecond\none.\n\n".reflow())
    }

    @Test
    fun spacesWithinALineAreKept() {
        assertEquals("License.  See the", "License.  See\nthe".reflow())
    }
}
