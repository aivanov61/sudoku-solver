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

import importlib
import inspect
import pkgutil

from collections.abc import Iterator
from dataclasses import dataclass, field
from types import ModuleType

from game.board import Board


@dataclass
class PuzzleLayout:
    """A puzzle layout found by the catalog, with anything that keeps it from working"""

    name: str
    board_class: type[Board] | None = None
    missing_hooks: list[str] = field(default_factory=list)

    def is_broken(self) -> bool:
        """Return True if the layout cannot be started at all"""
        return self.board_class is None or bool(self.missing_hooks)

    def has_notes(self) -> bool:
        return any(self.__notes())

    def label(self) -> str:
        """Return the name to show the player, followed by any notes in parentheses"""
        notes = "; ".join(self.__notes())
        return f"{self.name} ({notes})" if notes else self.name

    def board(self) -> Board:
        """Return a new board of the layout, which must not be broken"""
        assert self.board_class is not None, "a layout that could not be loaded has no board"
        return self.board_class()  # pyright: ignore[reportCallIssue]  # every layout is made with no arguments, unlike Board itself

    # Private functions

    def __notes(self) -> Iterator[str]:
        if self.board_class is None:
            yield "broken: could not be loaded"
        if self.missing_hooks:
            yield "broken: missing " + ", ".join(self.missing_hooks)


class PuzzleCatalog:
    """
    Find the puzzle layouts in the puzzles package.

    A layout is a Board subclass that has its own NAME.  Classes without a NAME, such as base classes
    shared by several layouts, are not listed.
    """

    PACKAGE = "game.puzzles"

    @staticmethod
    def available(package: str = PACKAGE) -> list[PuzzleLayout]:
        """Return every layout in the package, sorted by name"""
        modules = [info.name for info in pkgutil.iter_modules(importlib.import_module(package).__path__)]
        layouts = [layout for module_name in modules for layout in PuzzleCatalog.__layouts_in(package, module_name)]
        return sorted(layouts, key=lambda layout: layout.name.lower())

    # Private functions

    @staticmethod
    def __layouts_in(package: str, module_name: str) -> list[PuzzleLayout]:
        try:
            module = importlib.import_module(f"{package}.{module_name}")
        except Exception:
            return [PuzzleLayout(f"{module_name}.py")]
        classes = [obj for obj in vars(module).values() if PuzzleCatalog.__is_layout(obj, module)]
        return [PuzzleCatalog.__layout(board_class) for board_class in classes]

    @staticmethod
    def __is_layout(obj: object, module: ModuleType) -> bool:
        """A layout is a Board subclass defined in the module itself, with its own NAME"""
        is_board = inspect.isclass(obj) and issubclass(obj, Board)
        return is_board and obj.__module__ == module.__name__ and "NAME" in vars(obj)

    @staticmethod
    def __layout(board_class: type[Board]) -> PuzzleLayout:
        return PuzzleLayout(board_class.NAME, board_class, sorted(board_class.__abstractmethods__))
