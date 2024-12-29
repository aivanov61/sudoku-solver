# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
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

    # Initial background level is black (no guess), increases the more guesses are made
    bg_level = 0

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
        fg = "".join(optional.fg or primary.fg or ())
        level = next(iter([attr["level"] for attr in _attrs if isinstance(attr, dict) and "level" in attr]), None)
        bg_level = f"gray{level}" if level else ()
        bg = "".join(optional.bg or primary.bg or bg_level)
        return fg, bg

    def __get_attrs(_attrs, _attr_list) -> FgBgAttr:
        key = next(iter([key for key in _attr_list.keys() if key in _attrs]), None)
        return _attr_list[key] if key else DisplayAttrs.FgBgAttr()
