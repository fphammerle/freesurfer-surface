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

SUBJECTS_DIR = os.path.join(os.path.dirname(__file__), "subjects")

ANNOTATION_FILE_PATH = os.path.join(SUBJECTS_DIR, "fabian", "label", "lh.aparc.annot")
SURFACE_FILE_PATH = os.path.join(SUBJECTS_DIR, "fabian", "surf", "lh.pial")
