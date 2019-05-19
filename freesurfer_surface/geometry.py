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
