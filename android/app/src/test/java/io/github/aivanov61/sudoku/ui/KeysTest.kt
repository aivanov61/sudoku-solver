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

import io.github.aivanov61.sudoku.data.Layout
import kotlinx.serialization.descriptors.elementNames
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Test

class KeysTest {
    // A game's route

    @Test
    fun eachGameOnTheSameLayoutHasARouteOfItsOwn() {
        assertNotEquals(Route.Game(STANDARD), Route.Game(STANDARD))
    }

    @Test
    fun aGamesRouteIsSavedWithItsId() {
        val descriptor = Route.Game.serializer().descriptor
        assertFalse(descriptor.isElementOptional(descriptor.elementNames.indexOf("id")))
    }

    // The route that starts a game

    @Test
    fun theOnlyLayoutIsPlayed() {
        assertEquals(STANDARD, Route.toStart(listOf(layout(STANDARD))).gameLayout)
    }

    @Test
    fun theOnlyLayoutGoesToThePickerWhenItCantBePicked() {
        assertEquals(Route.LayoutPicker, Route.toStart(listOf(layout(STANDARD, canPick = false))))
    }

    @Test
    fun severalLayoutsGoToThePicker() {
        assertEquals(Route.LayoutPicker, Route.toStart(listOf(layout(STANDARD), layout(ANOTHER))))
    }

    @Test
    fun noLayoutsGoToThePicker() {
        assertEquals(Route.LayoutPicker, Route.toStart(emptyList()))
    }

    // Resuming the saved game

    @Test
    fun theSavedGamesLayoutIsPlayed() {
        assertEquals(ANOTHER, Route.toStart(listOf(layout(STANDARD), layout(ANOTHER)), savedLayout = ANOTHER).gameLayout)
    }

    @Test
    fun aSavedGameOnALayoutThatCantBePickedGoesToThePicker() {
        val layouts = listOf(layout(STANDARD), layout(ANOTHER, canPick = false))
        assertEquals(Route.LayoutPicker, Route.toStart(layouts, savedLayout = ANOTHER))
    }

    @Test
    fun aSavedGameOnALayoutNoLongerThereLeavesTheOnlyLayoutPlayed() {
        assertEquals(STANDARD, Route.toStart(listOf(layout(STANDARD)), savedLayout = ANOTHER).gameLayout)
    }

    // Private functions

    /** A layout with the name, which can be picked unless [canPick] says otherwise */
    private fun layout(name: String, canPick: Boolean = true) = Layout(name, label = name, canPick)

    private companion object {
        const val STANDARD = "Standard 9x9"
        const val ANOTHER = "Another"
    }
}
