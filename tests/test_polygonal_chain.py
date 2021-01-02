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

from freesurfer_surface import (
    LineSegment,
    PolygonalChain,
    PolygonalChainsNotOverlapingError,
)


def test_init():
    chain = PolygonalChain((0, 21, 42, 84))
    assert tuple(chain.vertex_indices) == (0, 21, 42, 84)


def test_reassign_vertex_indices():
    chain = PolygonalChain((0, 21, 42, 84))
    chain.vertex_indices = (1, 2, 3, 4)
    assert tuple(chain.vertex_indices) == (1, 2, 3, 4)


@pytest.mark.parametrize(
    ("indices_init", "indices_normalized"),
    (
        ([0, 3], [0, 3]),
        ([3, 0], [0, 3]),
        ([0, 3, 2, 4], [0, 3, 2, 4]),
        ([0, 4, 2, 3], [0, 3, 2, 4]),
        ([2, 3, 0, 4], [0, 3, 2, 4]),
        ([2, 4, 0, 3], [0, 3, 2, 4]),
        ([3, 0, 4, 2], [0, 3, 2, 4]),
        ([3, 2, 4, 0], [0, 3, 2, 4]),
        ([4, 0, 3, 2], [0, 3, 2, 4]),
        ([4, 2, 3, 0], [0, 3, 2, 4]),
    ),
)
def test_normalized(indices_init, indices_normalized):
    assert (
        list(PolygonalChain(indices_init).normalized().vertex_indices)
        == indices_normalized
    )


def test_eq():
    assert PolygonalChain((0, 1, 2)) == PolygonalChain((0, 1, 2))
    # pylint: disable=unneeded-not
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((0, 1, 4))
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((0, 4, 2))
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((4, 1, 2))
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((1, 2, 3, 4))


def test_eq_normalized():
    assert PolygonalChain((0, 1, 2)) == PolygonalChain((0, 2, 1))
    assert PolygonalChain((1, 0, 2)) == PolygonalChain((0, 2, 1))
    assert PolygonalChain((1, 0, 2, 4)) == PolygonalChain((0, 1, 4, 2))
    # pylint: disable=unneeded-not
    assert not PolygonalChain((1, 0, 2, 4)) == PolygonalChain((0, 1, 2, 4))


def test_repr():
    assert repr(PolygonalChain([])) == "PolygonalChain(vertex_indices=())"
    assert repr(PolygonalChain((0, 2, 1))) == "PolygonalChain(vertex_indices=(0, 2, 1))"
    assert (
        repr(PolygonalChain((0, 2, 1, 4, 3)))
        == "PolygonalChain(vertex_indices=(0, 2, 1, 4, 3))"
    )


@pytest.mark.parametrize(
    ("vertex_indices_a", "vertex_indices_b", "expected_vertex_indices"),
    [
        ((1, 2, 3), (3, 4), (1, 2, 3, 4)),
        ((1, 2, 3), (4, 3), (1, 2, 3, 4)),
        ((3, 2, 1), (3, 4), (4, 3, 2, 1)),
        ((3, 2, 1), (4, 3), (4, 3, 2, 1)),
        ((1,), (1,), (1,)),
        ((1, 2), (1,), (1, 2)),
        ((1, 2), (2,), (1, 2)),
        ((0, 3, 1, 5, 2), (3, 5, 2, 0), (3, 5, 2, 0, 3, 1, 5, 2)),
        ((98792, 98807, 98821), (98792, 98793), (98793, 98792, 98807, 98821)),
    ],
)
def test_connect(vertex_indices_a, vertex_indices_b, expected_vertex_indices):
    chain = PolygonalChain(vertex_indices_a)
    chain.connect(PolygonalChain(vertex_indices_b))
    assert PolygonalChain(expected_vertex_indices) == chain


@pytest.mark.parametrize(
    ("vertex_indices_a", "vertex_indices_b"), [((1, 2, 3), (2, 4))]
)
def test_connect_fail(vertex_indices_a, vertex_indices_b):
    chain = PolygonalChain(vertex_indices_a)
    with pytest.raises(PolygonalChainsNotOverlapingError):
        chain.connect(PolygonalChain(vertex_indices_b))


@pytest.mark.parametrize(
    ("vertex_indices_a", "vertex_indices_b"), [((1, 2, 3), ()), ((), (3, 4))]
)
def test_connect_fail_empty(vertex_indices_a, vertex_indices_b):
    chain = PolygonalChain(vertex_indices_a)
    with pytest.raises(Exception):
        chain.connect(PolygonalChain(vertex_indices_b))


def test_adjacent_vertex_indices_1():
    chain = PolygonalChain((0, 1, 4, 8))
    pairs = list(chain.adjacent_vertex_indices(1))
    assert len(pairs) == 4
    assert pairs[0] == (0,)
    assert pairs[1] == (1,)
    assert pairs[2] == (4,)
    assert pairs[3] == (8,)


def test_adjacent_vertex_indices_2():
    chain = PolygonalChain((0, 1, 4, 8))
    pairs = list(chain.adjacent_vertex_indices(2))
    assert len(pairs) == 3
    assert pairs[0] == (0, 1)
    assert pairs[1] == (1, 4)
    assert pairs[2] == (4, 8)


def test_adjacent_vertex_indices_3():
    chain = PolygonalChain((0, 1, 4, 8))
    pairs = list(chain.adjacent_vertex_indices(3))
    assert len(pairs) == 2
    assert pairs[0] == (0, 1, 4)
    assert pairs[1] == (1, 4, 8)


def test_segments():
    chain = PolygonalChain((0, 1, 4, 8))
    segments = list(chain.segments())
    assert len(segments) == 3
    assert segments[0] == LineSegment((0, 1))
    assert segments[1] == LineSegment((1, 4))
    assert segments[2] == LineSegment((4, 8))
