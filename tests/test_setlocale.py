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

import locale

import pytest

from freesurfer_surface import UnsupportedLocaleSettingError, setlocale


def test_set():
    system_locale = locale.setlocale(locale.LC_ALL)
    assert system_locale != "C"
    with setlocale("C"):
        assert locale.setlocale(locale.LC_ALL) == "C"
    assert locale.setlocale(locale.LC_ALL) == system_locale


def test_unsupported():
    system_locale = locale.setlocale(locale.LC_ALL)
    with pytest.raises(UnsupportedLocaleSettingError):
        with setlocale("abcdef21"):
            pass
    assert locale.setlocale(locale.LC_ALL) == system_locale


def test_other_error():
    system_locale = locale.setlocale(locale.LC_ALL)
    with pytest.raises(TypeError):
        with setlocale(42):
            pass
    assert locale.setlocale(locale.LC_ALL) == system_locale
