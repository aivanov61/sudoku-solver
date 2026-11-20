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
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.navigation3.rememberViewModelStoreNavEntryDecorator
import androidx.navigation3.runtime.NavBackStack
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.runtime.rememberSaveableStateHolderNavEntryDecorator
import androidx.navigation3.ui.NavDisplay
import io.github.aivanov61.sudoku.ui.LayoutPickerScreen
import io.github.aivanov61.sudoku.ui.LayoutPickerViewModel
import io.github.aivanov61.sudoku.ui.Route
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

    /**
     * The Sudoku app: the copyright splash screen, then the layout picker when there isn't exactly one layout to play,
     * then the game, closing when the game is over.  Navigation 3 shows the last route on the back stack; each step
     * replaces the route before it, so Back leaves the app.  Each route's entry gets its own view models, which live
     * as long as the route is on the back stack.
     */
    @Composable
    private fun SudokuApp() {
        val backStack = rememberNavBackStack(Route.Splash)  // saved through rotation and process death
        NavDisplay(
            backStack = backStack,
            onBack = { backStack.removeLastOrNull() },
            entryDecorators = listOf(
                rememberSaveableStateHolderNavEntryDecorator(),
                rememberViewModelStoreNavEntryDecorator(),
            ),
            entryProvider = entryProvider {
                entry<Route.Splash> { Splash(onEnded = backStack::replaceLast) }
                entry<Route.LayoutPicker> { LayoutPicker(onPick = { backStack.replaceLast(Route.Game(it)) }) }
                entry<Route.Game> { route -> Game(route.layout) }
            },
        )
    }

    /** The splash screen, until it has ended: then [onEnded] is given the route that follows it */
    @Composable
    private fun Splash(onEnded: (Route) -> Unit) {
        val splash: SplashViewModel = viewModel(factory = SplashViewModel.Factory)
        val state by splash.uiState.collectAsStateWithLifecycle()
        val next = state.next
        if (next != null) {
            LaunchedEffect(next) { onEnded(next) }
        }
        SplashScreen(state.notice, splash::onTap)
    }

    /** The layout picker: [onPick] is given the name of the layout picked */
    @Composable
    private fun LayoutPicker(onPick: (String) -> Unit) {
        val picker: LayoutPickerViewModel = viewModel(factory = LayoutPickerViewModel.Factory)
        val state by picker.uiState.collectAsStateWithLifecycle()
        LayoutPickerScreen(state, onPick = { onPick(it.name) })
    }

    /**
     * The game on the [layout] named, saved whenever the app is stopped (Home, Back, another app, a rotation), as
     * Android may then end the app's process without calling it; and closing the app once the game is over
     */
    @Composable
    private fun Game(layout: String) {
        val game: SudokuViewModel = viewModel(factory = SudokuViewModel.factory(layout))
        LifecycleEventEffect(Lifecycle.Event.ON_STOP) { game.onStopped() }
        val state by game.uiState.collectAsStateWithLifecycle()
        if (state.game.isOver) {
            LaunchedEffect(Unit) { finish() }
        }
        SudokuScreen(state, game)
    }
}

/** Show the [route] in place of the last one, so Back doesn't return to it */
private fun NavBackStack<NavKey>.replaceLast(route: Route) {
    this[lastIndex] = route
}
