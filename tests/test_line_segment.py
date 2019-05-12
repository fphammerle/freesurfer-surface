from freesurfer_surface import _LineSegment


def test_eq():
    assert _LineSegment((67018, 67019)) == _LineSegment((67018, 67019))
    assert _LineSegment((67018, 67019)) == _LineSegment((67019, 67018))
    assert _LineSegment((67019, 67018)) == _LineSegment((67018, 67019))


def test_repr():
    assert repr(_LineSegment((67018, 67019))) \
        == '_LineSegment(vertex_indices=(67018, 67019))'
