import numpy
import pytest

from freesurfer_surface import Vertex


def test_init():
    vertex = Vertex(-4.0, 0.5, 21.42)
    assert isinstance(vertex, numpy.ndarray)
    assert vertex.right == pytest.approx(-4.0)
    assert vertex.anterior == pytest.approx(0.5)
    assert vertex.superior == pytest.approx(21.42)


def test_init_kwargs():
    vertex = Vertex(right=-4.0, superior=21.42, anterior=0.5)
    assert vertex.right == pytest.approx(-4.0)
    assert vertex.anterior == pytest.approx(0.5)
    assert vertex.superior == pytest.approx(21.42)


def test_repr():
    vertex = Vertex(right=-4.0, superior=21.42, anterior=0.5)
    assert repr(vertex) == 'Vertex(right=-4.0, anterior=0.5, superior=21.42)'


def test_add():
    assert Vertex(-1.5, 4, 2) + Vertex(2, -4.5, 3) \
        == pytest.approx(Vertex(0.5, -0.5, 5))


def test_mult():
    assert Vertex(-1.5, 4, 2) * -3 == pytest.approx(Vertex(4.5, -12, -6))


def test_vars():
    attrs = vars(Vertex(-1.5, 4, 2))
    assert len(attrs) == 3
    assert attrs['right'] == pytest.approx(-1.5)
    assert attrs['anterior'] == pytest.approx(4)
    assert attrs['superior'] == pytest.approx(2)
