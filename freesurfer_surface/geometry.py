import typing

import numpy


def _collinear(vector_a: numpy.ndarray, vector_b: numpy.ndarray) -> bool:
    # null vector: https://math.stackexchange.com/a/1772580
    return numpy.allclose(numpy.cross(vector_a, vector_b), 0)


class _Line:

    # pylint: disable=too-few-public-methods

    def __init__(self, point, vector):
        self.point = numpy.array(point, dtype=float)
        self.vector = numpy.array(vector, dtype=float)

    def __eq__(self, other: '_Line') -> bool:
        if not _collinear(self.vector, other.vector):
            return False
        return _collinear(self.vector, self.point - other.point)

    def __repr__(self) -> str:
        return 'line(t) = {} + {} t'.format(self.point, self.vector)

    def intersect_line(self, other: '_Line') \
            -> typing.Union[numpy.ndarray, bool]:
        # https://en.wikipedia.org/wiki/Skew_lines#Distance
        lines_normal_vector = numpy.cross(self.vector, other.vector)
        if numpy.allclose(lines_normal_vector, 0):
            return _collinear(self.vector, self.point - other.point)
        plane_normal_vector = numpy.cross(other.vector, lines_normal_vector)
        return self.point + self.vector \
            * (numpy.inner(other.point - self.point, plane_normal_vector)
               / numpy.inner(self.vector, plane_normal_vector))


def _intersect_planes(normal_vector_a: numpy.ndarray,
                      constant_a: float,
                      normal_vector_b: numpy.ndarray,
                      constant_b: float) -> typing.Union[_Line, bool]:
    line_vector = numpy.cross(normal_vector_a, normal_vector_b)
    if numpy.allclose(line_vector, 0):
        return constant_a == constant_b
    point = numpy.linalg.solve(
        numpy.vstack((normal_vector_a, normal_vector_b, line_vector)),
        numpy.vstack((constant_a, constant_b, 0)),
    )
    return _Line(point=point.reshape(3), vector=line_vector)


def _between(lower_limit: numpy.ndarray,
             point: numpy.ndarray,
             upper_limit: numpy.ndarray) -> bool:
    return (lower_limit <= point).all() and (point <= upper_limit).all()


def _intersect_line_segments(points_a: numpy.ndarray,
                             points_b: numpy.ndarray) \
        -> typing.Union[numpy.ndarray, bool]:
    lines = [_Line(points[0], points[1] - points[0])
             for points in [points_a, points_b]]
    point = lines[0].intersect_line(lines[1])
    if isinstance(point, bool):
        return point
    for points in [points_a, points_b]:
        if not _between(points[0], point, points[1]) \
            and not _between(points[1], point, points[0]):
            return False
    return point
