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

import os

import setuptools

with open("README.rst", "r") as readme:
    LONG_DESCRIPTION = readme.read()

setuptools.setup(
    name="freesurfer-surface",
    use_scm_version={
        "write_to": os.path.join("freesurfer_surface", "version.py"),
        # `version` triggers pylint C0103
        # newline after import to fix pylint C0321/multiple-statements
        "write_to_template": "import typing\n"
        + "__version__: typing.Optional[str] = '{version}'\n",
    },
    description="Python Library to Read and Write Surface Files"
    " in Freesurfer's TriangularSurface Format",
    long_description=LONG_DESCRIPTION,
    author="Fabian Peter Hammerle",
    author_email="fabian@hammerle.me",
    url="https://github.com/fphammerle/freesurfer-surface",
    license="GPLv3+",
    keywords=[
        "brain",
        "freesurfer",
        "mesh",
        "neuroimaging",
        "reader",
        "surface",
        "triangle",
        "vertex",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        # .github/workflows/python.yml
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Utilities",
    ],
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "freesurfer-annotation-labels = freesurfer_surface.__main__:annotation_labels",
            "unite-freesurfer-surfaces = freesurfer_surface.__main__:unite_surfaces",
        ]
    },
    python_requires=">=3.6",
    install_requires=["numpy<2"],
    setup_requires=["setuptools_scm"],
    tests_require=["pytest<5"],
)
