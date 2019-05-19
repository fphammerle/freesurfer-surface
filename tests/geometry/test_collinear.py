import pytest

from freesurfer_surface.geometry import _collinear


@pytest.mark.parametrize(('vector_a', 'vector_b', 'collinear'), [
    ([1, 0, 0], [1, 0, 0], True),
    ([1, 0, 0], [2, 0, 0], True),
    ([1, 0, 0], [-2, 0, 0], True),
    ([1, 0, 0], [-2, 0, 0], True),
    ([1, 2, 3], [1, 2, 3], True),
    ([1, 2, 3], [1, 2, 4], False),
    ([1, 2, 3], [2, 4, 6], True),
    ([1, 2, 3], [2, 4, 7], False),
    ([1, 2, 3], [2, 5, 6], False),
    ([1, 2, 3], [3, 4, 6], False),
])
def test__collinear(vector_a, vector_b, collinear):
    # pylint: disable=protected-access
    assert _collinear(vector_a, vector_b) == collinear
