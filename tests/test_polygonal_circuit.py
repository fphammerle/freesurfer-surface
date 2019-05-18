import pytest

from freesurfer_surface import _PolygonalCircuit


@pytest.mark.parametrize(('source_vertex_indices', 'expected_vertex_indices'), [
    ((1,), (1,)),
    ((1, 2), (1, 2)),
    ((2, 1), (1, 2)),
    ((1, 2, 3), (1, 2, 3)),
    ((2, 3, 1), (1, 2, 3)),
    ((3, 1, 2), (1, 2, 3)),
    ((1, 3, 2), (1, 2, 3)),
    ((2, 1, 3), (1, 2, 3)),
    ((3, 2, 1), (1, 2, 3)),
    ((1, 2, 3, 5), (1, 2, 3, 5)),
    ((2, 3, 5, 1), (1, 2, 3, 5)),
    ((3, 5, 1, 2), (1, 2, 3, 5)),
    ((2, 1, 5, 3), (1, 2, 3, 5)),
    ((5, 3, 2, 1), (1, 2, 3, 5)),
])
def test__normalize(source_vertex_indices, expected_vertex_indices):
    # pylint: disable=protected-access
    circuit = _PolygonalCircuit(source_vertex_indices)
    assert expected_vertex_indices == circuit._normalize()._vertex_indices


def test_eq():
    assert _PolygonalCircuit((0, 1)) == _PolygonalCircuit((0, 1))
    assert _PolygonalCircuit((0, 1)) == _PolygonalCircuit((1, 0))
    assert _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((0, 1, 2))
    assert _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((1, 2, 0))
    assert _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((2, 0, 1))
    # pylint: disable=unneeded-not
    assert not _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((0, 1, 4))
    assert not _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((0, 4, 2))
    assert not _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((4, 1, 2))


def test_eq_reverse():
    assert _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((2, 1, 0))
    assert _PolygonalCircuit((0, 1, 2)) == _PolygonalCircuit((0, 2, 1))
    assert _PolygonalCircuit((0, 1, 2, 4)) == _PolygonalCircuit((4, 2, 1, 0))
    assert _PolygonalCircuit((0, 1, 2, 4)) == _PolygonalCircuit((1, 0, 4, 2))


def test_hash():
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        == hash(_PolygonalCircuit((0, 1, 2)))
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        == hash(_PolygonalCircuit((1, 2, 0)))
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        == hash(_PolygonalCircuit((2, 0, 1)))
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        != hash(_PolygonalCircuit((0, 1, 4)))
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        != hash(_PolygonalCircuit((0, 4, 2)))
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        != hash(_PolygonalCircuit((4, 1, 2)))


def test_hash_reverse():
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        == hash(_PolygonalCircuit((2, 1, 0)))
    assert hash(_PolygonalCircuit((0, 1, 2))) \
        == hash(_PolygonalCircuit((0, 2, 1)))
    assert hash(_PolygonalCircuit((0, 1, 2, 4))) \
        == hash(_PolygonalCircuit((4, 2, 1, 0)))
    assert hash(_PolygonalCircuit((0, 1, 2, 4))) \
        == hash(_PolygonalCircuit((1, 0, 4, 2)))
    assert hash(_PolygonalCircuit((0, 1, 2, 4))) \
        != hash(_PolygonalCircuit((1, 4, 0, 2)))
