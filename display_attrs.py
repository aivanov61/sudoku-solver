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


class DisplayAttrs:
    """
    Use display attribute mnemonics to produce properly rendered "blessed" function names.

    Valid Mnemonics are:
    - Primary (at most one is allowed per cell)
        - INITIAL - FG=Purple, BG=Lavender
        - GUESS - FG=Green, BG=[shade of gray]
    - Additional (optional)
        - CONFLICTING - FG=BoldRed, BG=Yellow
        - CONFLICTED - FG=[primary], BG=Yellow
    """

    INITIAL = "initial"
    GUESS = "guess"
    CONFLICTING = "conflicting"
    CONFLICTED = "conflicted"

    DEFAULT_COLOR = "darkorange3"

    @dataclass
    class FgBgAttr:
        fg: tuple = None
        bg: tuple = None

    ATTRS_PRIMARY = {
        # The following are mutually exclusive basic required attributes
        INITIAL: FgBgAttr(("purple"), ("lavender")),
        GUESS: FgBgAttr(("green"), None),
    }

    ATTRS_OPTIONAL = {
        # The following are optional (can be combined with the required ones) but are also mutually exclusive
        CONFLICTING: FgBgAttr(("bold", "red"), ("yellow")),
        CONFLICTED: FgBgAttr(None, ("yellow")),
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

    def __get_fg_bg(_attrs):
        primary = DisplayAttrs.__get_attrs(_attrs, DisplayAttrs.ATTRS_PRIMARY)
        optional = DisplayAttrs.__get_attrs(_attrs, DisplayAttrs.ATTRS_OPTIONAL)
        fg = "".join(optional.fg or primary.fg or DisplayAttrs.DEFAULT_COLOR)
        level = next(iter([attr["level"] for attr in _attrs if isinstance(attr, dict) and "level" in attr]), None)
        level = min(level, 100) if level else None  # There are no gray levels greater than 100
        bg_level = f"gray{level}" if level else ()
        bg = "".join(optional.bg or primary.bg or bg_level)
        return fg, bg

    def __get_attrs(_attrs, _attr_list) -> FgBgAttr:
        key = next(iter([key for key in _attr_list.keys() if key in _attrs]), None)
        return _attr_list[key] if key else DisplayAttrs.FgBgAttr()
