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

import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import io.github.aivanov61.sudoku.ui.theme.SudokuTheme
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

/** Compose UI tests of the screens pushed on top of the game, How to play and About, run on the device */
class PushedScreensTest {
    @get:Rule
    val composeRule = createComposeRule()

    private var ups = 0

    // How to play

    @Test
    fun howToPlayExplainsSetupAndPlay() {
        composeRule.setContent { SudokuTheme { HowToPlayScreen(onUp = { ups++ }) } }
        composeRule.onNodeWithText("Set up the puzzle").assertExists()
        composeRule.onNodeWithText("Play").assertExists()
    }

    @Test
    fun upLeavesHowToPlay() {
        composeRule.setContent { SudokuTheme { HowToPlayScreen(onUp = { ups++ }) } }
        composeRule.onNodeWithContentDescription("Navigate up").performClick()
        assertEquals(1, ups)
    }

    // About

    @Test
    fun aboutShowsTheVersionAndTheNotice() {
        showAbout()
        composeRule.onNodeWithText("Version 1.0").assertExists()
        composeRule.onNodeWithText("the notice").assertExists()
    }

    @Test
    fun upLeavesAbout() {
        showAbout()
        composeRule.onNodeWithContentDescription("Navigate up").performClick()
        assertEquals(1, ups)
    }

    // Private functions

    private fun showAbout() {
        composeRule.setContent { SudokuTheme { AboutScreen(version = "1.0", notice = "the notice", onUp = { ups++ }) } }
    }
}
