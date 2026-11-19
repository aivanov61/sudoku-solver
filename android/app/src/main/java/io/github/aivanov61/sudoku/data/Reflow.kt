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

/**
 * The text with each paragraph's lines joined into one, so that a screen can wrap it to its own width: text written
 * for the terminal breaks its lines at about 70 characters.  Paragraphs stay separated by one blank line, and
 * Windows line endings are taken care of too.  An extension function, so it reads `text.reflow()`.
 */
fun String.reflow(): String = this
    .lines()  // splits at \r\n and \n alike
    .joinToString("\n") { it.trim() }  // so a line of only spaces is a blank line
    .split(PARAGRAPH_BREAK)
    .map { it.trim().replace("\n", " ") }
    .filter { it.isNotEmpty() }
    .joinToString("\n\n")

/** One or more blank lines, which end a paragraph */
private val PARAGRAPH_BREAK = Regex("\n{2,}")
