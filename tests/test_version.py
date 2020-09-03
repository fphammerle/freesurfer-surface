import re
import pathlib
import subprocess
import sys

import pytest

import freesurfer_surface

_VERSION_MODULE_PATH = pathlib.Path(__file__).parent.parent.joinpath(
    "freesurfer_surface", "version.py"
)


def test_version():
    if not _VERSION_MODULE_PATH.exists():
        pytest.skip("package is not installed")
    assert re.match(r"^\d+\.\d+\.\d+", freesurfer_surface.__version__)


def test_version_missing(tmp_path):
    temp_module_path = tmp_path.joinpath("version.py")
    if _VERSION_MODULE_PATH.exists():
        _VERSION_MODULE_PATH.rename(temp_module_path)
    try:
        assert (
            subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import freesurfer_surface; print(freesurfer_surface.__version__)",
                ],
                check=True,
                stdout=subprocess.PIPE,
            ).stdout.rstrip()
            == b"None"
        )
    finally:
        if temp_module_path.exists():
            temp_module_path.rename(_VERSION_MODULE_PATH)
