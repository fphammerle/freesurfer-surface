# freesurfer-surface - Read and Write Surface Files in Freesurfer’s TriangularSurface Format
#
# Copyright (C) 2020 Fabian Peter Hammerle <fabian@hammerle.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest

from freesurfer_surface import LineSegment


def test_init_fail():
    with pytest.raises(Exception):
        LineSegment((1, 2, 3))


def test_eq():
    assert LineSegment((67018, 67019)) == LineSegment((67018, 67019))
    assert LineSegment((67018, 67019)) == LineSegment((67019, 67018))
    assert LineSegment((67019, 67018)) == LineSegment((67018, 67019))


def test_repr():
    assert (
        repr(LineSegment((67018, 67019)))
        == "LineSegment(vertex_indices=(67018, 67019))"
    )


def test_adjacent_vertex_indices_1():
    chain = LineSegment((1, 4))
    singles = list(chain.adjacent_vertex_indices(1))
    assert len(singles) == 2
    assert singles[0] == (1,)
    assert singles[1] == (4,)


def test_adjacent_vertex_indices_2():
    chain = LineSegment((1, 4))
    pairs = list(chain.adjacent_vertex_indices(2))
    assert len(pairs) == 2
    assert pairs[0] == (1, 4)
    assert pairs[1] == (4, 1)


def test_adjacent_vertex_indices_3():
    chain = LineSegment((1, 4))
    triplets = list(chain.adjacent_vertex_indices(3))
    assert len(triplets) == 2
    assert triplets[0] == (1, 4, 1)
    assert triplets[1] == (4, 1, 4)
