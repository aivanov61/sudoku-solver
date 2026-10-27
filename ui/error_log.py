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
import traceback

from datetime import datetime


class ErrorLog:
    """
    Keep the details of errors the program survives: each error's traceback is appended to FILE, followed by a
    blank line to set it apart from the next, so that a user interface can show a short message and point to
    the details.
    """

    FILE = "sudoku.log"

    def record(error) -> str:
        """Append the time and the error's traceback to the log; return the log's file name, or None if it can't be written"""
        try:
            with open(ErrorLog.FILE, "a", encoding="utf-8") as log:
                log.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S}\n")
                log.write("".join(traceback.format_exception(error)))
                log.write("\n")
        except OSError:
            return None
        return ErrorLog.FILE

    def where(error) -> str:
        """Return the innermost place on the error's stack, e.g. "game/puzzle.py:123 in up_" """
        frame = traceback.extract_tb(error.__traceback__)[-1]
        return f"{os.path.relpath(frame.filename)}:{frame.lineno} in {frame.name}"
