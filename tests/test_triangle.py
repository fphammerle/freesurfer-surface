import pytest

from freesurfer_surface import Triangle


def test_init():
    triangle = Triangle((0, 21, 42))
    assert triangle.vertex_indices == (0, 21, 42)


def test_init_invalid_indices_len():
    with pytest.raises(Exception):
        Triangle((0, 21, 42, 84))


def test_eq():
    assert Triangle((0, 1, 2)) == Triangle((0, 1, 2))
    assert Triangle((0, 1, 2)) == Triangle((1, 2, 0))
    # pylint: disable=unneeded-not
    assert not Triangle((0, 1, 2)) == Triangle((0, 1, 4))
    assert not Triangle((0, 1, 2)) == Triangle((0, 4, 2))
    assert not Triangle((0, 1, 2)) == Triangle((4, 1, 2))


def test_repr():
    assert repr(Triangle((0, 1, 2))) == 'Triangle(vertex_indices=(0, 1, 2))'


def test_adjacent_vertex_indices_1():
    chain = Triangle((1, 4, 8))
    singles = list(chain.adjacent_vertex_indices(1))
    assert len(singles) == 3
    assert singles[0] == (1,)
    assert singles[1] == (4,)
    assert singles[2] == (8,)


def test_adjacent_vertex_indices_2():
    chain = Triangle((1, 4, 8))
    pairs = list(chain.adjacent_vertex_indices(2))
    assert len(pairs) == 3
    assert pairs[0] == (1, 4)
    assert pairs[1] == (4, 8)
    assert pairs[2] == (8, 1)


def test_adjacent_vertex_indices_3():
    chain = Triangle((1, 4, 8))
    triplets = list(chain.adjacent_vertex_indices(3))
    assert len(triplets) == 3
    assert triplets[0] == (1, 4, 8)
    assert triplets[1] == (4, 8, 1)
    assert triplets[2] == (8, 1, 4)


def test_adjacent_vertex_indices_4():
    chain = Triangle((1, 4, 8))
    quadruples = list(chain.adjacent_vertex_indices(4))
    assert len(quadruples) == 3
    assert quadruples[0] == (1, 4, 8, 1)
    assert quadruples[1] == (4, 8, 1, 4)
    assert quadruples[2] == (8, 1, 4, 8)


def test_adjacent_vertex_indices_5():
    chain = Triangle((1, 4, 8))
    quintuples = list(chain.adjacent_vertex_indices(5))
    assert len(quintuples) == 3
    assert quintuples[0] == (1, 4, 8, 1, 4)
    assert quintuples[1] == (4, 8, 1, 4, 8)
    assert quintuples[2] == (8, 1, 4, 8, 1)
