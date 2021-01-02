# freesurfer-surface - Read and Write Surface Files in Freesurfer’s TriangularSurface Format
#
# Copyright (C) 2020 Fabian Peter Hammerle <fabian@hammerle.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest

from freesurfer_surface import Label


@pytest.mark.parametrize(
    ("red", "green", "blue", "transparency", "color_code"),
    [
        (220, 20, 20, 0, 1316060),
        (60, 20, 220, 0, 14423100),
        (75, 50, 125, 0, 8204875),
        (20, 220, 160, 0, 10542100),
    ],
)
def test_color_code(red, green, blue, transparency, color_code):
    label = Label(
        index=21,
        name="name",
        red=red,
        green=green,
        blue=blue,
        transparency=transparency,
    )
    assert color_code == label.color_code


def test_color_code_unknown():
    label = Label(index=0, name="unknown", red=21, green=21, blue=21, transparency=0)
    assert label.color_code == 0


@pytest.mark.parametrize(
    ("red", "green", "blue", "hex_color_code"),
    [
        (0, 0, 0, "#000000"),
        (255, 255, 255, "#ffffff"),
        (255, 0, 0, "#ff0000"),
        (0, 255, 0, "#00ff00"),
        (0, 0, 255, "#0000ff"),
        (1, 2, 3, "#010203"),
        (17, 18, 19, "#111213"),
        (128, 192, 255, "#80c0ff"),
        (20, 220, 160, "#14dca0"),
    ],
)
def test_hex_color_code(red, green, blue, hex_color_code):
    label = Label(
        index=21, name="name", red=red, green=green, blue=blue, transparency=0
    )
    assert hex_color_code == label.hex_color_code.lower()


def test_str():
    label = Label(
        index=24, name="precentral", red=60, green=20, blue=220, transparency=0
    )
    assert str(label) == "Label(name=precentral, index=24, color=#3c14dc)"


def test_repr():
    label = Label(
        index=24, name="precentral", red=60, green=20, blue=220, transparency=0
    )
    assert repr(label) == "Label(name=precentral, index=24, color=#3c14dc)"
