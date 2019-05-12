import locale

import pytest

from freesurfer_surface import setlocale, UnsupportedLocaleSettingError


def test_set():
    system_locale = locale.setlocale(locale.LC_ALL)
    assert system_locale != 'C'
    with setlocale('C'):
        assert locale.setlocale(locale.LC_ALL) == 'C'
    assert locale.setlocale(locale.LC_ALL) == system_locale


def test_unsupported():
    system_locale = locale.setlocale(locale.LC_ALL)
    with pytest.raises(UnsupportedLocaleSettingError):
        with setlocale('abcdef21'):
            pass
    assert locale.setlocale(locale.LC_ALL) == system_locale


def test_other_error():
    system_locale = locale.setlocale(locale.LC_ALL)
    with pytest.raises(TypeError):
        with setlocale(42):
            pass
    assert locale.setlocale(locale.LC_ALL) == system_locale
