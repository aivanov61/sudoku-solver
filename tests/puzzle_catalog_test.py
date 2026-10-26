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

import os
import sys
import tempfile
from unittest import main, TestCase

sys.path.insert(0, ".")

from puzzle_catalog import PuzzleCatalog
from puzzles.puzzle_3x3 import Puzzle3x3


class TestPuzzleCatalog(TestCase):
    PACKAGE = "catalog_test_puzzles"
    LAYOUTS = {
        "complete.py": (
            "from puzzles.puzzle_3x3 import Puzzle3x3\n"
            "class Complete(Puzzle3x3):\n"
            "    NAME = 'Complete'\n"
            "    def auto_(self):\n"
            "        pass\n"
        ),
        "partial.py": (
            "from puzzles.puzzle_3x3 import Puzzle3x3\n"
            "class Partial(Puzzle3x3):\n"
            "    NAME = 'Partial'\n"
        ),
        "no_hooks.py": (
            "from puzzle import Puzzle\n"
            "class NoHooks(Puzzle):\n"
            "    NAME = 'No hooks'\n"
        ),
        "intermediate.py": (
            "from puzzle import Puzzle\n"
            "class Intermediate(Puzzle):\n"
            "    pass\n"
        ),
        "bad.py": "this is not python\n",
    }

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        package_dir = os.path.join(self.temp_dir.name, self.PACKAGE)
        os.mkdir(package_dir)
        open(os.path.join(package_dir, "__init__.py"), "w").close()
        for file_name, source in self.LAYOUTS.items():
            with open(os.path.join(package_dir, file_name), "w") as file:
                file.write(source)
        sys.path.insert(0, self.temp_dir.name)
        return super().setUp()

    def tearDown(self):
        sys.path.remove(self.temp_dir.name)
        for module_name in [name for name in sys.modules if name.startswith(self.PACKAGE)]:
            del sys.modules[module_name]
        self.temp_dir.cleanup()
        return super().tearDown()

    def test_real_layouts_include_the_standard_puzzle(self):
        layouts = PuzzleCatalog.available()
        self.assertEqual([layout.puzzle_class for layout in layouts], [Puzzle3x3])

    def test_layouts_are_listed_by_name_with_their_notes(self):
        self.assertEqual(
            self.__labels(),
            [
                "bad.py (broken: could not be loaded)",
                "Complete",
                "No hooks (broken: missing _block_at, _blocks; not fully functional, missing: auto)",
                "Partial (not fully functional, missing: auto)",
            ],
        )

    def test_layout_that_cannot_be_loaded_is_broken(self):
        self.assertTrue(self.__layout("bad.py").is_broken())

    def test_layout_missing_a_hook_is_broken(self):
        self.assertTrue(self.__layout("No hooks").is_broken())

    def test_layout_missing_only_commands_is_not_broken(self):
        self.assertFalse(self.__layout("Partial").is_broken())

    def test_layout_class_is_available_for_loaded_layouts(self):
        self.assertEqual(self.__layout("Complete").puzzle_class.__name__, "Complete")

    # Private functions

    def __labels(self):
        return [layout.label() for layout in PuzzleCatalog.available(self.PACKAGE)]

    def __layout(self, name):
        return next(layout for layout in PuzzleCatalog.available(self.PACKAGE) if layout.name == name)


if __name__ == "__main__":
    main()
