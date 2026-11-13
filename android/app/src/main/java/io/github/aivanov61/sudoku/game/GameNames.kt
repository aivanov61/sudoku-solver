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

/** Something the Python game names: its gameName is the game's own name for it */
interface GameNamed {
    val gameName: String
}

/** The entry of E that the game calls name, or null if the app doesn't know it */
inline fun <reified E> fromGameName(name: String): E? where E : Enum<E>, E : GameNamed =
    enumValues<E>().firstOrNull { it.gameName == name }

/** The player's actions the app uses so far: the game's Action values (game/actions.py) */
enum class GameAction(override val gameName: String) : GameNamed {
    PLAY("play"),
    INIT("init"),
    VALUE("value"),
    SELECT("select"),
    DEL("del"),
    QUIT("quit"),
}

/**
 * How a cell's value got there: the game's primary attributes (game/cell_attrs.py), TYPED for a typed value or none
 */
enum class CellKind(override val gameName: String) : GameNamed {
    TYPED(""),
    INITIAL("initial"),
    GUESS("guess"),
    SOLVED("solved"),
}

/** A side of a cell (game/border.py) */
enum class Edge(override val gameName: String) : GameNamed {
    TOP("top"),
    LEFT("left"),
    RIGHT("right"),
    BOTTOM("bottom"),
}

/** What a message is for (game/user_interface.py's MessageKind), NONE for a blank status line */
enum class MessageKind(override val gameName: String) : GameNamed {
    NONE(""),
    INFO("info"),
    WARNING("warning"),
    SUCCESS("success"),
    HINT("hint"),
}
