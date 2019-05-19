import numpy
import pytest

from freesurfer_surface.geometry import _Line


def test_init_list():
    line = _Line(point=[1, 2, 3], vector=[4, 5, 6])
    assert isinstance(line.point, numpy.ndarray)
    assert line.point.dtype == float
    assert line.point.shape == (3,)
    assert numpy.allclose(line.point, [1, 2, 3])
    assert isinstance(line.vector, numpy.ndarray)
    assert line.vector.dtype == float
    assert line.vector.shape == (3,)
    assert numpy.allclose(line.vector, [4, 5, 6])


def test_init_numpy_array():
    line = _Line(point=numpy.array([2, 3, 4]),
                 vector=numpy.array([6, 7, 8]))
    assert isinstance(line.point, numpy.ndarray)
    assert line.point.dtype == float
    assert line.point.shape == (3,)
    assert numpy.allclose(line.point, [2, 3, 4])
    assert isinstance(line.vector, numpy.ndarray)
    assert line.vector.dtype == float
    assert line.vector.shape == (3,)
    assert numpy.allclose(line.vector, [6, 7, 8])


@pytest.mark.parametrize(('line_a', 'line_b', 'equal'), [
    (_Line(point=(0, 0, 0), vector=(0, 0, 1)),
     _Line(point=(0, 0, 0), vector=(0, 0, -1)),
     True),
    (_Line(point=(0, 0, 0), vector=(0, 0, 1)),
     _Line(point=(0, 0, 1), vector=(0, 0, -1)),
     True),
    (_Line(point=(2, 4, 0), vector=(0, 0, 1)),
     _Line(point=(2, 4, 1), vector=(0, 0, -1)),
     True),
    (_Line(point=(2, 4, 0), vector=(0, 0, 1)),
     _Line(point=(2, 4, 1), vector=(0, 1, -1)),
     False),
    (_Line(point=(2, 4, 0), vector=(2, 0, 1)),
     _Line(point=(2, 4, 1), vector=(0, 0, -1)),
     False),
    (_Line(point=(2, 4, 0), vector=(0, 0, 1)),
     _Line(point=(2, 5, 1), vector=(0, 0, -1)),
     False),
    (_Line(point=(0, 0, 0), vector=(0, 0, 1)),
     _Line(point=(0, 0, 0), vector=(0, 1, 0)),
     False),
    (_Line(point=(1, 2, 3), vector=(-1, 3, -5)),
     _Line(point=(-1, 8, -7), vector=(2, -6, 10)),
     True),
])
def test__equal(line_a, line_b, equal):
    assert (line_a == line_b) == equal


def test_repr():
    line = _Line(point=[1, 2, 3], vector=[4, 5, 6])
    assert repr(line) == 'line(t) = [1. 2. 3.] + [4. 5. 6.] t'


@pytest.mark.parametrize(('line_a', 'line_b', 'expected_point'), [
    (_Line(point=(1, 2, 3), vector=(0, 0, 4)),
     _Line(point=(1, 2, 3), vector=(0, 5, 0)),
     [1, 2, 3]),
    (_Line(point=(1, 2, 7), vector=(0, 0, 4)),
     _Line(point=(1, -8, 3), vector=(0, 5, 0)),
     [1, 2, 3]),
    (_Line(point=(1, 2, 3), vector=(3, 2, 4)),
     _Line(point=(1, 2, 3), vector=(4, -5, 9)),
     [1, 2, 3]),
    (_Line(point=(-2, 0, -1), vector=(3, 2, 4)),
     _Line(point=(1, 2, 3), vector=(4, -5, 9)),
     [1, 2, 3]),
    (_Line(point=(-2, 0, -1), vector=(3, 2, 4)),
     _Line(point=(9, -8, 21), vector=(4, -5, 9)),
     [1, 2, 3]),
    (_Line(point=(-7, 4, -2), vector=(2, 6, 3)),
     _Line(point=(-7, 4, -2), vector=(-4, 8, -3)),
     [-7, 4, -2]),
    (_Line(point=(-5, 10, 1), vector=(2, 6, 3)),
     _Line(point=(-15, 20, -8), vector=(-4, 8, -3)),
     [-7, 4, -2]),
    (_Line(point=(1, 2, 3), vector=(4, 8, 7)),
     _Line(point=(1, 2, 3), vector=(4, 8, 7)),
     True),
    (_Line(point=(1, 2, 3), vector=(4, 8, 7)),
     _Line(point=(1, 2, 3), vector=(8, 16, 14)),
     True),
    (_Line(point=(1, 2, 3), vector=(-4, -8, -7)),
     _Line(point=(1, 2, 3), vector=(8, 16, 14)),
     True),
    (_Line(point=(-3, -6, -4), vector=(-4, -8, -7)),
     _Line(point=(1, 2, 3), vector=(8, 16, 14)),
     True),
    (_Line(point=(-3, -6, -4), vector=(-4, -8, -7)),
     _Line(point=(5, 10, 10), vector=(8, 16, 14)),
     True),
    (_Line(point=(-3, -6, -3), vector=(-4, -8, -7)),
     _Line(point=(5, 10, 10), vector=(8, 16, 14)),
     False),
])
def test_intersect_line(line_a, line_b, expected_point):
    # pylint: disable=protected-access
    point = line_a.intersect_line(line_b)
    if isinstance(expected_point, bool):
        assert isinstance(point, bool)
        assert point == expected_point
    else:
        assert numpy.allclose(point, expected_point)
