import re

import freesurfer_surface


def test_version():
    assert re.match(r"^\d+\.\d+\.\d+", freesurfer_surface.__version__)
