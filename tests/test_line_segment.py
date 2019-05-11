from freesurfer_surface import _LineSegment


def test_eq():
    assert _LineSegment((67018, 67019)) == _LineSegment((67018, 67019))
    assert _LineSegment((67018, 67019)) == _LineSegment((67019, 67018))
    assert _LineSegment((67019, 67018)) == _LineSegment((67018, 67019))
