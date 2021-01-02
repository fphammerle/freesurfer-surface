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
