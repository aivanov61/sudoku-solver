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

class RecordingUI:
    """
    A user interface for tests: it records what the game shows and answers the game's questions as told.
    """

    def __init__(self, confirms=True, file_name=None):
        self.confirms = confirms  # the answer to every confirm()
        self.file_name = file_name  # the answer to every ask_file_name()
        self.statuses = []  # every message shown with status(), None for a blank status line
        self.informed = []  # every message shown with inform()
        self.questions = []  # every question asked with confirm(), and (prompt, default, extension) for each ask_file_name()
        self.guess_depths = []  # every guess depth reported
        self.shown_boards = []  # the cells of every board shown whole
        self.changed_cells = []  # every cell reported changed
        self.modes = []  # (mode, offered actions) for every mode announced

    # Interface required for the game

    def status(self, message) -> None:
        self.statuses.append(message)

    def inform(self, message) -> None:
        self.informed.append(message)

    def confirm(self, question) -> bool:
        self.questions.append(question)
        return self.confirms

    def ask_file_name(self, prompt, default, extension) -> str:
        self.questions.append((prompt, default, extension))
        return self.file_name

    def guess_depth_changed(self, depth) -> None:
        self.guess_depths.append(depth)

    def show_board(self, cells) -> None:
        self.shown_boards.append(list(cells))

    def cell_changed(self, cell) -> None:
        self.changed_cells.append(cell)

    def mode_changed(self, mode, actions) -> None:
        self.modes.append((mode, actions))

    # Interface required for tests

    def last_status(self) -> str:
        """Return the text the status line shows now, "" when it is blank"""
        message = self.statuses[-1] if self.statuses else None
        return message.text if message else ""

    def last_informed(self) -> str:
        """Return the text of the last message shown with inform(), or None"""
        return self.informed[-1].text if self.informed else None
