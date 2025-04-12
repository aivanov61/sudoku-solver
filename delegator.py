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


class Delegator:
    """
    A generic delegator class that delegates specific method calls to one or more target objects.

    Attributes:
        _delegate_targets: A dictionary where keys are target objects and values are lists of method names
                           to be delegated to each target.
    """

    def __init__(self, delegate_targets):
        """
        Initialize the Delegator with multiple delegate targets.

        Args:
            delegate_targets (dict): A dictionary where keys are target objects and values are lists of
                                     method names to be delegated to each target.
        """
        self._delegate_targets = delegate_targets

    def __getattr__(self, name):
        """
        Delegate attribute access to the appropriate target object if the attribute
        is in the list of methods to be delegated for that target.
        """
        for target, methods in self._delegate_targets.items():
            if name in methods:
                return getattr(target, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
