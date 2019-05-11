import pytest

from freesurfer_surface import Label


@pytest.mark.parametrize(('red', 'green', 'blue', 'transparency', 'color_code'), [
    # pylint: disable=bad-whitespace
    (220,  20,  20,   0,  1316060),
    ( 60,  20, 220,   0, 14423100),
    ( 75,  50, 125,   0,  8204875),
    ( 20, 220, 160,   0, 10542100),
])
def test_color_code(red, green, blue, transparency, color_code):
    label = Label()
    label.index = 21
    label.red = red
    label.green = green
    label.blue = blue
    label.transparency = transparency
    assert color_code == label.color_code


def test_color_code_unknown():
    label = Label()
    label.index = 0
    label.name = 'unknown'
    label.red = 21
    label.green = 21
    label.blue = 21
    assert label.color_code == 0


@pytest.mark.parametrize(('red', 'green', 'blue', 'hex_color_code'), [
    # pylint: disable=bad-whitespace
    (  0,   0,   0, '#000000'),
    (255, 255, 255, '#ffffff'),
    (255,   0,   0, '#ff0000'),
    (  0, 255,   0, '#00ff00'),
    (  0,   0, 255, '#0000ff'),
    (  1,   2,   3, '#010203'),
    ( 17,  18,  19, '#111213'),
    (128, 192, 255, '#80c0ff'),
    ( 20, 220, 160, '#14dca0'),
])
def test_hex_color_code(red, green, blue, hex_color_code):
    label = Label()
    label.red = red
    label.green = green
    label.blue = blue
    assert hex_color_code == label.hex_color_code.lower()


def test_str():
    label = Label()
    label.index = 24
    label.name = 'precentral'
    label.red = 60
    label.green = 20
    label.blue = 220
    label.transparency = 0
    assert str(label) == 'Label(name=precentral, index=24, color=#3c14dc)'
