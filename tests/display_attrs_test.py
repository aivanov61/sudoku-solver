# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

import sys

sys.path.insert(0, ".")

from unittest import main, TestCase

from display_attrs import DisplayAttrs


class TestDisplayRenderAttrs(TestCase):
    """No test cases for outer_border()/inner_border() since they currently do not render anything"""

    def test_no_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render(dict())
        self.assertEqual(out, "normal")

    def test_unrecognized_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render(dict(junk1="junk", junk2=("JUNK"), junk3=DisplayAttrs.FgBgAttr(("blue"), ("red"))))
        self.assertEqual(out, "normal")

    def test_initial_attribute_renders_purple_on_lavender(self):
        out = DisplayAttrs.render(DisplayAttrs.INITIAL)
        self.assertEqual(out, "purple_on_lavender")

        t = (DisplayAttrs.INITIAL, "junk")
        out = DisplayAttrs.render(t)
        self.assertEqual(out, "purple_on_lavender")

    def test_guess_attribute_renders_green(self):
        out = DisplayAttrs.render(DisplayAttrs.GUESS)
        self.assertEqual(out, "green")

    def test_level_attribute_that_is_not_a_dict_is_ignored(self):
        out = DisplayAttrs.render("level")
        self.assertEqual(out, "normal")

    def test_level_attribute_combined_with_non_dict_level_works_properly(self):
        out = DisplayAttrs.render(("level", dict(level=50)))
        self.assertEqual(out, "on_gray50")

        out = DisplayAttrs.render((dict(level=50), "level"))
        self.assertEqual(out, "on_gray50")

        out = DisplayAttrs.render(("level", dict(level=50), "level"))
        self.assertEqual(out, "on_gray50")

    def test_level75_attribute_with_guess_renders_green_on_gray75(self):
        out = DisplayAttrs.render((DisplayAttrs.GUESS, dict(level=75)))
        self.assertEqual(out, "green_on_gray75")

    def test_conflicting_value_renders_boldred_on_yellow(self):
        out = DisplayAttrs.render(DisplayAttrs.CONFLICTING)
        self.assertEqual(out, "boldred_on_yellow")

        out = DisplayAttrs.render((DisplayAttrs.INITIAL, DisplayAttrs.CONFLICTING))
        self.assertEqual(out, "boldred_on_yellow")

        out = DisplayAttrs.render((DisplayAttrs.GUESS, DisplayAttrs.CONFLICTING, dict(level=75)))
        self.assertEqual(out, "boldred_on_yellow")

    def test_conflicted_value_renders_primary_on_yellow(self):
        out = DisplayAttrs.render(DisplayAttrs.CONFLICTED)
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render((DisplayAttrs.CONFLICTED, DisplayAttrs.INITIAL))
        self.assertEqual(out, "purple_on_yellow")

        out = DisplayAttrs.render((DisplayAttrs.CONFLICTED, DisplayAttrs.GUESS, dict(level=25)))
        self.assertEqual(out, "green_on_yellow")


class TestDisplayRenderBgAttrs(TestCase):
    def test_no_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render_bg(dict())
        self.assertEqual(out, "normal")

    def test_unrecognized_attributes_renders_normal_terminal_output(self):
        out = DisplayAttrs.render_bg(dict(junk1="junk", junk2=("JUNK"), junk3=DisplayAttrs.FgBgAttr(("blue"), ("red"))))
        self.assertEqual(out, "normal")

    def test_guess_attribute_renders_the_right_level_of_gray(self):
        out = DisplayAttrs.render_bg(DisplayAttrs.GUESS)
        self.assertEqual(out, "normal")

        out = DisplayAttrs.render_bg((DisplayAttrs.GUESS, dict(level=60)))
        self.assertEqual(out, "on_gray60")

    def test_initial_attribute_renders_lavender(self):
        out = DisplayAttrs.render_bg(DisplayAttrs.INITIAL)
        self.assertEqual(out, "on_lavender")

        out = DisplayAttrs.render_bg((DisplayAttrs.INITIAL, dict(level=60)))
        self.assertEqual(out, "on_lavender")

    def test_conflicting_value_renders_yellow(self):
        out = DisplayAttrs.render_bg(DisplayAttrs.CONFLICTING)
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render_bg((DisplayAttrs.INITIAL, DisplayAttrs.CONFLICTING))
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render_bg((DisplayAttrs.GUESS, DisplayAttrs.CONFLICTING, dict(level=75)))
        self.assertEqual(out, "on_yellow")

    def test_conflicted_value_renders_yellow(self):
        out = DisplayAttrs.render_bg(DisplayAttrs.CONFLICTED)
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render_bg((DisplayAttrs.CONFLICTED, DisplayAttrs.INITIAL))
        self.assertEqual(out, "on_yellow")

        out = DisplayAttrs.render_bg((DisplayAttrs.CONFLICTED, DisplayAttrs.GUESS, dict(level=25)))
        self.assertEqual(out, "on_yellow")


main()
