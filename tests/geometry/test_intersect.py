import numpy
import pytest

from freesurfer_surface.geometry import _intersect_planes, _Line


@pytest.mark.parametrize(
    ('normal_vector_a', 'constant_a',
     'normal_vector_b', 'constant_b',
     'expected_line'),
    [([0, 0, 1], 0, [0, 1, 0], 0, _Line([0, 0, 0], [1, 0, 0])),
     ([0, 0, 1], 0, [0, 3, 0], 0, _Line([0, 0, 0], [1, 0, 0])),
     ([0, 0, 1], 0, [4, 0, 0], 0, _Line([0, 0, 0], [0, 1, 0])),
     ([0, 2, 2], 0, [3, 0, 3], 0, _Line([0, 0, 0], [1, 1, -1])),
     ([1, 2, 4], 0, [2, 3, 5], 0, _Line([0, 0, 0], [-2, 3, -1])),
     ([1, 2, 4], 0, [2, 3, 5], 2, _Line([2, 1, -1], [-2, 3, -1])),
     ([2, 3, 5], 2, [1, 2, 4], 0, _Line([2, 1, -1], [-2, 3, -1])),
     ([2, 3, 5], 2, [1, 2, 4], 7, _Line([-7, -3, 5], [-2, 3, -1])),
     ([1, 2, 4], 0, [2, 4, 8], 1, False),
     ([1, 2, 4], 0, [2, 4, 8], 0, True)],
)
def test__intersect_planes(normal_vector_a, constant_a,
                           normal_vector_b, constant_b,
                           expected_line):
    line = _intersect_planes(normal_vector_a, constant_a,
                             normal_vector_b, constant_b)
    assert line == expected_line
    if not isinstance(expected_line, bool):
        assert numpy.isclose(numpy.inner(normal_vector_a, line.vector), 0)
        assert numpy.isclose(numpy.inner(normal_vector_b, line.vector), 0)
        assert numpy.isclose(numpy.inner(normal_vector_a, line.point),
                             constant_a)
        assert numpy.isclose(numpy.inner(normal_vector_b, line.point),
                             constant_b)
        other_point = line.point + line.vector
        assert numpy.isclose(numpy.inner(normal_vector_a, other_point),
                             constant_a)
        assert numpy.isclose(numpy.inner(normal_vector_b, other_point),
                             constant_b)
