# Copyright (C) 2018-2019 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.


from copy import copy
from functools import total_ordering
from typing import Any

from libversion import ANY_IS_PATCH, P_IS_PATCH, version_compare

from repology.package import Package, PackageFlags


@total_ordering
class UserVisibleVersionInfo:
    __slots__ = ['version', 'versionclass', 'metaorder', 'versionflags', 'spread']

    version: str
    versionclass: int
    metaorder: int
    spread: int

    def __init__(self, package: Package, spread: int = 1) -> None:
        self.version = package.version
        self.versionclass = package.versionclass

        self.metaorder = PackageFlags.get_metaorder(package.flags)
        self.versionflags = (((package.flags & PackageFlags.P_IS_PATCH) and P_IS_PATCH) |
                             ((package.flags & PackageFlags.ANY_IS_PATCH) and ANY_IS_PATCH))

        self.spread = spread

    def as_with_spread(self, spread: int) -> 'UserVisibleVersionInfo':
        result = copy(self)
        result.spread = spread
        return result

    def __eq__(self, other: Any) -> bool:
        return (self.metaorder == other.metaorder and
                self.versionclass == other.versionclass and
                self.version == other.version and
                version_compare(self.version, other.version, self.versionflags, other.versionflags) == 0 and
                self.spread == other.spread)

    def __lt__(self, other: 'UserVisibleVersionInfo') -> bool:
        if self.metaorder < other.metaorder:
            return True
        if self.metaorder > other.metaorder:
            return False

        res = version_compare(
            self.version,
            other.version,
            self.versionflags,
            other.versionflags
        )

        if res < 0:
            return True
        if res > 0:
            return False

        if self.versionclass < other.versionclass:
            return True
        if self.versionclass > other.versionclass:
            return False

        if self.spread < other.spread:
            return True
        if self.spread > other.spread:
            return False

        return self.version < other.version

    def __hash__(self) -> int:
        return hash((self.metaorder, self.versionclass, self.version, self.spread))
