# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import sys
from unittest import main, TestCase

sys.path.insert(0, ".")

from ui.terminal.menu_choice import MenuChoice
from ui.terminal.menu_note import MenuNote


class TestMenuNote(TestCase):
    def setUp(self):
        self.choice = MenuChoice("Size", ["small", "medium", "large"])
        self.note = MenuNote(self.choice, ["Fits anywhere", "", "Needs room"])
        return super().setUp()

    def test_shows_the_note_for_the_choice_made(self):
        self.assertEqual(self.note.text(), "Fits anywhere")
        self.choice.handle("KEY_LEFT")
        self.assertEqual(self.note.text(), "Needs room")

    def test_a_choice_without_a_note_leaves_the_line_blank(self):
        self.choice.handle("KEY_RIGHT")
        self.assertEqual(self.note.text(), "")

    def test_is_grayed_out_and_never_selected(self):
        self.assertEqual((self.note.is_grayed_out(), self.note.is_selectable()), (True, False))

    def test_is_indented_under_its_choice(self):
        self.assertTrue(self.note.INDENT.startswith(MenuChoice.INDENT))
        self.assertGreater(len(self.note.INDENT), len(MenuChoice.INDENT))


if __name__ == "__main__":
    main()
