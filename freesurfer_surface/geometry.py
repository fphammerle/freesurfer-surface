import typing

import numpy


def _collinear(vector_a: numpy.ndarray, vector_b: numpy.ndarray) -> bool:
    # null vector: https://math.stackexchange.com/a/1772580
    return numpy.allclose(numpy.cross(vector_a, vector_b),
                          numpy.zeros(len(vector_a)))


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
