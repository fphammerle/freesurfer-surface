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
