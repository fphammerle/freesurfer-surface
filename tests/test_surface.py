import datetime

import pytest

from freesurfer_surface import setlocale, Vertex, Triangle, _LineSegment, \
                               Annotation, Surface

from conftest import ANNOTATION_FILE_PATH, SURFACE_FILE_PATH


def test_read_triangular():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert surface.creator == b'fabianpeter'
    assert surface.creation_datetime \
        == datetime.datetime(2019, 5, 9, 22, 37, 41)
    assert len(surface.vertices) == 155622
    assert len(surface.triangles) == 311240
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


def test_read_triangular_locale():
    with setlocale('de_AT.utf8'):
        surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert surface.creation_datetime \
        == datetime.datetime(2019, 5, 9, 22, 37, 41)


@pytest.mark.parametrize(('creation_datetime', 'expected_str'), [
    (datetime.datetime(2019, 5, 9, 22, 37, 41), b'Thu May  9 22:37:41 2019'),
    (datetime.datetime(2019, 4, 24, 23, 29, 22), b'Wed Apr 24 23:29:22 2019'),
])
def test_triangular_strftime(creation_datetime, expected_str):
    # pylint: disable=protected-access
    assert expected_str == Surface._triangular_strftime(creation_datetime)


def test_read_write_triangular_same(tmpdir):
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    output_path = tmpdir.join('surface').strpath
    surface.write_triangular(output_path,
                             creation_datetime=surface.creation_datetime)
    with open(output_path, 'rb') as output_file:
        with open(SURFACE_FILE_PATH, 'rb') as expected_file:
            assert expected_file.read() == output_file.read()


def test_read_write_datetime(tmpdir):
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    original_creation_datetime = surface.creation_datetime
    output_path = tmpdir.join('surface').strpath
    surface.write_triangular(output_path)
    assert original_creation_datetime == surface.creation_datetime
    new_surface = Surface.read_triangular(output_path)
    assert new_surface.creation_datetime > original_creation_datetime
    assert datetime.datetime.now() > new_surface.creation_datetime
    assert (datetime.datetime.now() - new_surface.creation_datetime) \
        < datetime.timedelta(seconds=20)


def test_write_read_triangular_same(tmpdir):
    expected_surface = Surface()
    expected_surface.creator = b'pytest'
    expected_surface.creation_datetime = datetime.datetime.now().replace(microsecond=0)
    expected_surface.vertices = [Vertex(0.0, 0.0, 0.0),
                                 Vertex(1.0, 2.0, 3.0),
                                 Vertex(2.0, 4.0, 6.0),
                                 Vertex(3.0, 5.0, 7.0)]
    expected_surface.triangles = [Triangle((0, 1, 2)),
                                  Triangle((0, 1, 3)),
                                  Triangle((3, 2, 1))]
    expected_surface.using_old_real_ras = False
    expected_surface.volume_geometry_info = tuple(b'?\n' for _ in range(8))
    expected_surface.command_lines = [b'?', b'!']
    output_path = tmpdir.join('surface').strpath
    expected_surface.write_triangular(output_path,
                                      creation_datetime=expected_surface.creation_datetime)
    resulted_surface = Surface.read_triangular(output_path)
    assert vars(expected_surface) == vars(resulted_surface)


def test_write_triangular_same_locale(tmpdir):
    surface = Surface()
    surface.creator = b'pytest'
    surface.volume_geometry_info = tuple(b'?' for _ in range(8))
    creation_datetime = datetime.datetime(2018, 12, 31, 21, 42)
    output_path = tmpdir.join('surface').strpath
    with setlocale('de_AT.utf8'):
        surface.write_triangular(output_path,
                                 creation_datetime=creation_datetime)
    resulted_surface = Surface.read_triangular(output_path)
    assert resulted_surface.creation_datetime == creation_datetime
    with open(output_path, 'rb') as output_file:
        assert output_file.read().split(b' on ')[1] \
            .startswith(b'Mon Dec 31 21:42:00 2018\n')


def test_load_annotation():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    assert not surface.annotation
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    assert isinstance(surface.annotation, Annotation)
    assert len(surface.annotation.vertex_label_index) == 155622
    assert surface.annotation.vertex_label_index[0] == 5


def test_add_vertex():
    surface = Surface()
    assert not surface.vertices
    assert surface.add_vertex(Vertex(1.0, 1.5, 2.0)) == 0
    assert len(surface.vertices) == 1
    assert surface.vertices[0].anterior == pytest.approx(1.5)
    assert surface.add_vertex(Vertex(-3.0, 0.0, 4.0)) == 1
    assert len(surface.vertices) == 2
    assert surface.vertices[1].right == pytest.approx(-3.0)


@pytest.mark.parametrize(('vertices_coords', 'expected_extra_vertex_coords'), [
    (((0, 0, 0), (2, 4, 0), (2, 4, 3)), (0, 0, 3)),
    (((1, 1, 0), (3, 5, 0), (3, 5, 3)), (1, 1, 3)),
    (((1, 1, 7), (3, 5, 7), (3, 5, 3)), (1, 1, 3)),
    (((1, 1, 1), (3, 5, 7), (3, 5, 9)), (1, 1, 3)),
    (((3, 5, 7), (1, 1, 1), (1, 1, 3)), (3, 5, 9)),
])
def test_add_rectangle(vertices_coords, expected_extra_vertex_coords):
    surface = Surface()
    for vertex_coords in vertices_coords:
        surface.add_vertex(Vertex(*(float(c) for c in vertex_coords)))
    surface.add_rectangle(range(3))
    assert tuple(surface.vertices[3]) \
        == pytest.approx(expected_extra_vertex_coords)
    assert len(surface.triangles) == 2
    assert surface.triangles[0].vertex_indices == (0, 1, 2)
    assert surface.triangles[1].vertex_indices == (2, 3, 0)


def test__find_label_border_segments():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    precentral_label, = filter(lambda l: l.name == 'precentral',
                               surface.annotation.labels.values())
    # pylint: disable=protected-access
    border_segments = set(
        surface._find_label_border_segments(precentral_label))
    assert len(border_segments) == 417
    assert _LineSegment((33450, 32065)) in border_segments
    assert _LineSegment((33454, 33450)) in border_segments
    for border_vertex_index in [33450, 33454, 32065]:
        assert surface.annotation.vertex_label_index[border_vertex_index] == precentral_label.index
        for other_vertex_index in [32064, 33449, 33455, 33449, 33455]:
            assert _LineSegment((other_vertex_index, border_vertex_index)) \
                not in border_segments
            assert _LineSegment((border_vertex_index, other_vertex_index)) \
                not in border_segments


def test_find_label_border_polygonal_chains():
    surface = Surface.read_triangular(SURFACE_FILE_PATH)
    surface.load_annotation_file(ANNOTATION_FILE_PATH)
    precentral_label, = filter(lambda l: l.name == 'precentral',
                               surface.annotation.labels.values())
    border_chain, = surface.find_label_border_polygonal_chains(precentral_label)
    vertex_indices = list(border_chain.vertex_indices)
    assert len(vertex_indices) == 418
    min_index = vertex_indices.index(min(vertex_indices))
    vertex_indices_normalized = vertex_indices[min_index:] + vertex_indices[:min_index]
    assert vertex_indices_normalized[:4] == [32065, 32072, 32073, 32080]
    assert vertex_indices_normalized[-4:] == [36281, 34870, 33454, 33450]
