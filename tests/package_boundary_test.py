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

import ast
import sys
from pathlib import Path
from unittest import main, TestCase

sys.path.insert(0, ".")


class TestPackageBoundary(TestCase):
    """The game knows nothing about how it is shown: nothing in game/ imports a user interface or a terminal library"""

    SHOWING = ("ui", "blessed")

    def test_no_game_module_imports_a_user_interface(self):
        modules = sorted(Path("game").rglob("*.py"))
        self.assertGreater(len(modules), 0)
        offenders = [f"{path}: {name}" for path in modules for name in self.__imports(path) if self.__is_showing(name)]
        self.assertEqual(offenders, [])

    # Private functions

    def __imports(self, path) -> list:
        """The names of the modules the file imports"""
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        return imports + [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]

    def __is_showing(self, name) -> bool:
        return name.split(".")[0] in self.SHOWING


if __name__ == "__main__":
    main()
