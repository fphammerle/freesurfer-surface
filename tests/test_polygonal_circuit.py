import pytest

from freesurfer_surface import _PolygonalCircuit


def test_init_tuple():
    circuit = _PolygonalCircuit((1, 2, 3, 5))
    assert circuit.vertex_indices == (1, 2, 3, 5)


def test_init_list():
    circuit = _PolygonalCircuit([1, 2, 3, 5])
    assert circuit.vertex_indices == (1, 2, 3, 5)


def test_init_iterator():
    circuit = _PolygonalCircuit(iter([1, 2, 3, 5]))
    assert circuit.vertex_indices == (1, 2, 3, 5)


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


def test_adjacent_vertex_indices_1():
    chain = _PolygonalCircuit((0, 1, 4, 8))
    singles = list(chain.adjacent_vertex_indices(1))
    assert len(singles) == 4
    assert singles[0] == (0,)
    assert singles[1] == (1,)
    assert singles[2] == (4,)
    assert singles[3] == (8,)


def test_adjacent_vertex_indices_2():
    chain = _PolygonalCircuit((0, 1, 4, 8))
    pairs = list(chain.adjacent_vertex_indices(2))
    assert len(pairs) == 4
    assert pairs[0] == (0, 1)
    assert pairs[1] == (1, 4)
    assert pairs[2] == (4, 8)
    assert pairs[3] == (8, 0)


def test_adjacent_vertex_indices_3():
    chain = _PolygonalCircuit((0, 1, 4, 8))
    triplets = list(chain.adjacent_vertex_indices(3))
    assert len(triplets) == 4
    assert triplets[0] == (0, 1, 4)
    assert triplets[1] == (1, 4, 8)
    assert triplets[2] == (4, 8, 0)
    assert triplets[3] == (8, 0, 1)


def test_adjacent_vertex_indices_4():
    chain = _PolygonalCircuit((0, 1, 4, 8))
    quadruples = list(chain.adjacent_vertex_indices(4))
    assert len(quadruples) == 4
    assert quadruples[0] == (0, 1, 4, 8)
    assert quadruples[1] == (1, 4, 8, 0)
    assert quadruples[2] == (4, 8, 0, 1)
    assert quadruples[3] == (8, 0, 1, 4)


def test_adjacent_vertex_indices_5():
    chain = _PolygonalCircuit((0, 1, 4, 8))
    quintuples = list(chain.adjacent_vertex_indices(5))
    assert len(quintuples) == 4
    assert quintuples[0] == (0, 1, 4, 8, 0)
    assert quintuples[1] == (1, 4, 8, 0, 1)
    assert quintuples[2] == (4, 8, 0, 1, 4)
    assert quintuples[3] == (8, 0, 1, 4, 8)
