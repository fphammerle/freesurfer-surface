import pytest

from freesurfer_surface import Label


@pytest.mark.parametrize(('red', 'green', 'blue', 'transparency', 'color_code'), [
    # pylint: disable=bad-whitespace
    (100,  20, 220,   0, 6558940),
    (140,  30,  20,   0, 9182740),
    (140,  30,  20,   1, 9182740 + (1 << (8 * 3))),
    (140,  30,  20,   7, 9182740 + (7 << (8 * 3))),
    (140,  30,  20, 123, 2072780308),
])
def test_color_code(red, green, blue, transparency, color_code):
    label = Label()
    label.red = red
    label.green = green
    label.blue = blue
    label.transparency = transparency
    assert color_code == label.color_code
