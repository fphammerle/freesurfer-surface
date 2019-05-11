import pytest

from freesurfer_surface import PolygonalChain


def test_init():
    chain = PolygonalChain((0, 21, 42, 84))
    assert tuple(chain.vertex_indices) == (0, 21, 42, 84)


def test_reassign_vertex_indices():
    chain = PolygonalChain((0, 21, 42, 84))
    chain.vertex_indices = (1, 2, 3, 4)
    assert tuple(chain.vertex_indices) == (1, 2, 3, 4)


def test_eq():
    assert PolygonalChain((0, 1, 2)) == PolygonalChain((0, 1, 2))
    # pylint: disable=unneeded-not
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((0, 1, 4))
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((0, 4, 2))
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((4, 1, 2))
    assert not PolygonalChain((0, 1, 2)) == PolygonalChain((1, 2, 3, 4))


def test_repr():
    assert repr(PolygonalChain([])) \
        == 'PolygonalChain(vertex_indices=())'
    assert repr(PolygonalChain((0, 2, 1))) \
        == 'PolygonalChain(vertex_indices=(0, 2, 1))'
    assert repr(PolygonalChain((0, 2, 1, 4, 3))) \
        == 'PolygonalChain(vertex_indices=(0, 2, 1, 4, 3))'


@pytest.mark.parametrize(('vertex_indices_a', 'vertex_indices_b', 'expected_vertex_indices'), [
    ((1, 2, 3), (3, 4), (1, 2, 3, 4)),
    ((1, 2, 3), (4, 3), (1, 2, 3, 4)),
    ((3, 2, 1), (3, 4), (4, 3, 2, 1)),
    ((3, 2, 1), (4, 3), (4, 3, 2, 1)),
    ((1,), (1,), (1,)),
    ((1, 2), (1,), (1, 2)),
    ((1, 2), (2,), (1, 2)),
    ((0, 3, 1, 5, 2), (3, 5, 2, 0), (3, 5, 2, 0, 3, 1, 5, 2)),
])
def test_connect(vertex_indices_a, vertex_indices_b, expected_vertex_indices):
    chain = PolygonalChain(vertex_indices_a)
    chain.connect(PolygonalChain(vertex_indices_b))
    assert PolygonalChain(expected_vertex_indices) == chain


@pytest.mark.parametrize(('vertex_indices_a', 'vertex_indices_b'), [
    ((1, 2, 3), (2, 4)),
    ((1, 2, 3), ()),
    ((), (3, 4)),
])
def test_connect_fail(vertex_indices_a, vertex_indices_b):
    chain = PolygonalChain(vertex_indices_a)
    with pytest.raises(Exception):
        chain.connect(PolygonalChain(vertex_indices_b))
