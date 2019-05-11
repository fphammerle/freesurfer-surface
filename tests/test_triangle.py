import pytest

from freesurfer_surface import Triangle


def test_init():
    triangle = Triangle((0, 21, 42))
    assert triangle.vertex_indices == (0, 21, 42)


def test_init_invalid_indices_len():
    with pytest.raises(Exception):
        Triangle((0, 21, 42, 84))


def test_reassign_vertex_indices():
    triangle = Triangle((0, 21, 42))
    triangle.vertex_indices = (1, 2, 3)
    assert triangle.vertex_indices == (1, 2, 3)


def test_reassign_vertex_indices_invalid_len():
    triangle = Triangle((0, 21, 42))
    with pytest.raises(Exception):
        triangle.vertex_indices = (1, 2, 3, 4)


def test_eq():
    assert Triangle((0, 1, 2)) == Triangle((0, 1, 2))
    assert Triangle((0, 1, 2)) == Triangle((1, 2, 0))
    # pylint: disable=unneeded-not
    assert not Triangle((0, 1, 2)) == Triangle((0, 1, 4))
    assert not Triangle((0, 1, 2)) == Triangle((0, 4, 2))
    assert not Triangle((0, 1, 2)) == Triangle((4, 1, 2))


def test_repr():
    assert repr(Triangle((0, 1, 2))) == 'Triangle(vertex_indices=(0, 1, 2))'
