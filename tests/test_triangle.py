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
    # pylint: disable=unneeded-not
    assert not Triangle((0, 1, 2)) == Triangle((0, 1, 4))
    assert not Triangle((0, 1, 2)) == Triangle((0, 4, 2))
    assert not Triangle((0, 1, 2)) == Triangle((4, 1, 2))


def test_repr():
    assert repr(Triangle((0, 1, 2))) == 'Triangle(vertex_indices=(0, 1, 2))'
