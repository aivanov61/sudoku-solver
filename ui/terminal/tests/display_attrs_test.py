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

sys.path.insert(0, ".")

from unittest import main, TestCase

from game.cell_attrs import CellAttrs
from ui.terminal.display_attrs import DisplayAttrs


class TestDisplayRenderAttrs(TestCase):
    """No test cases for outer_border()/inner_border() since they currently do not render anything"""

    def test_no_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render(dict())
        self.assertEqual(out, DisplayAttrs.DEFAULT_COLOR)

    def test_unrecognized_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render(dict(junk1="junk", junk2=("JUNK"), junk3=DisplayAttrs.FgBgAttr(("blue"), ("red"))))
        self.assertEqual(out, DisplayAttrs.DEFAULT_COLOR)

    def test_initial_attribute_renders_purple_on_lavender(self):
        out = DisplayAttrs.render(CellAttrs.INITIAL)
        self.assertEqual(out, "purple_on_lavender")

        t = (CellAttrs.INITIAL, "junk")
        out = DisplayAttrs.render(t)
        self.assertEqual(out, "purple_on_lavender")

    def test_solved_attribute_renders_steelblue(self):
        self.assertEqual(DisplayAttrs.render(CellAttrs.SOLVED), "steelblue")

    def test_solved_attribute_keeps_the_guess_shading(self):
        self.assertEqual(DisplayAttrs.render((CellAttrs.SOLVED, dict(depth=1))), "steelblue_on_gray10")

    def test_guess_attribute_renders_green(self):
        out = DisplayAttrs.render(CellAttrs.GUESS)
        self.assertEqual(out, "green")

    def test_depth_attribute_that_is_not_a_dict_is_ignored(self):
        out = DisplayAttrs.render("depth")
        self.assertEqual(out, DisplayAttrs.DEFAULT_COLOR)

    def test_depth_attribute_combined_with_non_dict_depth_works_properly(self):
        out = DisplayAttrs.render(("depth", dict(depth=5)))
        self.assertEqual(out, f"{DisplayAttrs.DEFAULT_COLOR}_on_gray50")

        out = DisplayAttrs.render((dict(depth=5), "depth"))
        self.assertEqual(out, f"{DisplayAttrs.DEFAULT_COLOR}_on_gray50")

        out = DisplayAttrs.render(("depth", dict(depth=5), "depth"))
        self.assertEqual(out, f"{DisplayAttrs.DEFAULT_COLOR}_on_gray50")

    def test_guess_seven_deep_renders_green_on_gray70(self):
        out = DisplayAttrs.render((CellAttrs.GUESS, dict(depth=7)))
        self.assertEqual(out, "green_on_gray70")

    def test_guess_deeper_than_the_last_shade_renders_the_last_shade(self):
        out = DisplayAttrs.render((CellAttrs.GUESS, dict(depth=12)))
        self.assertEqual(out, "green_on_gray100")

    def test_only_a_depth_beyond_the_last_shade_runs_out_of_shades(self):
        self.assertFalse(DisplayAttrs.is_beyond_last_shade(0))
        self.assertFalse(DisplayAttrs.is_beyond_last_shade(10))
        self.assertTrue(DisplayAttrs.is_beyond_last_shade(11))

    def test_conflicting_value_renders_bold_red_on_bright_yellow(self):
        out = DisplayAttrs.render(CellAttrs.CONFLICTING)
        self.assertEqual(out, "bold_red_on_bright_yellow")

        out = DisplayAttrs.render((CellAttrs.INITIAL, CellAttrs.CONFLICTING))
        self.assertEqual(out, "bold_red_on_bright_yellow")

        out = DisplayAttrs.render((CellAttrs.GUESS, CellAttrs.CONFLICTING, dict(depth=7)))
        self.assertEqual(out, "bold_red_on_bright_yellow")

    def test_conflicted_value_renders_primary_on_yellow(self):
        out = DisplayAttrs.render(CellAttrs.CONFLICTED)
        self.assertEqual(out, f"{DisplayAttrs.DEFAULT_COLOR}_on_yellow")

        out = DisplayAttrs.render((CellAttrs.CONFLICTED, CellAttrs.INITIAL))
        self.assertEqual(out, "purple_on_yellow")

        out = DisplayAttrs.render((CellAttrs.CONFLICTED, CellAttrs.GUESS, dict(depth=2)))
        self.assertEqual(out, "green_on_yellow")


class TestDisplayRenderBgAttrs(TestCase):
    def test_no_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render_bg(dict())
        self.assertEqual(out, "normal")

    def test_unrecognized_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render_bg(dict(junk1="junk", junk2=("JUNK"), junk3=DisplayAttrs.FgBgAttr(("blue"), ("red"))))
        self.assertEqual(out, "normal")

    def test_solved_attribute_has_no_background_of_its_own(self):
        self.assertEqual(DisplayAttrs.render_bg(CellAttrs.SOLVED), "normal")

    def test_guess_attribute_renders_the_gray_for_its_depth(self):
        out = DisplayAttrs.render_bg(CellAttrs.GUESS)
        self.assertEqual(out, "normal")

        out = DisplayAttrs.render_bg((CellAttrs.GUESS, dict(depth=6)))
        self.assertEqual(out, "on_gray60")

    def test_initial_attribute_renders_lavender(self):
        out = DisplayAttrs.render_bg(CellAttrs.INITIAL)
        self.assertEqual(out, "on_lavender")

        out = DisplayAttrs.render_bg((CellAttrs.INITIAL, dict(depth=6)))
        self.assertEqual(out, "on_lavender")

    def test_conflicting_value_renders_bright_yellow(self):
        out = DisplayAttrs.render_bg(CellAttrs.CONFLICTING)
        self.assertEqual(out, "on_bright_yellow")

        out = DisplayAttrs.render_bg((CellAttrs.INITIAL, CellAttrs.CONFLICTING))
        self.assertEqual(out, "on_bright_yellow")

        out = DisplayAttrs.render_bg((CellAttrs.GUESS, CellAttrs.CONFLICTING, dict(depth=7)))
        self.assertEqual(out, "on_bright_yellow")

    def test_conflicted_value_renders_yellow(self):
        out = DisplayAttrs.render_bg(CellAttrs.CONFLICTED)
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render_bg((CellAttrs.CONFLICTED, CellAttrs.INITIAL))
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render_bg((CellAttrs.CONFLICTED, CellAttrs.GUESS, dict(depth=2)))
        self.assertEqual(out, "on_yellow")


if __name__ == "__main__":
    main()
