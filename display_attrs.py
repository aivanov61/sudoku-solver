# -----------------------------------------------------------------------------
# Copyright (c) by Anton Ivanov.
# This information is the confidential and proprietary property of Anton Ivanov
# and the possession or use of this file requires a written license from him.
# -----------------------------------------------------------------------------

class DisplayAttrs:
    def outer_border(str, attrs):
        """Render outer border attributes - currently no rendering"""
        return str

    def inner_border(str, attrs):
        """Render inner border attributes - currently no rendering"""
        return str

    def render(str, attrs):
        """Render both foreground and background attributes"""
        return str

    def render_bg(str, attrs):
        """Render only the background attributes"""
        return str