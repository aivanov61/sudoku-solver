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

from game.cell_attrs import Attributes, CellAttrs


class DisplayAttrs:
    """
    The terminal's style table: turns a cell's attributes (see CellAttrs) into "blessed" style names.

    - Primary (at most one per cell)
        - INITIAL - FG=Purple, BG=Lavender
        - GUESS - FG=Green, BG=[shade of gray]
        - SOLVED - FG=LightSkyBlue, BG=[shade of gray]
    - Additional (optional)
        - CONFLICTING - FG=BoldRed, BG=BrightYellow
        - CONFLICTED - FG=[primary], BG=Yellow
    - Guess depth - the shade of gray: GRAY_STEP lighter for each guess, up to the last shade, MAX_GRAY_LEVEL
    - Tagged - the small digits (marks and possible values) in TAGGED_COLOR, on the cell's background
    - Removed - the possible values of a cell that has lost some as ruled out, in REMOVED_VALUES, on the cell's background, even if tagged
    - Ruled out - the values such a cell has lost, in RULED_OUT_DIGITS, on the cell's background
    """

    DEFAULT_COLOR = "darkorange3"
    MISSING_VALUE = "white_on_red"  # a value with no place left, shown in a cell while a warning says so
    GRAY_STEP = 10
    MAX_GRAY_LEVEL = 100  # There are no gray levels greater than 100
    TAGGED_COLOR = "lightskyblue"  # the small digits of a cell the player tagged
    REMOVED_VALUES = "yellow"  # the possible values of a cell that has lost some as ruled out
    RULED_OUT_DIGITS = "red"  # the values a cell has lost as ruled out, shown before those it has left
    HIGHLIGHTED_BORDER = "yellow"  # the outline of a house a message points at, while it is shown
    HIGHLIGHTED_VALUE = "yellow_on_black"  # a value shown where it can still go, in the cells a message points at
    RULED_OUT_VALUE = "white_on_red"  # a value shown where it can't go, in the cells a message points at

    @dataclass
    class FgBgAttr:
        fg: tuple[str, ...] | None = None
        bg: tuple[str, ...] | None = None

    ATTRS_PRIMARY = {
        # The following are mutually exclusive basic required attributes
        CellAttrs.INITIAL: FgBgAttr(("purple",), ("lavender",)),
        CellAttrs.GUESS: FgBgAttr(("green",), None),
        CellAttrs.SOLVED: FgBgAttr(("lightskyblue",), None),
    }

    ATTRS_OPTIONAL = {
        # The following are optional (can be combined with the required ones) but are also mutually exclusive
        CellAttrs.CONFLICTING: FgBgAttr(("bold", "red"), ("bright", "yellow")),
        CellAttrs.CONFLICTED: FgBgAttr(None, ("yellow",)),
    }

    @staticmethod
    def outer_border(_str: str, _attrs: Attributes) -> str:
        """Render outer border attributes - currently no rendering"""
        return _str

    @staticmethod
    def inner_border(_str: str, _attrs: Attributes) -> str:
        """Render inner border attributes - currently no rendering"""
        return _str

    @staticmethod
    def render(_attrs: Attributes) -> str:
        """Render the term.[attr] string for both foreground and background attributes"""
        fg, bg = DisplayAttrs.__get_fg_bg(_attrs)
        return DisplayAttrs.__style(fg, bg)

    @staticmethod
    def render_bg(_attrs: Attributes) -> str:
        """Render the term.[attr] string for only the background attributes"""
        _fg, bg = DisplayAttrs.__get_fg_bg(_attrs)
        return DisplayAttrs.__style(None, bg)

    @staticmethod
    def render_small_digits(_attrs: Attributes, tagged: bool, removed: bool = False) -> str:
        """Render the term.[attr] string for the small digits: the background attributes, in REMOVED_VALUES if removed, else TAGGED_COLOR if tagged"""
        _fg, bg = DisplayAttrs.__get_fg_bg(_attrs)
        tagged_color = DisplayAttrs.TAGGED_COLOR if tagged else None
        return DisplayAttrs.__style(DisplayAttrs.REMOVED_VALUES if removed else tagged_color, bg)

    @staticmethod
    def render_ruled_out_digits(_attrs: Attributes) -> str:
        """Render the term.[attr] string for the small digits of values ruled out: RULED_OUT_DIGITS on the background attributes"""
        _fg, bg = DisplayAttrs.__get_fg_bg(_attrs)
        return DisplayAttrs.__style(DisplayAttrs.RULED_OUT_DIGITS, bg)

    @staticmethod
    def is_beyond_last_shade(depth: int) -> bool:
        """Return True if the guess depth needs a lighter shade of gray than the last one"""
        return depth * DisplayAttrs.GRAY_STEP > DisplayAttrs.MAX_GRAY_LEVEL

    # Private functions

    @staticmethod
    def __get_fg_bg(_attrs: Attributes) -> tuple[str, str]:
        primary = DisplayAttrs.__get_attrs(_attrs, DisplayAttrs.ATTRS_PRIMARY)
        optional = DisplayAttrs.__get_attrs(_attrs, DisplayAttrs.ATTRS_OPTIONAL)
        fg = "_".join(optional.fg or primary.fg or (DisplayAttrs.DEFAULT_COLOR,))
        level = min(DisplayAttrs.__depth(_attrs) * DisplayAttrs.GRAY_STEP, DisplayAttrs.MAX_GRAY_LEVEL)
        bg_level = (f"gray{level}",) if level else ()
        bg = "_".join(optional.bg or primary.bg or bg_level)
        return fg, bg

    @staticmethod
    def __style(fg: str | None, bg: str) -> str:
        return f"{fg}_on_{bg}" if fg and bg else fg if fg else f"on_{bg}" if bg else "normal"

    @staticmethod
    def __depth(_attrs: Attributes) -> int:
        """Return the guess depth, 0 when there is none"""
        return next(iter([attr["depth"] for attr in _attrs if isinstance(attr, dict) and "depth" in attr]), 0)

    @staticmethod
    def __get_attrs(_attrs: Attributes, _attr_list: dict[str, FgBgAttr]) -> FgBgAttr:
        key = next(iter([key for key in _attr_list.keys() if key in _attrs]), None)
        return _attr_list[key] if key else DisplayAttrs.FgBgAttr()
