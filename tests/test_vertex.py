import pytest

from freesurfer_surface import Vertex


def test_init():
    vertex = Vertex(-4.0, 0.5, 21.42)
    assert vertex.right == pytest.approx(-4.0)
    assert vertex.anterior == pytest.approx(0.5)
    assert vertex.superior == pytest.approx(21.42)
