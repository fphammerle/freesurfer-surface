import locale

import pytest

from freesurfer_surface import setlocale, UnsupportedLocaleSettingError


def test_set():
    system_locale = locale.setlocale(locale.LC_ALL)
    assert system_locale != 'C'
    with setlocale('C'):
        assert locale.setlocale(locale.LC_ALL) == 'C'
    assert locale.setlocale(locale.LC_ALL) == system_locale


def test_invalid():
    system_locale = locale.setlocale(locale.LC_ALL)
    with pytest.raises(UnsupportedLocaleSettingError):
        with setlocale('abcdef21'):
            pass
    assert locale.setlocale(locale.LC_ALL) == system_locale
