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

from dataclasses import dataclass

from game.cell_attrs import CellAttrs


class DisplayAttrs:
    """
    The terminal's style table: turns a cell's attributes (see CellAttrs) into "blessed" style names.

    - Primary (at most one per cell)
        - INITIAL - FG=Purple, BG=Lavender
        - GUESS - FG=Green, BG=[shade of gray]
        - SOLVED - FG=SteelBlue, BG=[shade of gray]
    - Additional (optional)
        - CONFLICTING - FG=BoldRed, BG=BrightYellow
        - CONFLICTED - FG=[primary], BG=Yellow
    - Guess depth - the shade of gray: GRAY_STEP lighter for each guess, up to the last shade, MAX_GRAY_LEVEL
    """

    DEFAULT_COLOR = "darkorange3"
    GRAY_STEP = 10
    MAX_GRAY_LEVEL = 100  # There are no gray levels greater than 100

    @dataclass
    class FgBgAttr:
        fg: tuple = None
        bg: tuple = None

    ATTRS_PRIMARY = {
        # The following are mutually exclusive basic required attributes
        CellAttrs.INITIAL: FgBgAttr(("purple",), ("lavender",)),
        CellAttrs.GUESS: FgBgAttr(("green",), None),
        CellAttrs.SOLVED: FgBgAttr(("steelblue",), None),
    }

    ATTRS_OPTIONAL = {
        # The following are optional (can be combined with the required ones) but are also mutually exclusive
        CellAttrs.CONFLICTING: FgBgAttr(("bold", "red"), ("bright", "yellow")),
        CellAttrs.CONFLICTED: FgBgAttr(None, ("yellow",)),
    }

    def outer_border(_str, _attrs):
        """Render outer border attributes - currently no rendering"""
        return _str

    def inner_border(_str, _attrs):
        """Render inner border attributes - currently no rendering"""
        return _str

    def render(_attrs: tuple[str]) -> str:
        """Render the term.[attr] string for both foreground and background attributes"""
        fg, bg = DisplayAttrs.__get_fg_bg(_attrs)
        return f"{fg}_on_{bg}" if fg and bg else fg if fg else f"on_{bg}" if bg else "normal"

    def render_bg(_attrs) -> str:
        """Render the term.[attr] string for only the background attributes"""
        fg, bg = DisplayAttrs.__get_fg_bg(_attrs)
        return f"on_{bg}" if bg else "normal"

    def is_beyond_last_shade(depth) -> bool:
        """Return True if the guess depth needs a lighter shade of gray than the last one"""
        return depth * DisplayAttrs.GRAY_STEP > DisplayAttrs.MAX_GRAY_LEVEL

    # Private functions

    def __get_fg_bg(_attrs):
        primary = DisplayAttrs.__get_attrs(_attrs, DisplayAttrs.ATTRS_PRIMARY)
        optional = DisplayAttrs.__get_attrs(_attrs, DisplayAttrs.ATTRS_OPTIONAL)
        fg = "_".join(optional.fg or primary.fg or (DisplayAttrs.DEFAULT_COLOR,))
        level = min(DisplayAttrs.__depth(_attrs) * DisplayAttrs.GRAY_STEP, DisplayAttrs.MAX_GRAY_LEVEL)
        bg_level = (f"gray{level}",) if level else ()
        bg = "_".join(optional.bg or primary.bg or bg_level)
        return fg, bg

    def __depth(_attrs) -> int:
        """Return the guess depth, 0 when there is none"""
        return next(iter([attr["depth"] for attr in _attrs if isinstance(attr, dict) and "depth" in attr]), 0)

    def __get_attrs(_attrs, _attr_list) -> FgBgAttr:
        key = next(iter([key for key in _attr_list.keys() if key in _attrs]), None)
        return _attr_list[key] if key else DisplayAttrs.FgBgAttr()
