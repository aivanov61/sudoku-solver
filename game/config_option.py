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

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ConfigOption:
    """
    A setting the player can configure: the group it is listed under, its name, the choices it offers as
    (label, value) pairs, the value chosen, and optionally a note explaining each choice.  A note can name the
    key for an action as {key}, since only the user interface knows which key that is.
    """

    group: str
    name: str
    choices: tuple  # (label, value) for each choice, in the order offered
    value: object
    notes: tuple = ()  # a note for each choice, in the same order ("" for none), or none at all
    note_action: object = None  # the Action whose key the notes name as {key}

    def labels(self) -> list:
        return [label for label, _ in self.choices]

    def chosen_index(self) -> int:
        return [value for _, value in self.choices].index(self.value)

    def with_choice(self, index) -> "ConfigOption":
        """Return the option with the choice at index chosen"""
        return replace(self, value=self.choices[index][1])
