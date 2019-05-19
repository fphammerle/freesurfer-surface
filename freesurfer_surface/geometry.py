import numpy


def _collinear(vector_a: numpy.ndarray, vector_b: numpy.ndarray) -> bool:
    # null vector: https://math.stackexchange.com/a/1772580
    return numpy.allclose(numpy.cross(vector_a, vector_b),
                          numpy.zeros(len(vector_a)))
