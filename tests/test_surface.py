import datetime
import os

import pytest

from freesurfer_surface import Surface, Vertex


SUBJECTS_DIR = os.path.join(os.path.dirname(__file__), 'subjects')
SURFACE_FILE_PATH = os.path.join(SUBJECTS_DIR, 'fabian', 'surf', 'lh.pial')


def test_read_triangular():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert surface.creator == b'fabianpeter'
    assert surface.creation_datetime == datetime.datetime(2019, 5, 9, 22, 37, 41)
    assert len(surface.vertices) == 155622
    assert len(surface.triangles_vertex_indices) == 311240
    assert not surface.using_old_real_ras
    assert surface.volume_geometry_info == (
        b'valid = 1  # volume info valid\n',
        b'filename = ../mri/filled-pretess255.mgz\n',
        b'volume = 256 256 256\n',
        b'voxelsize = 1.000000000000000e+00 1.000000000000000e+00 1.000000000000000e+00\n',
        b'xras   = -1.000000000000000e+00 0.000000000000000e+00 1.862645149230957e-09\n',
        b'yras   = 0.000000000000000e+00 -6.655682227574289e-09 -1.000000000000000e+00\n',
        b'zras   = 0.000000000000000e+00 1.000000000000000e+00 -8.300048648379743e-09\n',
        b'cras   = -2.773597717285156e+00 1.566547393798828e+01 -7.504364013671875e+00\n')
    assert surface.command_lines == [
        b'mris_remove_intersection ../surf/lh.orig ../surf/lh.orig'
        b' ProgramVersion: $Name: stable6 $'
        b'  TimeStamp: 2019/05/09-17:42:36-GMT'
        b'  BuildTimeStamp: Jan 18 2017 16:38:58'
        b'  CVS: $Id: mris_remove_intersection.c,v 1.6 2011/03/02 00:04:32 nicks Exp $'
        b'  User: fabianpeter'
        b'  Machine: host12345'
        b'  Platform: Linux'
        b'  PlatformVersion: 4.15.0-46-generic'
        b'  CompilerName: GCC'
        b'  CompilerVersion: 40400'
        b'  ',
        b'mris_make_surfaces -orig_white white.preaparc -orig_pial white.preaparc'
        b' -aseg ../mri/aseg.presurf -mgz -T1 brain.finalsurfs'
        b' fabian20190509 lh ProgramVersion: $Name:  $'
        b'  TimeStamp: 2019/05/09-20:27:28-GMT'
        b'  BuildTimeStamp: Jan 18 2017 16:38:58'
        b'  CVS: $Id: mris_make_surfaces.c,v 1.164.2.4 2016/12/13 22:26:32 zkaufman Exp $'
        b'  User: fabianpeter'
        b'  Machine: host12345'
        b'  Platform: Linux'
        b'  PlatformVersion: 4.15.0-46-generic'
        b'  CompilerName: GCC'
        b'  CompilerVersion: 40400'
        b'  ']


@pytest.mark.parametrize(('creation_datetime', 'expected_str'), [
    (datetime.datetime(2019, 5, 9, 22, 37, 41), b'Thu May  9 22:37:41 2019'),
    (datetime.datetime(2019, 4, 24, 23, 29, 22), b'Wed Apr 24 23:29:22 2019'),
])
def test_triangular_creation_datetime_strftime(creation_datetime, expected_str):
    surface = Surface()
    surface.creation_datetime = creation_datetime
    # pylint: disable=protected-access
    assert expected_str == surface._triangular_creation_datetime_strftime()


def test_read_write_triangular_same(tmpdir):
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    output_path = tmpdir.join('surface')
    surface.write_triangular(output_path,
                             creation_datetime=surface.creation_datetime)
    with open(output_path, 'rb') as output_file:
        with open(SURFACE_FILE_PATH, 'rb') as expected_file:
            assert expected_file.read() == output_file.read()


def test_write_read_triangular_same(tmpdir):
    expected_surface = Surface()
    expected_surface.creator = b'pytest'
    expected_surface.creation_datetime = datetime.datetime.now().replace(microsecond=0)
    expected_surface.vertices = [Vertex(0.0, 0.0, 0.0),
                                 Vertex(1.0, 2.0, 3.0),
                                 Vertex(2.0, 4.0, 6.0),
                                 Vertex(3.0, 5.0, 7.0)]
    expected_surface.triangles_vertex_indices = [(0, 1, 2),
                                                 (0, 1, 3),
                                                 (3, 2, 1)]
    expected_surface.using_old_real_ras = False
    expected_surface.volume_geometry_info = tuple(b'?\n' for _ in range(8))
    expected_surface.command_lines = [b'?', b'!']
    output_path = tmpdir.join('surface')
    expected_surface.write_triangular(output_path,
                                      creation_datetime=expected_surface.creation_datetime)
    resulted_surface = Surface.read_triangular(output_path)
    assert vars(expected_surface) == vars(resulted_surface)
