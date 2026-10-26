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
import sys

from dataclasses import dataclass, field

sys.path.insert(0, ".")

from commands import Commands
from puzzle import Puzzle


@dataclass
class PuzzleLayout:
    """A puzzle layout found by the catalog, with anything that keeps it from working fully"""

    name: str
    puzzle_class: type = None
    missing_hooks: list = field(default_factory=list)
    missing_commands: list = field(default_factory=list)

    def is_broken(self) -> bool:
        """Return True if the layout cannot be started at all"""
        return self.puzzle_class is None or bool(self.missing_hooks)

    def has_notes(self) -> bool:
        return any(self.__notes())

    def label(self) -> str:
        """Return the name to show the player, followed by any notes in parentheses"""
        notes = "; ".join(self.__notes())
        return f"{self.name} ({notes})" if notes else self.name

    # Private functions

    def __notes(self):
        if self.puzzle_class is None:
            yield "broken: could not be loaded"
        if self.missing_hooks:
            yield "broken: missing " + ", ".join(self.missing_hooks)
        if self.missing_commands:
            yield "not fully functional, missing: " + ", ".join(self.missing_commands)


class PuzzleCatalog:
    """
    Find the puzzle layouts in the puzzles package.

    A layout is a Puzzle subclass that has its own NAME.  Classes without a NAME, such as base classes
    shared by several layouts, are not listed.
    """

    PACKAGE = "puzzles"

    def available(package=PACKAGE) -> list:
        """Return every layout in the package, sorted by name"""
        modules = [info.name for info in pkgutil.iter_modules(importlib.import_module(package).__path__)]
        layouts = [layout for module_name in modules for layout in PuzzleCatalog.__layouts_in(package, module_name)]
        return sorted(layouts, key=lambda layout: layout.name.lower())

    # Private functions

    def __layouts_in(package, module_name) -> list:
        try:
            module = importlib.import_module(f"{package}.{module_name}")
        except Exception:
            return [PuzzleLayout(f"{module_name}.py")]
        classes = [obj for obj in vars(module).values() if PuzzleCatalog.__is_layout(obj, module)]
        return [PuzzleCatalog.__layout(puzzle_class) for puzzle_class in classes]

    def __is_layout(obj, module) -> bool:
        """A layout is a Puzzle subclass defined in the module itself, with its own NAME"""
        is_puzzle = inspect.isclass(obj) and issubclass(obj, Puzzle)
        return is_puzzle and obj.__module__ == module.__name__ and "NAME" in vars(obj)

    def __layout(puzzle_class) -> PuzzleLayout:
        missing_hooks = sorted(puzzle_class.__abstractmethods__)
        missing_commands = PuzzleCatalog.__missing_commands(puzzle_class)
        return PuzzleLayout(puzzle_class.NAME, puzzle_class, missing_hooks, missing_commands)

    def __missing_commands(puzzle_class) -> list:
        all_commands = {**Commands.COMMON_CMDS, **Commands.INIT_COMMANDS, **Commands.PLAY_COMMANDS}
        return [command for command in all_commands if not hasattr(puzzle_class, PuzzleCatalog.__method_name(command))]

    def __method_name(command) -> str:
        """Return the puzzle method for a command; digits ("#") are entered through value_()"""
        return "value_" if command == "#" else f"{command}_"
