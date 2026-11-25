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

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable

from game.puzzle import Puzzle
from ui.android.auto_save import AutoSave


class Request(ABC):
    """
    What the screen asks of the game, through AndroidUI's requests queue: taken off it by play(), between actions,
    or by a dialog's wait, while the game waits for the player's answer
    """

    @abstractmethod
    def in_play(self, game: Puzzle) -> None:
        """Carry the request out on the game, between actions"""

    @abstractmethod
    def while_waiting(self, game: Puzzle, held: deque[Request]) -> bool | None:
        """
        Carry the request out, or add it to held for play() to carry out after the dialog, while a dialog waits;
        return the player's answer when the request ends the wait, else None
        """


class Act(Request):
    """The player's action, which changes the game, so it waits until no dialog does"""

    def __init__(self, carry_out: Callable[[Puzzle], None]) -> None:
        self.__carry_out = carry_out

    def in_play(self, game: Puzzle) -> None:
        self.__carry_out(game)

    def while_waiting(self, game: Puzzle, held: deque[Request]) -> bool | None:
        held.append(self)
        return None


class Save(Request):
    """A save of the game, carried out at once even while a dialog waits, as Android may end the app at any time"""

    def __init__(self, auto_save: AutoSave) -> None:
        self.__auto_save = auto_save

    def in_play(self, game: Puzzle) -> None:
        self.__auto_save.save(game)

    def while_waiting(self, game: Puzzle, held: deque[Request]) -> bool | None:
        self.in_play(game)
        return None


class Answer(Request):
    """The player's answer to the dialog the game waits on"""

    def __init__(self, yes: bool) -> None:
        self.__yes = yes

    def in_play(self, game: Puzzle) -> None:
        """Drop the answer, as no dialog waits for it (such as a second tap on OK)"""

    def while_waiting(self, game: Puzzle, held: deque[Request]) -> bool | None:
        return self.__yes
