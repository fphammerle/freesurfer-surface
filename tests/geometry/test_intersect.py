import numpy
import pytest

from freesurfer_surface.geometry \
    import _Line, _intersect_planes, _intersect_line_segments


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


@pytest.mark.parametrize(('points_a', 'points_b', 'expected_point'), [
    (([0, 0, 0], [0, 0, 2]), ([0, -1, 1], [0, 1, 1]), [0, 0, 1]),
    (([0, 0, 0], [0, 0, 2]), ([0, 0, 1], [0, 1, 1]), [0, 0, 1]),
    (([0, 0, 0], [0, 0, 2]), ([0, -1, 1], [0, 0, 1]), [0, 0, 1]),
    (([0, 0, 0], [0, 0, 2]), ([0, 0, 1], [0, -1, 1]), [0, 0, 1]),
    (([0, 0, 0], [2, 4, 8]), ([0, 0, 4], [2, 4, 4]), [1, 2, 4]),
    (([0, 0, 0], [2, 4, 8]), ([0, 0, 2], [2, 4, 2]), [0.5, 1, 2]),
    (([2, 4, 8], [0, 0, 0]), ([0, 0, 2], [2, 4, 2]), [0.5, 1, 2]),
    (([2, 4, 8], [0, 0, 0]), ([2, 4, 2], [0, 0, 2]), [0.5, 1, 2]),
    (([3, 5, 9], [1, 1, 1]), ([3, 5, 3], [1, 1, 3]), [1.5, 2, 3]),
    (([0, 0, 0], [0, 0, 4]), ([0, -8, 0], [0, 8, 0]), [0, 0, 0]),
    (([0, 0, 0], [0, 0, 4]), ([0, -8, 3], [0, 8, 3]), [0, 0, 3]),
    (([0, 0, 0], [0, 0, 4]), ([0, -8, 4], [0, 8, 4]), [0, 0, 4]),
    (([0, 0, 0], [0, 0, 4]), ([0, -8, 4.1], [0, 8, 4.1]), False),
    (([0, 0, 0], [0, 0, 4]), ([0, -8, -1], [0, 8, -1]), False),
    (([0, 0, 0], [0, 0, 4]), ([0, 0, 0], [0, 0, 4]), True),
])
def test_intersect_line_segments(points_a, points_b, expected_point):
    # pylint: disable=protected-access
    point = _intersect_line_segments(numpy.array(points_a),
                                     numpy.array(points_b))
    if isinstance(expected_point, bool):
        assert isinstance(point, bool)
        assert point == expected_point
    else:
        assert numpy.allclose(point, expected_point)
