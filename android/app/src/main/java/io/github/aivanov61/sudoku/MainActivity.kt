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

package io.github.aivanov61.sudoku

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import io.github.aivanov61.sudoku.ui.SplashScreen
import io.github.aivanov61.sudoku.ui.SplashViewModel
import io.github.aivanov61.sudoku.ui.SudokuScreen
import io.github.aivanov61.sudoku.ui.SudokuViewModel

/** The app's one startup activity: it hosts [SudokuApp] */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    SudokuApp()
                }
            }
        }
    }

    /** The Sudoku app: copyright splash screen followed by the game, and then close when the game is over */
    @Composable
    private fun SudokuApp() {
        val splash: SplashViewModel = viewModel(factory = SplashViewModel.Factory)
        val splashState by splash.uiState.collectAsStateWithLifecycle()

        // Made now, not after the splash, so the game (and Python's slow first start) gets started behind the splash
        val game: SudokuViewModel = viewModel(factory = SudokuViewModel.factory(STANDARD_LAYOUT))
        val gameState by game.uiState.collectAsStateWithLifecycle()

        if (!splashState.hasEnded) {
            SplashScreen(splashState.notice, splash::onTap)
        } else {
            if (gameState.game.isOver) {
                LaunchedEffect(Unit) { finish() }
            }
            SudokuScreen(gameState, game)
        }
    }

    private companion object {
        /**
         * Temporary, deleted in phase 4b: the layout played until navigation takes the layouts from the game's catalog.
         * It repeats Board3x3.NAME from the Python code, which only the catalog should give.
         */
        const val STANDARD_LAYOUT = "Standard 9x9"
    }
}
